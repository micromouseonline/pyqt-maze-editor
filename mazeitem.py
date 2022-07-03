# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# Copyright (c) Peter Harrison 2022
# License: MIT
# description: A Maze Editor written using PyQt5
# python version >= 3.8
# ============================================================================ #
import math
import struct
from itertools import product

import numpy

# from PyQt5.QtCore import
import numpy as np
from PyQt5.QtGui import QBrush, QPen, QColor, QPicture, QFont, QPainter, QFontMetrics
from PyQt5.QtCore import QPointF
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
ORANGE = QColor(223, 108, 27)
WHITE = QColor(255, 255, 255)

WALL_COLOR = RED
POST_COLOR = YELLOW
NO_PEN = QtCore.Qt.PenStyle.NoPen


class Arrow():
    def __init__(self, start, end):
        self.start = start
        self.end = end

    @classmethod
    def draw(self, painter, src, dst, color=WHITE):
        """ draw an arrow between two points """
        painter.drawLine(src, dst)
        line = QtCore.QLineF(src, dst)
        angle = math.acos(line.dx() / line.length())
        if line.dy() >= 0:
            angle = 2 * math.pi - angle
        size = line.length() / 4
        p1 = dst + QPointF(math.sin(angle - math.pi / 3) * size, math.cos(angle - math.pi / 3) * size)
        p2 = dst + QPointF(math.sin(angle - math.pi + math.pi / 3) * size, math.cos(angle - math.pi + math.pi / 3) * size)
        painter.drawLine(dst, p1)
        painter.drawLine(dst, p2)
        return


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
        self.wall_width = max(4, 192 // self.maze_size)
        self.width = self.maze_size * self.cell_width + self.wall_width
        self.base_rect = QtCore.QRect(0, 0, self.width, self.width)
        self.notes = ''
        self.is_modified = False
        self.needs_flood = True
        self.flooder = None
        self.display_costs = False
        self.display_arrows = False
        self.display_paths = False

    def boundingRect(self):
        ''' all graphics items must implement this '''
        return QtCore.QRectF(self.base_rect.adjusted(-20, -20, 20, 80))

    def set_maze(self, maze):
        self.maze = maze
        self.maze_size = self.maze.size
        self.cell_width = 2880 // self.maze_size
        self.wall_width = max(4, 192 // self.maze_size)
        self.width = self.maze_size * self.cell_width + self.wall_width
        self.flooder = Manhattan(maze)
        self.is_modified = False
        self.needs_flood = True
        self.update()

    def show_arrows(self):
        self.display_arrows = True

    def hide_arrows(self):
        self.display_arrows = False

    def show_costs(self):
        self.display_costs = True

    def hide_costs(self):
        self.display_costs = False

    def show_paths(self):
        self.display_paths = True

    def hide_paths(self):
        self.display_paths = False

    def cell_origin(self, cell_x, cell_y) -> QtCore.QPointF:
        cx = cell_x * self.cell_width + self.wall_width / 2
        cy = self.width - (cell_y + 1) * self.cell_width - self.wall_width / 2
        return QtCore.QPointF(cx, cy)

    def cell_center(self, cell_x, cell_y) -> QtCore.QPointF:
        return self.cell_origin(cell_x, cell_y) + QtCore.QPointF(self.cell_width / 2, self.cell_width / 2)

    def cell_top_center(self, cell_x, cell_y) -> QtCore.QPointF:
        return self.cell_origin(cell_x, cell_y) + QtCore.QPointF(self.cell_width / 2, 0)

    def cell_left_center(self, cell_x, cell_y) -> QtCore.QPointF:
        return self.cell_origin(cell_x, cell_y) + QtCore.QPointF(0, self.cell_width / 2)

    def cell_right_center(self, cell_x, cell_y) -> QtCore.QPointF:
        return self.cell_origin(cell_x, cell_y) + QtCore.QPointF(self.cell_width, self.cell_width / 2)

    def cell_bottom_center(self, cell_x, cell_y) -> QtCore.QPointF:
        return self.cell_origin(cell_x, cell_y) + QtCore.QPointF(self.cell_width / 2, self.cell_width)

    def paint_path(self, painter):
        if self.flooder.path is None:
            return
        if not self.display_paths:
            return
        if self.flooder.get_cost_at(0, 0) == np.inf:
            return
        painter.save()
        painter.setPen(QPen(GREEN, self.wall_width / 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        p0 = self.cell_center(0, 0)
        p1 = self.cell_top_center(0, 0)
        p2 = p1
        painter.drawLine(p0, p1)
        for x, y in self.flooder.path[1:-1]:
            this_heading = self.flooder.get_heading(x, y)
            if this_heading == Maze.North:
                p2 = self.cell_top_center(x, y)
            elif this_heading == Maze.East:
                p2 = self.cell_right_center(x, y)
            elif this_heading == Maze.South:
                p2 = self.cell_bottom_center(x, y)
            elif this_heading == Maze.West:
                p2 = self.cell_left_center(x, y)
            painter.drawLine(p1, p2)
            p1 = p2
        x, y = self.flooder.path[-1]
        painter.drawLine(p1, self.cell_center(x, y))
        painter.restore()

    def paint_costs(self, painter):
        if self.display_costs == False:
            return
        if self.flooder.path is None:
            return

        font = QFont()
        font.setPixelSize(self.cell_width / 3)
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
            cost = self.flooder.get_cost_at(x, y)
            if [x, y] in self.flooder.path:
                painter.setPen(YELLOW)
            else:
                painter.setPen(ORANGE)
            if cost != np.inf:
                painter.drawText(inner_rect, QtCore.Qt.AlignCenter, F"{cost}")
        painter.restore()

    def paint_arrows(self, painter):
        if self.display_arrows == False:
            return
        painter.save()
        painter.setPen(QPen(YELLOW, self.wall_width / 2, QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        # painter.setBrush(BLACK)
        for (x, y) in product(range(self.maze_size), repeat=2):
            left_x = x * self.cell_width + self.wall_width / 2 + 1 * self.cell_width / 4
            mid_x = left_x + self.cell_width / 4
            right_x = left_x + self.cell_width / 2
            top_y = self.width - y * self.cell_width - self.cell_width - self.wall_width / 2 + self.cell_width / 4
            mid_y = top_y + self.cell_width / 4
            bottom_y = top_y + self.cell_width / 2
            n = QPointF(mid_x, top_y)
            e = QPointF(right_x, mid_y)
            s = QPointF(mid_x, bottom_y)
            w = QPointF(left_x, mid_y)
            i = self.maze.get_cell_index(x, y)
            if self.flooder.heading_map[i] == Maze.North:
                Arrow.draw(painter, s, n)
            elif self.flooder.heading_map[i] == Maze.East:
                Arrow.draw(painter, w, e)
            elif self.flooder.heading_map[i] == Maze.South:
                Arrow.draw(painter, n, s)
            elif self.flooder.heading_map[i] == Maze.West:
                Arrow.draw(painter, e, w)
            else:
                pass

        painter.restore()

    def paint_posts(self, painter):
        painter.save()
        painter.setBrush(WALL_COLOR)
        painter.setPen(QPen(BLACK))
        for (col, row) in product(range(self.maze_size + 1), repeat=2):
            x = self.cell_width * col
            y = self.cell_width * row
            painter.drawRect(x, y, self.wall_width, self.wall_width)
        painter.restore()

    def paint_cells(self, painter):
        painter.save()
        painter.setPen(NO_PEN)
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
        painter.restore()

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
        self.notes = F'Simple Manhattan flood gives cell count to goal of {self.flooder.get_cost_at(0, 0)}'
        font = QFont()
        font.setPixelSize(48)
        font_height = QFontMetrics(font).height()
        painter.setFont(font)
        painter.setPen(YELLOW)
        painter.drawText(self.wall_width, self.maze_size * self.cell_width + self.wall_width + font_height, str(self.notes))

    def paint(self, painter, *args):
        if self.needs_flood:
            self.flooder.set_maze(self.maze)
            self.flooder.update()
            self.needs_flood = False
        painter.setBrush(DARK_GRAY)
        painter.drawRect(self.base_rect)
        self.paint_cells(painter)
        self.paint_posts(painter)
        self.paint_walls(painter)
        self.paint_notes(painter)
        self.paint_costs(painter)
        self.paint_arrows(painter)
        self.paint_path(painter)

    def on_maze_click(self, pos, buttons, modifiers):
        # self.notes = ''
        x = int(pos.x())
        y = self.maze_size * self.cell_width - int(pos.y())
        cell_x = x // self.cell_width
        cell_y = y // self.cell_width
        if cell_x >= self.maze_size or cell_x < 0 or cell_y >= self.maze_size or cell_y < 0:
            return
        offset_x = x % self.cell_width
        offset_y = y % self.cell_width
        cell_id = cell_x * self.maze_size + cell_y
        # self.notes += F'Mouse: ({x},{y}) -> cell({cell_x},{cell_y})'
        # self.notes += F' offset:({offset_x},{offset_y})'
        self.is_modified = True
        self.needs_flood = True
        if modifiers == QtCore.Qt.ShiftModifier:
            goal = [cell_x, cell_y]
            if goal in self.maze.goals:
                self.maze.goals.remove(goal)
            else:
                self.maze.goals.append(goal)
        elif buttons == QtCore.Qt.RightButton:
            # self.notes += ' - change target cell'
            pass
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
