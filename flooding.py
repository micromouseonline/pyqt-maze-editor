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

from maze import Maze

class Manhattan:
    """
    Simple costs based on the cell count to the goal
    """

    def __init__(self, maze):
        self.maze = None
        self.step_map = None

    def set_maze(self,maze):
        self.maze = maze
        self.step_map = [np.inf] * maze.cell_index_size

    def update(self, roots=None):
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

    def get_cost_at(self,x,y):
        cost = self.step_map[self.maze.get_cell_index(x, y)]
        return cost

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
