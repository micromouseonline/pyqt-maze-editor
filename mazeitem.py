# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# Copyright (c) Peter Harrison 2022
# License: MIT
# description: A Maze Editor written using PyQt5
# python version >= 3.8
# ============================================================================ #


import struct
from itertools import product

import numpy

# from PyQt5.QtCore import
import numpy as np
from PyQt5.QtGui import QBrush, QPen, QColor, QPicture, QFont, QPainter, QFontMetrics
from PyQt5.QtWidgets import QGraphicsItem
# from PyQt5 import QtGui
from PyQt5 import QtCore

from maze import EAST_BIT
from maze import MAZE_SIZE
from maze import NORTH_BIT
from maze import SOUTH_BIT
from maze import VISITED_BIT
from maze import WEST_BIT
from maze import Maze
from flooding import Manhattan

BLACK = QColor(0, 0, 0)
DARK_GRAY = QColor(30, 10, 10)
GOAL_COLOR = QColor('#002a00')
HOME_COLOR = QColor('#100010')
GRAY = QColor(100, 100, 100)
GREEN = QColor(0, 255, 0)
RED = QColor(255, 0, 0)
YELLOW = QColor(QtCore.Qt.yellow)
WHITE = QColor(255, 255, 255)

WALL_COLOR = RED
POST_COLOR = YELLOW
NO_PEN = QtCore.Qt.PenStyle.NoPen


