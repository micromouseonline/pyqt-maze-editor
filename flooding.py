#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ============================================================================ #
# author: Ryotaro Onuki (kerikun11+github@gmail.com)
# modified: Peter Harrison, July 2022
# description: Creates cost maps for micromouse mazes
# usage: $ python maze_step_map.py mazefile.maze
# python version >= 3.8
# ============================================================================ #
import sys
import numpy as np
from itertools import product
from maze import Maze


class Manhattan:
    """
    Simple costs based on the cell count to the goal
    """

    def __init__(self, maze):
        self.maze = None
        self.step_map = None
        self.heading_map = None
        self.path = None

    def set_maze(self, maze):
        self.maze = maze
        self.step_map = [np.inf] * maze.cell_index_size
        self.heading_map = [Maze.Unknown] * maze.cell_index_size

    def update(self, roots=None):
        if self.maze is None:
            return
        self.update_costs(roots)
        # self.update_heading_map()
        self.update_path_map()

    def update_costs(self, roots=None):
        """
        calculate cost map of cells using breadth first search
        """
        # prepare
        maze = self.maze
        step_map = self.step_map
        roots = roots if roots else maze.goals
        # initialize
        for c in step_map:
            c = np.inf
        open_list = []
        for x, y in roots:
            step_map[maze.get_cell_index(x, y)] = 0
            open_list.append([x, y])
        # breadth first search
        while open_list:
            x, y = open_list.pop(0)
            i = maze.get_cell_index(x, y)
            cost_here = step_map[i]
            next_cost = cost_here + 1

            # update neighbors
            for nx, ny, nd in [
                [x, y + 1, Maze.North],
                [x + 1, y, Maze.East],
                [x, y - 1, Maze.South],
                [x - 1, y, Maze.West],
            ]:
                # see if the next cell can be visited
                if maze.wall(x, y, nd):
                    continue
                next_i = maze.get_cell_index(nx, ny)
                neighbour_cost = step_map[next_i]
                if neighbour_cost <= next_cost:
                    continue
                step_map[next_i] = next_cost
                open_list.append([nx, ny])
        self.step_map = step_map
        return step_map

    def get_cost_at(self, x, y):
        if self.maze.is_outside_maze(x, y):
            return np.inf
        cost = self.step_map[self.maze.get_cell_index(x, y)]
        return cost

    def get_neighbour_cost(self, x, y, heading):
        if self.maze.wall(x, y, heading):
            return np.inf
        if heading == Maze.North:
            return self.step_map[self.maze.get_cell_index(x, y + 1)]
        if heading == Maze.East:
            return self.step_map[self.maze.get_cell_index(x + 1, y)]
        if heading == Maze.South:
            return self.step_map[self.maze.get_cell_index(x, y - 1)]
        if heading == Maze.West:
            return self.step_map[self.maze.get_cell_index(x - 1, y)]

    def get_direction_to_smallest(self, x, y, start_heading=Maze.North):
        if self.maze.is_outside_maze(x, y):
            return Maze.Unknown
        best_heading = start_heading
        heading = start_heading
        i = self.maze.get_cell_index(x, y)
        lowest_cost = self.step_map[i]
        for j in range(0, 4):
            heading = (start_heading + j) % 4
            cost = self.get_neighbour_cost(x,y,heading)
            if cost < lowest_cost:
                lowest_cost = cost
                best_heading = heading
        return best_heading

    def update_heading_map(self):
        if self.maze is None:
            return
        heading_map = self.heading_map
        smallest_cost = np.inf
        for (x, y) in product(range(self.maze.size), repeat=2):
            i = self.maze.get_cell_index(x, y)
            heading_now = self.heading_map[i]
            heading_map[i] = self.get_direction_to_smallest(x,y,heading_now)
        self.heading_map = heading_map
        return heading_map

    def get_heading(self,x,y):
        i = self.maze.get_cell_index(x, y)
        return self.heading_map[i]

    def update_path_map(self):
        if self.maze is None:
            return
        self.heading_map = [Maze.Unknown] * self.maze.cell_index_size
        if self.step_map[0] == np.inf:
            self.heading_map[0] = Maze.South
            return
        self.heading_map[0] = Maze.North
        last_heading = Maze.North
        x,y = self.maze.get_cell_xy(0)
        path = [[x,y]]
        while not [x,y] in self.maze.goals:
            i = self.maze.get_cell_index(x,y)
            heading_now = last_heading
            direction = self.get_direction_to_smallest(x,y,heading_now)
            self.heading_map[i] = direction
            last_heading = direction
            if direction == Maze.North:
                y = y + 1
            elif direction == Maze.East:
                x = x + 1
            elif direction == Maze.South:
                y = y - 1
            elif direction == Maze.West:
                x = x - 1
            path.append([x,y])
        self.path = path
        return path


    def __str__(self):
        maze = self.maze
        res = ''
        for y in reversed(range(maze.size)):
            for x in range(maze.size):
                c = self.step_map[maze.get_cell_index(x, y)]
                res += f'{c:>4}'
            res += '\n'
        return res

    def __getitem__(self, key):
        return self.step_map[key]


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
        maze = Maze.parse_maze_string(file)

    # show info
    print(maze)
    print(maze.get_maze_string())

    # show cost map
    step_map = Manhattan(maze)
    step_map.update()
    print(step_map)
