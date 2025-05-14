"""
Course    : CSE 351
Assignment: 04
Student   : Fiona Barnett

Instructions:
    - review instructions in the course
"""

import time
from common import *
import queue

from cse351 import *

THREADS = 30             # TODO - set for your program
WORKERS = 30
RECORDS_TO_RETRIEVE = 500 # Don't change


# ---------------------------------------------------------------------------
def retrieve_weather_data(q1, q2):
    while True:
        cmd = q1.get()
        if cmd is None:
            break  # Sentinel to stop the thread

        city, recno = cmd
        print(f"Thread received command: {cmd}")  # Debugging line

        # Request data from the server
        url = f"{TOP_API_URL}/record/{city}/{recno}"
        data = get_data_from_server(url)

        if data is None:
            print(f"Failed to retrieve data for URL: {url}")
        else: 
            print(f"Data retrieved: {data}")

        # Debugging: Print the data that was fetched
        print(f"Data retrieved for {city}, record {recno}: {data}")

        # Try putting data into q2, but handle queue full gracefully
        q2.put(data)


# ---------------------------------------------------------------------------
# TODO - Create Worker threaded class
class Worker(threading.Thread):
    def __init__(self, q2, noaa):
        super().__init__()
        self.q2 = q2
        self.noaa = noaa

    def run(self):
        print(f"Worker {self.name} started")
        while True:
            data = self.q2.get()  # BLOCKS until data is available
            if data is None:
                break

            print(f"Worker {self.name} received data: {data}")
            city = data['city']
            date = data['date']
            temp = data['temp']
            self.noaa.add_new_city(city)
            self.noaa.store_info(city, date, temp)
            print(f"Worker {self.name} processed and stored: City={city}, Date={date}, Temp={temp}")
    

# ---------------------------------------------------------------------------
  
# TODO - Complete this class
class NOAA:
    def __init__(self):
        # This will store cities and their respective records (city: [(date, temp), ...])
        self.cities_dict = {}

    def add_new_city(self, city):
        # Add city if not already present in the dictionary
        if city not in self.cities_dict:
            self.cities_dict[city] = []

    def store_info(self, city, date, temp):
        # Ensure temp is a float for consistent processing
        temp = float(temp)
        # Store the (date, temp) tuple
        self.cities_dict[city].append((date, temp))

    def get_temp_details(self, city):
        # Check if the city exists and has any records
        if city not in self.cities_dict or len(self.cities_dict[city]) == 0:
            return None  # Return None if no data exists

        total = 0
        for record in self.cities_dict[city]:  # Each record is (date, temp)
            total += record[1]  # Add the temperature value (already a float)

        return total / len(self.cities_dict[city])  # Average temperature


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
            msg = f'FAILED  Excepted {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


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
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    # Create queues and load work
    q1 = queue.Queue(maxsize=10)  # command queue for record retrieval
    q2 = queue.Queue(maxsize=10)  # worker queue for processing data
    
    # Create and start worker threads
    worker_threads = []
    retrieval_threads = []

    # Launch threads for retrieving weather data
    # 1. Start workers FIRST
    for _ in range(WORKERS):
        t = Worker(q2, noaa)
        t.start()
        worker_threads.append(t)

    # 2. Start retrieval threads NEXT
    for _ in range(THREADS):
        t = threading.Thread(target=retrieve_weather_data, args=(q1, q2))
        t.start()
        retrieval_threads.append(t)

    # 3. Add commands
    for name in CITIES:
        for i in range(RECORDS_TO_RETRIEVE):
            q1.put((name, i))
            print(f"Added command to queue: ({name}, {i})")  # Debugging statement

    # 4. Add sentinels to q1 AFTER work is enqueued
    for _ in range(THREADS):
        q1.put(None)

    # 5. Join retrieval threads
    for t in retrieval_threads:
        t.join()

    # 6. Add sentinels to q2 after retrieval is fully complete
    for _ in range(WORKERS):
        q2.put(None)

    # 7. Join workers
    for t in worker_threads:
        t.join()

    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

