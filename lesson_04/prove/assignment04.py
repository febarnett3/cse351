"""
Course    : CSE 351
Assignment: 04
Student   : Fiona Barnett

4. Meets requirements: is under 60s, uses 2 queues (max size 10), used threaded worker class, used threaded function

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *
import queue

THREADS = 100                 # TODO - set for your program
WORKERS = 10
RECORDS_TO_RETRIEVE = 5000  # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(q1, q2, q1_empty_slots, q1_full_slots, q2_empty_slots, q2_full_slots):
    while True:
        q1_full_slots.acquire()  # Wait for a full slot (something to consume)
        command = q1.get()       # Get the item from the queue
        q1_empty_slots.release() # Release an empty slot in the queue

        if command is None:  # Termination signal
            break

        name, recno = command
       
        data = get_data_from_server(f'{TOP_API_URL}/record/{name}/{recno}')
        
        q2_empty_slots.acquire()
        q2.put(data)
        q2_full_slots.release()



# ---------------------------------------------------------------------------
# TODO - Create Worker threaded class
class Worker(threading.Thread):
    def __init__(self, q2, noaa, q2_empty_slots, q2_full_slots):
        super().__init__()
        self.q2 = q2
        self.noaa = noaa
        self.q2_empty_slots = q2_empty_slots
        self.q2_full_slots = q2_full_slots

    def run(self):
        while True:
            self.q2_full_slots.acquire()
            data = self.q2.get()
            self.q2_empty_slots.release()
            
            if data is None:
                break
            
            # assign values in triple tuple a variable
            city = data['city']
            date = data['date']
            temp = data['temp']

            # store variables in noaa
            
            self.noaa.store_data(city,date,temp)
            

        
        

# ---------------------------------------------------------------------------
# TODO - Complete this class
class NOAA:

    def __init__(self):
        self.weather_dict = {}
        self.lock = threading.Lock()

    def store_data(self, city, date, temp):
        with self.lock:
            if city not in self.weather_dict:
                self.weather_dict[city] = []
            self.weather_dict[city].append((date, temp))

    def get_temp_details(self, city):
        if city not in self.weather_dict or len(self.weather_dict[city]) == 0:
            return None

        total = sum(record[1] for record in self.weather_dict[city])
        return total / len(self.weather_dict[city])  # Average temperature


# ---------------------------------------------------------------------------
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')
# ---------------------------------------------------------------------------

def producer(CITIES, records, q1, q1_empty_slots, q1_full_slots):
    for city in CITIES:
        for i in range(records):
            q1_empty_slots.acquire()  # Wait for an empty slot in the queue
            q1.put((city, i))         # Put the city and record number into the queue
            q1_full_slots.release()   # Signal that the queue now has a full slot

# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]["records"]:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    q1_empty_slots = threading.Semaphore(10)
    q1_full_slots = threading.Semaphore(0)

    q2_empty_slots = threading.Semaphore(10)
    q2_full_slots = threading.Semaphore(0)

    q1 = queue.Queue()
    q2 = queue.Queue()

    threads = []
    workers = []

    barrier = threading.Barrier(THREADS+1)

    # Start worker threads for stage 2 (processing data from q2)
    for _ in range(WORKERS):
        w = Worker(q2, noaa, q2_empty_slots, q2_full_slots)
        w.start()
        workers.append(w)

    # Start consumer threads (stage 1, retrieving weather data and pushing to q2)
    for _ in range(THREADS):
        # REMOVE barrier2 from args, or set it to None if retrieve_weather_data expects it
        t = threading.Thread(target=retrieve_weather_data, args=(q1, q2, q1_empty_slots, q1_full_slots, q2_empty_slots, q2_full_slots)) # Pass None or remove argument
        t.start()
        threads.append(t)

    producer(CITIES, records, q1, q1_empty_slots, q1_full_slots)


    for _ in range(THREADS):
        q1_empty_slots.acquire()
        q1.put(None)
        q1_full_slots.release()

    for t in threads:
        t.join()

    for _ in range(WORKERS):
        q2_empty_slots.acquire()
        q2.put(None)
        q2_full_slots.release()

    for w in workers:
        w.join()

    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()