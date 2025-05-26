# # import threading
# # # creating semaphores (the name is important -- what is it intending to signal?)
# # space_in_queue = threading.semaphore(10)
# # stuff_in_queue = threading.semaphore(0)

# # barrier = threading.barrier(PRODUCERS)

# # producers = [threading.Thread(target = producer , args = (queue, space_in_queue, stuff_in_queue)) for _ in range (PRODUCERS)] # you can do this in one line

# # consumers = [threading.Thread(target = consumer, args =(queue, space_in_queue, stuff_in_queue)) for _ in range(CONSUMERS)]

# # for t in producers + producers:
# #     t.start()

# # for t in producers + producers:
# #     t.join()

# # # what do we need to do in the queue? 
# # # how to place on a queue?
# # #these colons after each parameter ensure that the parameter is the correct type.
# # def producer(queue:Queue351, space_in_queue:threading.Semaphore, barrier:threading.Barrier):
# #     space_in_queue.acquire()
# #     queue.put(number)
# #     stuff_in_queue.release()

# #     # we take the first item that gets to the barrier and add none to it, that way it's only a single 'All done' message
# #     # it is a synchronization tool that requires certain amount of threads to reach this point before they can continue.
# #     #the wait function assigns those values of 0, 1, 2, 3, but it's not the nae of a thread. it's a way of tracking the thread, it's the value it retuns for a thread going through the wait
# #     if barrier.wait() == 0:
# #         space_in_queue.acquire()
# #         queue.put(None)
# #         stuff_in_queue.release()

# # def consumer(): #put parameters in there as usual
# #     stuff_in_queue.acquire()
# #     queue.get()
# #     space_in_queue.release()

# #     if value is None:
# #         space_in_queue.acquire()
# #         queue.put(None)
# #         stuff_in_queue.release()
# #         break #only one has the none value however


# # os.Remove(file_name)

# # # put f.flush() after writing to a file.. this prevents a runtime error

# # you cn use multiple processes on CPU, it has private memory.
# #you can share memory between threads, but a process had its own set of memory <- that's a downside for processes
# #every tab on chrome is a process, crash isolation

# import random
# import threading
# import multiprocessing as mp
# import time

# PRIME_COUNT =10000

# def is_prime(n: int):
#     if n <= 3:
#         return n > 1
#     if n % 2 == 0 or n % 3 == 0:
#         return False
#     i = 5
#     while i ** 2 <= n:
#         if n % i == 0 or n % (i + 2) == 0:
#             return False
#         i += 6
#     return True

# def main():
#      random.seed(102030)
#      for i in range(PRIME_COUNT):
#         number = random.randint(1, 1_000_000_000_000)
#         thread = mp.Process(target=check_prime, args(number,))
#         if is_prime(number):
#             print(number)


# if __name__ =='__main__':
#     main()


# processes = [mp.Process(target=check) for _ in range (process_count)]
# #processes have locks, semaphores, and barriers