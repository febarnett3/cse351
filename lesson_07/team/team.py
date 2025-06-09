"""
Course: CSE 351 
Week: 07 Team
File:   team.py
Author: <Add name here>

Purpose: Solve the Dining philosophers problem to practice skills you have learned so far in this course.

Problem Statement:

Five silent philosophers sit at a round table with bowls of spaghetti. Forks
are placed between each pair of adjacent philosophers.

Each philosopher must alternately think and eat. However, a philosopher can
only eat spaghetti when they have both left and right forks. Each fork can be
held by only one philosopher and so a philosopher can use the fork only if it
is not being used by another philosopher. After an individual philosopher
finishes eating, they need to put down both forks so that the forks become
available to others. A philosopher can only take the fork on their right or
the one on their left as they become available and they cannot start eating
before getting both forks.  When a philosopher is finished eating, they think 
for a little while.

Eating is not limited by the remaining amounts of spaghetti or stomach space;
an infinite supply and an infinite demand are assumed.

The problem is how to design a discipline of behavior (a concurrent algorithm)
such that no philosopher will starve

Instructions:

        ****************************************************************
        ** DO NOT search for a solution on the Internet! Your goal is **
        ** not to copy a solution, but to work out this problem using **
        ** the skills you have learned so far in this course.         **
        ****************************************************************

Requirements you must Implement:

- Use threads for this problem.
- Start with the PHILOSOPHERS being set to 5.
- Philosophers need to eat for a random amount of time, between 1 to 3 seconds, when they get both forks.
- Philosophers need to think for a random amount of time, between 1 to 3 seconds, when they are finished eating.
- You want as many philosophers to eat and think concurrently as possible without violating any rules.
- When the number of philosophers has eaten a combined total of MAX_MEALS_EATEN times, stop the
  philosophers from trying to eat; any philosophers already eating will put down their forks when they finish eating.
    - MAX_MEALS_EATEN = PHILOSOPHERS x 5

Suggestions and team Discussion:

- You have Locks and Semaphores that you can use:
    - Remember that lock.acquire() has arguments that may be useful: `blocking` and `timeout`.  
- Design your program to handle N philosophers and N forks after you get it working for 5.
- When you get your program working, how to you prove that no philosopher will starve?
  (Just looking at output from print() statements is not enough!)
- Are the philosophers each eating and thinking the same amount?
    - Modify your code to track how much eat philosopher is eating.
- Using lists for the philosophers and forks will help you in this program. For example:
  philosophers[i] needs forks[i] and forks[(i+1) % PHILOSOPHERS] to eat (the % operator helps).
"""

import time
import random
import threading

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5 # NOTE: Total meals to be eaten, not per philosopher!

import threading
import time
import random

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5


class Philosopher(threading.Thread):
    def __init__(self, id, left_fork, right_fork, meals_counter, meals_lock):
        super().__init__()
        self.id = id
        self.left_fork = left_fork
        self.right_fork = right_fork
        self.meals_counter = meals_counter
        self.meals_lock = meals_lock
        self.my_meals = 0

    def think(self):
        print(f"Philosopher {self.id} is thinking.")
        time.sleep(random.uniform(1, 3))

    def eat(self):
        print(f"Philosopher {self.id} is eating.")
        time.sleep(random.uniform(1, 3))

    def try_to_eat(self):
        # Avoid deadlock: let one philosopher pick up right fork first
        if self.id == 0:
            forks = [self.right_fork, self.left_fork]
        else:
            forks = [self.left_fork, self.right_fork]

        acquired_first = forks[0].acquire(timeout=1)
        if not acquired_first:
            return True  # Try again later

        acquired_second = forks[1].acquire(timeout=1)
        if not acquired_second:
            forks[0].release()
            return True  # Try again later

        # Safely acquired both forks
        with self.meals_lock:
            if self.meals_counter[0] >= MAX_MEALS_EATEN:
                forks[1].release()
                forks[0].release()
                return False  # Time to stop

            self.meals_counter[0] += 1
            self.my_meals += 1
            print(f"Philosopher {self.id} is starting meal #{self.my_meals}. Total meals: {self.meals_counter[0]}")

        self.eat()

        forks[1].release()
        forks[0].release()

        return True

    def run(self):
        while True:
            self.think()
            should_continue = self.try_to_eat()
            if not should_continue:
                break
        print(f"Philosopher {self.id} is done after eating {self.my_meals} times.")


def main():
    forks = [threading.Lock() for _ in range(PHILOSOPHERS)]
    meals_counter = [0]  # shared mutable object
    meals_lock = threading.Lock()

    philosophers = []
    for i in range(PHILOSOPHERS):
        left = forks[i]
        right = forks[(i + 1) % PHILOSOPHERS]
        philosopher = Philosopher(i, left, right, meals_counter, meals_lock)
        philosophers.append(philosopher)

    for p in philosophers:
        p.start()
    for p in philosophers:
        p.join()

    print("\nFinal Report:")
    for p in philosophers:
        print(f"Philosopher {p.id} ate {p.my_meals} times.")


if __name__ == "__main__":
    main()
