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
def process_blur(filename):
    input_path = os.path.join(INPUT_FOLDER, filename)
    output_path = os.path.join(STEP1_OUTPUT_FOLDER, filename)
    img = cv2.imread(input_path)
    if img is None:
        print(f"Failed to read {filename}")
        return
    smoothed = task_smooth_image(img, GAUSSIAN_BLUR_KERNEL_SIZE)
    cv2.imwrite(output_path, smoothed)

def process_grayscale(filename):
    input_path = os.path.join(STEP1_OUTPUT_FOLDER, filename)
    output_path = os.path.join(STEP2_OUTPUT_FOLDER, filename)
    img = cv2.imread(input_path)
    if img is None:
        print(f"Failed to read {filename}")
        return
    gray = task_convert_to_grayscale(img)
    cv2.imwrite(output_path, gray)

def process_edges(filename):
    input_path = os.path.join(STEP2_OUTPUT_FOLDER, filename)
    output_path = os.path.join(STEP3_OUTPUT_FOLDER, filename)
    img = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Failed to read {filename}")
        return
    edges = task_detect_edges(img, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
    cv2.imwrite(output_path, edges)
#----------------------------------------------------------------------------
def clear_and_recreate_folder(folder_path):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)  # Delete folder and all its contents
    os.makedirs(folder_path) 
#----------------------------------------------------------------------------
def run_image_processing_pipeline():
    print("Starting image processing pipeline...")

    print("Recreating folders...")
    clear_and_recreate_folder(STEP1_OUTPUT_FOLDER)
    clear_and_recreate_folder(STEP2_OUTPUT_FOLDER)
    clear_and_recreate_folder(STEP3_OUTPUT_FOLDER)

    # Get list of images from folder
    filenames = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith('.jpg')]

    num_cores = mp.cpu_count()

    # Use all cores for each step
    with mp.Pool(num_cores) as pool:
        print("Step 1: Smoothing images...")
        pool.map(process_blur, filenames)

        print("Step 2: Converting to grayscale...")
        pool.map(process_grayscale, filenames)

        print("Step 3: Detecting edges...")
        pool.map(process_edges, filenames)

    
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