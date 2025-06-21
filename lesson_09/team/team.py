""" 
Course: CSE 351
Team  : 
File  : Week 9 team.py
Author:  Luc Comeau
"""

# Include CSE 351 common Python files. 
from cse351 import *
import time
import random
import multiprocessing as mp

# number of cleaning staff and hotel guests
CLEANING_STAFF = 2
HOTEL_GUESTS = 5

# Run program for this number of seconds
TIME = 60

STARTING_PARTY_MESSAGE =  'Turning on the lights for the party vvvvvvvvvvvvvv'
STOPPING_PARTY_MESSAGE  = 'Turning off the lights  ^^^^^^^^^^^^^^^^^^^^^^^^^^'

STARTING_CLEANING_MESSAGE =  'Starting to clean the room >>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
STOPPING_CLEANING_MESSAGE  = 'Finish cleaning the room <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'

def cleaner_waiting():
    time.sleep(random.uniform(0, 2))

def cleaner_cleaning(id):
    print(f'Cleaner: {id}')
    time.sleep(random.uniform(0, 2))

def guest_waiting():
    time.sleep(random.uniform(0, 2))

def guest_partying(id, count):
    print(f'Guest: {id}, count = {count}')
    time.sleep(random.uniform(0, 1))

def cleaner(id,clean_room_lock, cleaned_count, start_time):
    """
    do the following for TIME seconds
        cleaner will wait to try to clean the room (cleaner_waiting())
        get access to the room
        display message STARTING_CLEANING_MESSAGE
        Take some time cleaning (cleaner_cleaning())
        display message STOPPING_CLEANING_MESSAGE
    """
    while time.time()-start_time < TIME:
        cleaner_waiting()
        clean_room_lock.acquire()
        cleaned_count.value += 1
        print(STARTING_CLEANING_MESSAGE)
        cleaner_cleaning(id)
        print(STOPPING_CLEANING_MESSAGE)
        clean_room_lock.release()

def guest(id,guest_count_lock, clean_room_lock, party_count, start_time, room_count):
    """
    do the following for TIME seconds
        guest will wait to try to get access to the room (guest_waiting())
        get access to the room
        display message STARTING_PARTY_MESSAGE if this guest is the first one in the room
        Take some time partying (call guest_partying())
        display message STOPPING_PARTY_MESSAGE if the guest is the last one leaving in the room
    """
    while time.time()-start_time < TIME:
        guest_waiting()
        num_in_room = 0
        with guest_count_lock:
            room_count.value += 1
            num_in_room = room_count.value
            if room_count.value == 1:
                #first guest
                clean_room_lock.acquire()
                print(STARTING_PARTY_MESSAGE)
                party_count.value += 1

        guest_partying(id, room_count.value)

        with guest_count_lock:
            room_count.value -= 1
            if room_count.value == 0:
                print(STOPPING_PARTY_MESSAGE)
                clean_room_lock.release()

def main():
    # Start time of the running of the program.
    start_time = time.time()

    cleaned_count =  mp.Value('i',0)
    party_count = mp.Value('i',0)
    room_count = mp.Value('i',0)

    # TODO - add any variables, data structures, processes you need
    light_lock = mp.Lock()
    room_lock = mp.Lock()

    guest_count_lock = mp.Lock()
    clean_room_lock = mp.Lock()


    cleaners = []
    guests = []
    for i in range(CLEANING_STAFF):
        worker = mp.Process(target= cleaner, args=(i+1,clean_room_lock, cleaned_count, start_time))
        cleaners.append(worker)
    
    for i in range(HOTEL_GUESTS):
        worker = mp.Process(target= guest, args=(i+1,guest_count_lock, clean_room_lock, party_count, start_time,room_count))
        guests.append(worker)

    for p in cleaners + guests:
        p.start()
    
    for p in guests + cleaners:
        p.join()


    # TODO - add any arguments to cleaner() and guest() that you need

    # Results
    print(f'Room was cleaned {cleaned_count.value} times, there were {party_count.value} parties')


if __name__ == '__main__':
    main()