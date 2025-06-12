"""
Course: CSE 251 
Assignment: 08 Prove Part 1
File:   prove_part_1.py
Author: <Add name here>

Purpose: Part 1 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:

- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- Complete any TODO comments.
"""

import math
from screen import Screen
from maze import Maze
import cv2
import sys

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
SLOW_SPEED = 100
FAST_SPEED = 1
speed = SLOW_SPEED

# TODO: Add any functions needed here.

def solve_path(maze):
    """ Solve the maze and return the path found between the start and end positions.  
        The path is a list of positions, (x, y) """
    path = []

    def dfs(position):
        path.append(position) # add position
        curr_row, curr_col = position # define row and col values from position
        if maze.at_end(curr_row, curr_col): # check if maze is at end before checking moves
            return True
        open_moves = maze.get_possible_moves(curr_row, curr_col) # returns a list of possible moves
        for move in open_moves:
            if maze.can_move_here(move[0], move[1]): # making sure if move is valid
                maze.move(move[0], move[1], COLOR) # change to red on display
                if dfs(move): # RECURSION, for this move, add it to path, and iterate through its open_moves if not at end, will recurse until a true or false is returned in one of the rounds.
                    return True
                else:
                    path.pop() # in the case that it's false return adica no open moves (can't move there!), remove move from path
                    maze.restore(move[0], move[1]) # and change color to gray.
        return False  # ensures recursion always returns a boolean

    position = maze.get_start_pos()
    dfs(position)
    return path




    # Hint: You can create an inner function to do the recursion


def get_path(log, filename):
    """ Do not change this function """
    # 'Maze: Press "q" to quit, "1" slow drawing, "2" faster drawing, "p" to play again'
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))


    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    path = solve_path(maze)

    log.write(f'Drawing commands to solve = {screen.get_command_count()}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True

    return path


def find_paths(log):
    """ Do not change this function """

    files = (
        'very-small.bmp',
        'very-small-loops.bmp',
        'small.bmp',
        'small-loops.bmp',
        'small-odd.bmp',
        'small-open.bmp',
        'large.bmp',
        'large-loops.bmp',
        'large-squares.bmp',
        'large-open.bmp'
    )

    log.write('*' * 40)
    log.write('Part 1')
    for filename in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        path = get_path(log, filename)
        log.write(f'Found path has length     = {len(path)}')
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_paths(log)


if __name__ == "__main__":
    main()