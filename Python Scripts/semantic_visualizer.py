import argparse
import os
import numpy as np
import cv2
from matplotlib import pyplot as plt

parser = argparse.ArgumentParser()
parser.add_argument('--image_path', action='store',help='The path of a semantic segmentation generated image.')
parser.add_argument('--threshold', type=int, help='The minimum number (int) of pixels to consider a unique class.')


args = parser.parse_args()

if (args.image_path is None) or not os.path.isfile(args.image_path):
    print(
        '--image_path argument is not set. Please provide a valid path in the disk where the image is stored.')
    exit(1)

if (args.threshold is None) or not isinstance(args.threshold, int):
    print("--threshold argument is not set. Please provide a valid threshold as an integer.")

def get_unique_rgb_values(image, threshold):
    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    pixels = image.reshape((-1, 3))
    unique_rgb_values, counts = np.unique(pixels, axis=0, return_counts=True)
    mask = counts >= threshold
    unique_rgb_values_filtered = unique_rgb_values[mask]

    return unique_rgb_values_filtered

def create_grayscale_matrix(rgb_image, rgb_to_value_mapping):
    rgb_array = np.array(rgb_image)
    grayscale_matrix = np.zeros_like(rgb_array[:, :, 0], dtype=np.uint8)

    for value, target_rgb_values in rgb_to_value_mapping.items():
        mask = np.all(rgb_array == target_rgb_values, axis=-1)
        grayscale_matrix[mask] = value

    return grayscale_matrix

def rgb_image_to_one_hot_gray(rgb_array, target_rgb_values):
    mask = np.all(rgb_array == target_rgb_values, axis=-1)
    one_hot_gray = np.zeros_like(mask, dtype=np.uint8)
    one_hot_gray[mask] = 1

    return one_hot_gray


image_path = args.image_path
img = cv2.imread(image_path)
found_unique_classes = get_unique_rgb_values(img,int(args.threshold))
integral_mapping = {}

print("Found "+str(len(found_unique_classes))+" unique classes")
print("Visualizing the one-hot encoded mask for each of the detected classes...")

for i in range(len(found_unique_classes)):
    print(found_unique_classes[i])
    mask = rgb_image_to_one_hot_gray(img,found_unique_classes[i])
    integral_mapping[i] = found_unique_classes[i]
    plt.imshow(mask)
    plt.show()

image_ids = create_grayscale_matrix(img,integral_mapping)
print("The final gray-scale array with the semantic IDs is...")
print(image_ids)
print(image_ids.shape)