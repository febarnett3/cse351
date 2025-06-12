import threading
import time
import random

PHILOSOPHERS = 5
MAX_MEALS_EATEN = PHILOSOPHERS * 5

class Waiter:
    def __init__(self, num_philosophers):
        self.forks = [threading.Lock() for _ in range(num_philosophers)]
        self.lock = threading.Lock()
        self.meals_eaten = 0
        self.meals_lock = threading.Lock()
    
    def request_to_eat(self, left_index, right_index):
        with self.lock:
            if self.forks[left_index].locked() or self.forks[right_index].locked():
                return False
            # Lock both forks
            self.forks[left_index].acquire()
            self.forks[right_index].acquire()
            return True

    def done_eating(self, left_index, right_index):
        self.forks[left_index].release()
        self.forks[right_index].release()
        with self.meals_lock:
            self.meals_eaten += 1
            print(f"Total meals eaten: {self.meals_eaten}")
            return self.meals_eaten < MAX_MEALS_EATEN

class Philosopher(threading.Thread):
    def __init__(self, id, waiter):
        super().__init__()
        self.id = id
        self.left_index = id
        self.right_index = (id + 1) % PHILOSOPHERS
        self.waiter = waiter
        self.eaten = 0

    def run(self):
        while True:
            self.think()

            # Ask waiter to eat
            allowed = self.waiter.request_to_eat(self.left_index, self.right_index)
            if not allowed:
                wait_time = random.uniform(1, 3)
                print(f"Philosopher {self.id} is waiting {wait_time:.2f}s to try again.")
                time.sleep(wait_time)
                continue

            self.eat()
            self.eaten += 1

            # Inform waiter that this philosopher is done
            if not self.waiter.done_eating(self.left_index, self.right_index):
                break  # Stop if global max meals reached

    def think(self):
        print(f"Philosopher {self.id} is thinking.")
        time.sleep(random.uniform(1, 3))

    def eat(self):
        print(f"Philosopher {self.id} is eating.")
        time.sleep(random.uniform(1, 3))


def main():
    waiter = Waiter(PHILOSOPHERS)
    philosophers = [Philosopher(i, waiter) for i in range(PHILOSOPHERS)]

    for p in philosophers:
        p.start()
    
    for p in philosophers:
        p.join()

    print("\n--- Final Results ---")
    for p in philosophers:
        print(f"Philosopher {p.id} ate {p.eaten} times.")


if __name__ == '__main__':
    main()
