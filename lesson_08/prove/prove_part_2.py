"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: <Add name here>

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

Each thread will maintain its own list called path_so_far, which contains the positions it has visited as tuples. 
When a new thread is created, it receives a copy of the current path with the new position added, so that each 
thread works with its own independent path. I will also create a shared variable, final_path, to hold the first 
successful path that reaches the end. To protect this variable from race conditions, I will use a path_lock. When 
a thread finds the end, it will acquire the lock, set final_path to its current path, and then set the global stop 
flag to True to signal other threads to terminate.

Why would it work?

This approach works because it isolates each thread’s exploration path, preventing interference or corruption between 
threads. Copying the path only when branching into new threads avoids unnecessary overhead while maintaining thread 
safety. The lock around final_path ensures that only the first successful path is recorded, and the stop flag efficiently 
signals other threads to terminate early.

"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# Add any function(s) you need, if any, here.

def solve_find_end(maze):
    """Finds the end position using threads. Nothing is returned."""
    global stop,thread_count
    
    thread_lock = threading.Lock()
    move_lock = threading.Lock()
    
    stop = False
    threads = []    
    start_pos = maze.get_start_pos()

    dfs(start_pos, get_color(),maze, move_lock, thread_lock, threads)

    for t in threads:
        t.join()
    thread_count= len(threads)

def dfs(position, color, maze,move_lock, thread_lock, threads):
    global stop
    if stop:
        return

    curr_row, curr_col = position
    if maze.can_move_here(curr_row, curr_col):
        maze.move(curr_row, curr_col, color)
    else:
        return

    if maze.at_end(curr_row, curr_col):
        stop = True
        return

    open_moves = maze.get_possible_moves(curr_row, curr_col)

    for move in open_moves:   
        if stop:
            return
        if maze.can_move_here(move[0], move[1]):
            if move == open_moves[len(open_moves)-1]:
                dfs(move,color,maze,move_lock, thread_lock, threads)
                continue
            with move_lock:
                branch_color = get_color()
                t = threading.Thread(target = dfs, args = (move, branch_color,maze,move_lock, thread_lock, threads))
                t.start()
            with thread_lock:
                threads.append(t)
            
    
def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

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


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()