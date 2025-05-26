""" 
Course: CSE 351
Lesson: L05 Team Activity
File:   team.py
Author: Fiona Barnett
Purpose: Find prime numbers

Instructions:

- Don't include any other Python packages or modules
- Review and follow the team activity instructions (team.md)
"""

from datetime import datetime, timedelta
import random
from matplotlib.pylab import plt  # load plot library

# Include cse 351 common Python files
from cse351 import *

import multiprocessing as mp

def is_prime(n):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i ** 2 <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def process_numbers(x):
    print(x, end=', ', flush=True)
    print(flush=True)
    if is_prime(x):
        return x
    else:
        return None

def main():
    log = Log(show_terminal=True)
    log.start_timer()

    #shared_int = mp.Value('prime_count', 0) 
    #shared_int = mp.Value('numbers_processed', 0) 

    xaxis_cpus = []
    yaxis_times = []

    start_time = time.time()

    start = 10000000000
    range_count = 100000

    processed_numbers = 0
    prime_count = 0

    for cpu in range(1,mp.cpu_count()+1):
        with mp.Pool(cpu) as p:
            print(f"Cores: {cpu}")
            start_time = time.time()
            results = p.map(process_numbers, range(start,start+range_count))
            end_time = time.time()

            # for item in results:
            #     if item is True:
            #             processed_numbers += 1
            #             prime_count+=1
            #     else:
            #         processed_numbers+=1
        elapsed_time = end_time - start_time

        xaxis_cpus.append(cpu)
        yaxis_times.append(elapsed_time)

    # print(processed_numbers)
    # print(prime_count)
    # print(elapsed_time)
    # print(num_cpus)


    # create plot of results and also save it to a PNG file
    plt.plot(xaxis_cpus, yaxis_times)
    
    plt.title('Time VS CPUs')
    plt.xlabel('CPU Cores')
    plt.ylabel('Seconds')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    main()