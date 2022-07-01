# !/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# from https://github.com/kerikun11/micromouse-maze-data
# Original author: Ryotaro Onuki (kerikun11+github@gmail.com)
# Modified Jul 2022: Peter Harrison
# description: a maze module includes Maze class
# usage: $ python maze.py mazefile.maze
# python version >= 3.8
# ============================================================================ #


import sys
import numpy as np

MAZE_SIZE = 16

NORTH_BIT = 1
EAST_BIT = 2
SOUTH_BIT = 4
WEST_BIT = 8
VISITED_BIT = 16


class Maze:
    """
    a maze class includes wall data, start indexes, goal indexes
    """
    # constants
    East, North, West, South, Unknown = range(5)

    def __init__(self, size=32):
        """
        construct a maze object with a maze size

        Returns
        -------
        None
        """
        self.size = size  # number of cells on one side of the maze
        # the number of cells in the maze: x * y
        self.cell_index_size = size * size
        # the number of walls to save: x * y * z
        self.wall_index_size = size * size * 2
        # wall data; wall states and known flags
        self.walls = np.zeros(self.wall_index_size, dtype=bool)
        self.knowns = np.zeros(self.wall_index_size, dtype=bool)
        # start and goal cells
        self.start = []
        self.goals = []

    @classmethod
    def uniquify(cls, x, y, d):
        """
        returns a unique coordinates of a wall without redundancy on both sides of the wall

        :returns: int x, int y, int z, int d
        """
        if d == cls.East:
            x, y, z, d = x, y, 0, cls.East
        elif d == cls.North:
            x, y, z, d = x, y, 1, cls.North
        elif d == cls.West:
            x, y, z, d = x - 1, y, 0, cls.East
        elif d == cls.South:
            x, y, z, d = x, y - 1, 1, cls.North
        return x, y, z, d

    def get_wall_index(self, x, y, z):
        """
        get a unique and sequential index of a wall inside the maze

        :returns: int index
        """
        if self.is_outside_maze(x, y):
            raise ValueError("out of field!")
        return x + y * self.size + z * self.size * self.size

    def get_cell_index(self, x, y):
        """
        get a unique and sequential index of a cell inside the maze

        Returns
        -------
        int index
        """
        if self.is_outside_maze(x, y):
            raise ValueError("out of field!")
        return y * self.size + x

    def is_outside_maze(self, x, y):
        """
        check that a cell location is valid
        :param x: cell x
        :param y: cell y
        :return: boolean
        """
        return x < 0 or y < 0 or x >= self.size or y >= self.size

    def wall(self, x, y, d, new_state=None, new_known=None):
        """
        get or update a wall flag, and optionally update a known flag

        Returns
        -------
        bool flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        # If it is out of the field, the wall is assumed to exist.
        if self.is_outside_maze(x, y):
            return True
        i = self.get_wall_index(x, y, z)
        if new_state is not None:
            self.walls[i] = new_state
        if new_known is not None:
            self.knowns[i] = new_known
        return self.walls[i]

    def set_wall(self, x, y, direction):
        """
        add a wall and set it to be known
        """
        self.wall(x, y, direction, True, True)

    def clear_wall(self, x, y, direction):
        """
        Remove a wall and set it to be known
        Should only be used when editing the maze
        """
        self.wall(x, y, direction, False, True)

    def toggle_wall(self, x, y, direction):
        if self.is_outside_maze(x, y):
            return
        if self.is_wall(x, y, direction):
            self.clear_wall(x, y, direction)
        else:
            self.set_wall(x, y, direction)

    def get_wall(self, x, y, direction):
        return self.is_wall(x, y, direction)

    def get_walls(self, x, y):
        """ get all the walls around a cell """
        wall_data = 0
        if self.is_wall(x, y, self.North):
            wall_data += NORTH_BIT
        if self.is_wall(x, y, self.East):
            wall_data += EAST_BIT
        if self.is_wall(x, y, self.South):
            wall_data += SOUTH_BIT
        if self.is_wall(x, y, self.West):
            wall_data += WEST_BIT
        return wall_data

    def _known(self, x, y, d, new_known=None):
        """
        get or update a known flag of a wall

        Returns
        -------
        bool flag
        """
        x, y, z, d = self.uniquify(x, y, d)
        # If it is out of the field, the wall is assumed to be known.
        if self.is_outside_maze(x, y):
            return True
        i = self.get_wall_index(x, y, z)
        if new_known != None:
            self.knowns[i] = new_known
        return self.knowns[i]

    def is_wall(self, x, y, direction):
        return self.wall(x, y, direction)

    def is_known_wall(self, x, y, direction):
        return self._known(x, y, direction)

    def is_goal_cell(self, x, y):
        return [x, y] in self.goals

    def is_home_cell(self, x, y):
        return [x, y] in self.start

    def __str__(self):
        """
        show information of the maze

        :returns: string
        """
        return f'size: {self.size}x{self.size}' + '\n' + \
               'start: ' + ', '.join([f'({x}, {y})' for x, y in self.start]) + '\n' + \
               'goals: ' + ', '.join([f'({x}, {y})' for x, y in self.goals])

    @staticmethod
    def parse_maze_file(file):
        """
        parse a maze string from file and construct a maze object
        sets the walls and looks for the start and goal cells
        assumes a fixed format of four characters per cell
        does not check the format
        does not report or handle errors
        sample tiny maze
        +---+---+---+---+
        |       |       |
        +   +   +   +   +
        |   |   |   |   |
        +   +   +   +   +
        |   |       |   |
        +   +---+---+   +
        | S | G         |
        +---+---+---+---+

        :returns: Maze object
        """
        lines = file.readlines()
        the_maze = Maze.parse_maze_lines(lines)
        return the_maze

    @staticmethod
    def parse_maze_lines(lines):
        maze_size = max(len(lines) // 2, len(lines[0]) // 4)
        the_maze = Maze(maze_size)  # construct a maze object
        # the text is upside down so that the first line is the south edge
        for i, line in enumerate(reversed(lines)):
            line = line.rstrip()  # remove \n
            cell_y = i // 2
            if i % 2 == 0:  # +---+---+---+---+
                for cell_x, c in enumerate(line[2::4]):
                    if c == '-':
                        the_maze.set_wall(cell_x, cell_y, Maze.South)
                    elif c == ' ':
                        the_maze.clear_wall(cell_x, cell_y, Maze.South)
            else:  # |   |   | G |   |
                for cell_x, c in enumerate(line[0::4]):
                    if c == '|':
                        the_maze.set_wall(cell_x, cell_y, Maze.West)
                    elif c == ' ':
                        the_maze.clear_wall(cell_x, cell_y, Maze.West)
                for cell_x, c in enumerate(line[2::4]):
                    if c == 'S':
                        the_maze.start.append([cell_x, cell_y])
                    if c == 'G':
                        the_maze.goals.append([cell_x, cell_y])
        return the_maze

    def get_maze_string(self):
        """
        generate a maze string to be saved in text format

        Returns
        -------
        string
        """
        post_char = 'o'
        res = ''  # result string
        for y in reversed(range(-1, self.size)):
            # +---+---+---+---+
            res += post_char  # first post
            for x in range(self.size):
                # horizontal wall
                if not self.is_known_wall(x, y, Maze.North):
                    res += ' . '
                elif self.is_wall(x, y, Maze.North):
                    res += '---'
                else:
                    res += '   '
                res += post_char
            res += '\n'
            # |   |   | G |   |
            if y == -1:
                break
            res += '|'  # first wall
            for x in range(self.size):
                # cell space
                if [x, y] in self.start:
                    res += ' S '
                elif [x, y] in self.goals:
                    res += ' G '
                else:
                    res += '   '
                # vertical wall
                if not self.is_known_wall(x, y, Maze.East):
                    res += '.'
                elif self.is_wall(x, y, Maze.East):
                    res += '|'
                else:
                    res += ' '
            res += '\n'
        return res


# ============================================================================ #
empty_classic_maze = [
    "o---o---o---o---o---o---o---o---o---o---o---o---o---o---o---o---o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                             G   G                             |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                             G   G                             |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "|                                                               |",
    "o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o   o",
    "| S |                                                           |",
    "o---o---o---o---o---o---o---o---o---o---o---o---o---o---o---o---o",
]

empty_half_size = [
    "+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                             G   G                                                                                             |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                             G   G                                                                                             |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "|                                                                                                                               |",
    "+   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +   +",
    "| S |                                                                                                                           |",
    "+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+---+",
]
# ============================================================================ #
# example
if __name__ == "__main__":
    # check arguments
    if len(sys.argv) < 2:
        print('please specify a maze file.')
        sys.exit(1)

    # set filepath
    filepath = sys.argv[1]

    # read maze file
    with open(filepath, 'r') as file:
        maze = Maze.parse_maze_file(file)

    # show info
    print(maze)
    print(maze.get_maze_string())

