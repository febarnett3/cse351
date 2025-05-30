"""
Course: CSE 351
Assignment: 06
Author: Fiona Barnett

4. Meets Requirements: implemented 3 queues, distributed 2 processes for each group, decreased execution time significantly.
"""

import multiprocessing as mp
import os
import cv2
import shutil
from cse351 import *

# Constants
INPUT_FOLDER = "faces"
OUTPUT_FOLDER = "step3_edges"
ALLOWED_EXTENSIONS = [".jpg"]
GAUSSIAN_BLUR_KERNEL = (5, 5)
CANNY_THRESHOLDS = (75, 155)

# ----------------------------------------------------------------------------
def create_folder(folder):
    if os.path.exists(folder):
        for _ in range(3):  # Try 3 times
            try:
                shutil.rmtree(folder)
                break
            except PermissionError as e:
                print(f"Retrying folder delete: {e}")
                time.sleep(1)
    os.makedirs(folder)

# ----------------------------------------------------------------------------
def task_smooth(image):
    return cv2.GaussianBlur(image, GAUSSIAN_BLUR_KERNEL, 0)

def task_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def task_edge(image):
    return cv2.Canny(image, *CANNY_THRESHOLDS)

# ----------------------------------------------------------------------------
def producer(queue, input_folder, num_consumers):
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith('.jpg'):
            continue
        path = os.path.join(input_folder, filename)
        image = cv2.imread(path)
        if image is not None:
            queue.put((filename, image))
        else:
            print(f"Warning: Unable to load {filename}")
    for _ in range(num_consumers):
        queue.put(None)  # Sentinel

def smooth_worker(q_in, q_out):
    while True:
        item = q_in.get()
        if item is None:
            q_out.put(None)
            break
        filename, image = item
        smoothed = task_smooth(image)
        q_out.put((filename, smoothed))

def grayscale_worker(q_in, q_out):
    while True:
        item = q_in.get()
        if item is None:
            q_out.put(None)
            break
        filename, image = item
        gray = task_grayscale(image)
        q_out.put((filename, gray))

def edge_worker(q_in, output_folder):
    while True:
        item = q_in.get()
        if item is None:
            break
        filename, image = item
        edge = task_edge(image)
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, edge)

# ----------------------------------------------------------------------------
def run_pipeline():
    queue_size = 20  # Bounded queue to avoid overload
    print("Starting image processing pipeline...")
    create_folder(OUTPUT_FOLDER)

    cpu_count = mp.cpu_count()
    num_blur = 2
    num_gray = 2
    num_edge = 2

    q1 = mp.Queue(maxsize=queue_size)
    q2 = mp.Queue(maxsize=queue_size)
    q3 = mp.Queue(maxsize=queue_size)

    # Create processes
    producers = [mp.Process(target=producer, args=(q1, INPUT_FOLDER, num_blur))]
    blur_procs = [mp.Process(target=smooth_worker, args=(q1, q2)) for _ in range(num_blur)]
    gray_procs = [mp.Process(target=grayscale_worker, args=(q2, q3)) for _ in range(num_gray)]
    edge_procs = [mp.Process(target=edge_worker, args=(q3, OUTPUT_FOLDER)) for _ in range(num_edge)]

    for p in producers + blur_procs + gray_procs + edge_procs:
        p.start()

    for p in producers + blur_procs + gray_procs + edge_procs:
        p.join()

    q1.close()
    q1.join_thread()

    q2.close()
    q2.join_thread()

    q3.close()
    q3.join_thread()

    print("Image processing pipeline finished!")
    print(f"Original images: '{INPUT_FOLDER}'")
    print(f"Edge-detected images: '{OUTPUT_FOLDER}'")

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    if not os.path.exists(INPUT_FOLDER):
        print(f"Error: Folder '{INPUT_FOLDER}' not found. Place your images there.")
    else:
        run_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')