class MazeItem(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.distances = None
        self.maze = None
        self.x = 0
        self.y = 0
        # set some basic default values
        self.maze_size = 16
        self.cell_width = 2880 // self.maze_size
        self.wall_width = max(4,192 // self.maze_size)
        self.width = self.maze_size * self.cell_width + self.wall_width
        self.base_rect = QtCore.QRect(0, 0, self.width, self.width)
        self.notes = ''
        self.is_modified = False
        self.needs_flood = True
        self.flooder = None
        self.display_costs = False

    def boundingRect(self):
        ''' all graphics items must implement this '''
        return QtCore.QRectF(self.base_rect.adjusted(-20, -20, 20, 80))

    def set_maze(self, maze):
        self.maze = maze
        self.maze_size = self.maze.size
        self.cell_width = 2880 // self.maze_size
        self.wall_width = max(4,192 // self.maze_size)
        self.width = self.maze_size * self.cell_width + self.wall_width
        self.flooder = Manhattan(maze)
        self.is_modified = False
        self.needs_flood = True
        self.update()

    def show_costs(self):
        self.display_costs = True

    def hide_costs(self):
        self.display_costs = False

    def paint_costs(self,painter):
        if self.display_costs == False:
            return
        if self.needs_flood:
            self.flooder.set_maze(self.maze)
            self.flooder.update()
            self.needs_flood = False

        font = QFont()
        font.setPixelSize(self.cell_width/3)
        font_height = QFontMetrics(font).height()
        painter.save()
        painter.setFont(font)
        painter.setPen(YELLOW)
        painter.setBrush(BLACK)
        for (x, y) in product(range(self.maze_size), repeat=2):
            left = x * self.cell_width
            top = self.width - y * self.cell_width - self.cell_width - self.wall_width
            inner_rect = QtCore.QRect(left, top, self.cell_width, self.cell_width)
            inner_rect.adjust(self.wall_width, self.wall_width, 0, 0)
            cost = self.flooder.get_cost_at(x,y)
            if cost != np.inf:
                painter.drawText(inner_rect,QtCore.Qt.AlignCenter,F"{cost}")
        painter.restore()

    def paint_posts(self, painter):
        painter.setBrush(WALL_COLOR)
        painter.setPen(QPen(BLACK))
        for (col, row) in product(range(self.maze_size + 1), repeat=2):
            x = self.cell_width * col
            y = self.cell_width * row
            painter.drawRect(x, y, self.wall_width, self.wall_width)

    def paint_cells(self, painter):
        for (x, y) in product(range(self.maze_size), repeat=2):
            left = x * self.cell_width
            top = self.width - y * self.cell_width - self.cell_width - self.wall_width
            inner_rect = QtCore.QRect(left, top, self.cell_width, self.cell_width)
            inner_rect.adjust(self.wall_width, self.wall_width, 0, 0)
            if self.maze.is_goal_cell(x, y):
                painter.setBrush(GOAL_COLOR)
            elif self.maze.is_home_cell(x, y):
                painter.setBrush(HOME_COLOR)
            else:
                painter.setBrush(BLACK)
            painter.drawRect(inner_rect)

    def paint_walls(self, painter):
        if self.maze is None:
            return
        painter.setBrush(QBrush(RED))
        painter.setPen(QPen(NO_PEN))
        for (x, y) in product(range(self.maze_size), repeat=2):
            left = x * self.cell_width
            top = self.width - y * self.cell_width - self.cell_width - self.wall_width
            inner_rect = QtCore.QRect(left, top, self.cell_width, self.cell_width)
            inner_rect.adjust(self.wall_width, self.wall_width, 0, 0)
            painter.setBrush(WALL_COLOR)
            painter.setPen(QPen(BLACK))
            walls_here = self.maze.get_walls(x, y)
            if walls_here & EAST_BIT:
                wall_left = left + self.cell_width
                wall_top = top + self.wall_width
                wall_width = self.wall_width
                wall_height = self.cell_width - self.wall_width
                wall_rect = QtCore.QRectF(wall_left, wall_top, wall_width, wall_height)
                painter.drawRect(wall_rect)
            if walls_here & WEST_BIT:
                wall_left = left
                wall_top = top + self.wall_width
                wall_width = self.wall_width
                wall_height = self.cell_width - self.wall_width
                wall_rect = QtCore.QRectF(wall_left, wall_top, wall_width, wall_height)
                painter.drawRect(wall_rect)
            if walls_here & SOUTH_BIT:
                wall_left = left + self.wall_width
                wall_top = top + self.cell_width
                wall_width = self.cell_width - self.wall_width
                wall_height = self.wall_width
                wall_rect = QtCore.QRectF(wall_left, wall_top, wall_width, wall_height)
                painter.drawRect(wall_rect)
            if walls_here & NORTH_BIT:
                wall_left = left + self.wall_width
                wall_top = top
                wall_width = self.cell_width - self.wall_width
                wall_height = self.wall_width
                wall_rect = QtCore.QRectF(wall_left, wall_top, wall_width, wall_height)
                painter.drawRect(wall_rect)

    def paint_notes(self, painter):
        ''' This will be where we display route metrics from a list of strings'''
        font = QFont()
        font.setPixelSize(64)
        font_height = QFontMetrics(font).height()
        painter.setFont(font)
        painter.setPen(YELLOW)
        painter.drawText(540, 2890 + font_height, str(self.notes))

    def paint(self, painter, *args):
        painter.setBrush(DARK_GRAY)
        painter.drawRect(self.base_rect)
        self.paint_cells(painter)
        self.paint_posts(painter)
        self.paint_walls(painter)
        self.paint_notes(painter)
        self.paint_costs(painter)

    def on_maze_click(self, pos, buttons, modifiers):
        self.notes = ''
        x = int(pos.x())
        y = self.maze_size * self.cell_width - int(pos.y())
        cell_x = x // self.cell_width
        cell_y = y // self.cell_width
        if cell_x >= self.maze_size or cell_x < 0 or cell_y >= self.maze_size or cell_y < 0:
            return
        offset_x = x % self.cell_width
        offset_y = y % self.cell_width
        cell_id = cell_x * self.maze_size + cell_y
        self.notes += F'Mouse: ({x},{y}) -> cell({cell_x},{cell_y})'
        self.notes += F' offset:({offset_x},{offset_y})'
        self.is_modified = True
        self.needs_flood = True
        if modifiers == QtCore.Qt.ShiftModifier:
            goal = [cell_x,cell_y]
            if goal in self.maze.goals:
                self.maze.goals.remove(goal)
            else:
                self.maze.goals.append(goal)
        elif buttons == QtCore.Qt.RightButton:
            self.notes += ' - change target cell'
        else:
            if offset_y > offset_x:
                if offset_y > self.cell_width - offset_x:
                    if cell_y < self.maze_size - 1:
                        self.maze.toggle_wall(cell_x, cell_y, Maze.North)
                else:
                    if cell_x > 0:
                        self.maze.toggle_wall(cell_x, cell_y, Maze.West)
            else:
                if offset_y > self.cell_width - offset_x:
                    if cell_x < self.maze_size - 1:
                        self.maze.toggle_wall(cell_x, cell_y, Maze.East)
                else:
                    if cell_y > 0:
                        self.maze.toggle_wall(cell_x, cell_y, Maze.South)

        self.update()
