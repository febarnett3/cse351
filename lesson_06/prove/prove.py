"""
Course: CSE 351
Assignment: 06
Author: [Your Name]

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np
import shutil

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def process_images_in_folder(input_folder,              # input folder with images
                             output_folder,             # output folder for processed images
                             processing_function,       # function to process the image (ie., task_...())
                             load_args=None,            # Optional args for cv2.imread
                             processing_args=None):     # Optional args for processing function

    create_folder_if_not_exists(output_folder)
    print(f"\nProcessing images from '{input_folder}' to '{output_folder}'...")

    processed_count = 0
    for filename in os.listdir(input_folder):
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            continue

        input_image_path = os.path.join(input_folder, filename)
        output_image_path = os.path.join(output_folder, filename) # Keep original filename

        try:
            # Read the image
            if load_args is not None:
                img = cv2.imread(input_image_path, load_args)
            else:
                img = cv2.imread(input_image_path)

            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue

            # Apply the processing function
            if processing_args:
                processed_img = processing_function(img, *processing_args)
            else:
                processed_img = processing_function(img)

            # Save the processed image
            cv2.imwrite(output_image_path, processed_img)

            processed_count += 1
        except Exception as e:
            print(f"Error processing file '{input_image_path}': {e}")

    print(f"Finished processing. {processed_count} images processed into '{output_folder}'.")

# ---------------------------------------------------------------------------
def producer(input_folder, q1, q1_empty_slots, q1_full_slots, num_consumers):
    for filename in os.listdir(input_folder):
        if not filename.lower().endswith('.jpg'):
            continue
        image_path = os.path.join(input_folder, filename)
        img = cv2.imread(image_path)
        if img is None:
            print(f"Warning: Failed to load {filename}.")
            continue
        q1_empty_slots.acquire()
        q1.put((filename, img))  # Send (filename, image) tuple
        q1_full_slots.release()
    
    for _ in range(num_consumers):
        q1_empty_slots.acquire()
        q1.put(None)
        q1_full_slots.release()
#----------------------------------------------------------------------------
def blur_process(q1, q2, kernel_size,q1_empty_slots, q1_full_slots,q2_empty_slots, q2_full_slots, num_consumers):
    while True:
        q1_full_slots.acquire()
        item = q1.get()
        q1_empty_slots.release()

        if item is None:
            # Send sentinel to next stage for each consumer
            for _ in range(num_consumers):
                q2_empty_slots.acquire()
                q2.put(None)
                q2_full_slots.release()
            break

        filename, img = item
        smoothed_img = task_smooth_image(img, kernel_size)
        q2_empty_slots.acquire()
        q2.put((filename, smoothed_img))
        q2_full_slots.release()
#----------------------------------------------------------------------------
def grayscale_process(q2, q3,q2_empty_slots, q2_full_slots,q3_empty_slots, q3_full_slots, num_consumers):
    while True:
        q2_full_slots.acquire()
        item = q2.get()
        q2_empty_slots.release()
        if item is None:
            for _ in range(num_consumers):
                q3_empty_slots.acquire()
                q3.put(None)
                q3_full_slots.release()
            break
        filename, img = item
        gray_img = task_convert_to_grayscale(img)
        q3_empty_slots.acquire()
        q3.put((filename, gray_img))
        q3_full_slots.release()
#----------------------------------------------------------------------------
def edge_and_save_process(q3, output_folder, threshold1, threshold2,q3_empty_slots, q3_full_slots, lock):
    create_folder_if_not_exists(output_folder)
    while True:
        q3_full_slots.acquire()
        item = q3.get()
        q3_empty_slots.release()
        if item is None:
            break
        filename, img = item
        edge_img = task_detect_edges(img, threshold1, threshold2)
        output_path = os.path.join(output_folder, filename)
        # consider locking this.
        with lock:
            cv2.imwrite(output_path, edge_img)
# ---------------------------------------------------------------------------
def clear_and_recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Delete folder and all its contents
    os.makedirs(folder_path) 
#----------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")
    create_folder_if_not_exists(STEP3_OUTPUT_FOLDER)

    num_cores = mp.cpu_count()

    clear_and_recreate_folder(STEP1_OUTPUT_FOLDER)
    clear_and_recreate_folder(STEP2_OUTPUT_FOLDER)
    clear_and_recreate_folder(STEP3_OUTPUT_FOLDER)


    num_producers = 1
    num_blur = 2
    num_gray = 2
    num_edge = 1

    # TODO
    # - create queues
    q1 = mp.Queue()
    q2 = mp.Queue()
    q3 = mp.Queue()
    # create semphores
    q1_empty_slots = mp.Semaphore(10)
    q1_full_slots = mp.Semaphore(0)
    q2_empty_slots = mp.Semaphore(10)
    q2_full_slots = mp.Semaphore(0)
    q3_empty_slots = mp.Semaphore(10)
    q3_full_slots = mp.Semaphore(0)

    lock = mp.Lock()
    # - create barriers
    # - create the three processes groups
    num_processes = 3
    
    processes1 = [mp.Process(target=producer, args =(INPUT_FOLDER, q1, q1_empty_slots, q1_full_slots,num_blur)) for _ in range (num_producers)]
    processes2 = [mp.Process(target=blur_process, args =(q1, q2, GAUSSIAN_BLUR_KERNEL_SIZE,q1_empty_slots, q1_full_slots,q2_empty_slots, q2_full_slots, num_gray)) for _ in range (num_blur)]
    processes3 = [mp.Process(target=grayscale_process, args =(q2, q3,q2_empty_slots, q2_full_slots,q3_empty_slots, q3_full_slots, num_edge)) for _ in range (num_gray)]
    processes4 = [mp.Process(target=edge_and_save_process, args=(q3, STEP3_OUTPUT_FOLDER, CANNY_THRESHOLD1, CANNY_THRESHOLD2, q3_empty_slots, q3_full_slots, lock)) for _ in range(num_edge)]

    for p in processes1 + processes2 + processes3 + processes4:
        p.start()
    
    for p in processes1 + processes2 + processes3 + processes4:
        p.join()

    # Start processes
    # p1.start()
    # p2.start()
    # p3.start()
    # p4.start()

    # Wait for them to finish
    # p1.join()
    # p2.join()
    # p3.join()
    # p4.join()

    # - you are free to change anything in the program as long as you
    #   do all requirements.

    # --- Step 1: Smooth Images ---
    # process_images_in_folder(INPUT_FOLDER, STEP1_OUTPUT_FOLDER, task_smooth_image,
    #                          processing_args=(GAUSSIAN_BLUR_KERNEL_SIZE,))

    # --- Step 2: Convert to Grayscale ---
    # process_images_in_folder(STEP1_OUTPUT_FOLDER, STEP2_OUTPUT_FOLDER, task_convert_to_grayscale)

    # --- Step 3: Detect Edges ---
    # process_images_in_folder(STEP2_OUTPUT_FOLDER, STEP3_OUTPUT_FOLDER, task_detect_edges,
                            #  load_args=cv2.IMREAD_GRAYSCALE,        
                            #  processing_args=(CANNY_THRESHOLD1, CANNY_THRESHOLD2))

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Grayscale images are in: '{STEP1_OUTPUT_FOLDER}'")
    print(f"Smoothed images are in: '{STEP2_OUTPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
    else:
        run_image_processing_pipeline()

    log.write()
    log.stop_timer('Total Time To complete')