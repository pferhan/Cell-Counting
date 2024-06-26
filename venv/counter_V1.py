from PIL import (Image, ImageOps)
import numpy as np
import pandas as pd
from scipy import ndimage
import sys
import os

sys.setrecursionlimit(2000)

def thresholdGreenPixels(imageArray, threshold):
    greenChannel = imageArray[:, :, 1]
    thresholdedImage = np.where(greenChannel > threshold, 255, 0)
    return thresholdedImage

def largestBlob(blobSizes):
    largestBlobSize = 0
    largestBlobID = None

    # find the largest blob in the image
    for blobID in blobSizes:
        blobSize = blobSizes[blobID]

        if blobSize > largestBlobSize:  # checks if the current blob is larger than the previously found largest blob
            largestBlobSize = blobSize  # stores the size and ID of the largest blobs
            largestBlobID = blobID

    return largestBlobSize, largestBlobID

# Counts number of green blobs (sections marked True in visited array)
def countBlobs(thresholdedImage, minBlobSize):
    blobID = 1
    visitedArray = np.zeros_like(thresholdedImage, dtype=bool) # Array to mark pixels visited - all values start set to false
    blobSizes = {}  # track the sizes of each blob found; key = blob ID / value = size
    blobCoordinates = {}; #track coordinates of each blob

    # Adds neighboring pixels to existing blob
    def addPixel(new_i, new_j, blobID):
        blobSizes[blobID] = blobSizes.get(blobID,0) + 1
        blobCoordinates.setdefault(blobID, []).append((new_i, new_j))

        visitedArray[new_i, new_j] = True

        # explores the 8 pixels around the one being explored
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                new_i2 = new_i + di
                new_j2 = new_j + dj

                if (0 <= new_i2 < visitedArray.shape[0] and 0 <= new_j2 < visitedArray.shape[1]):
                    if (not visitedArray[new_i2, new_j2] and thresholdedImage[new_i2, new_j2] == 255):
                        addPixel(new_i2, new_j2, blobID)

    # Covers whole array and adds pixels to blobs
    for i in range(thresholdedImage.shape[0]):
        for j in range(thresholdedImage.shape[1]):
            if thresholdedImage[i, j] != 255:
                visitedArray[i, j] = True
            elif not visitedArray[i, j]:
                addPixel(i, j, blobID)  # adds current pixel under specified ID
                blobID += 1

    filteredBlobSizes = {k: v for k, v in blobSizes.items() if v > minBlobSize}
    filteredBlobCoordinates = {k: blobCoordinates[k] for k in filteredBlobSizes.keys()}
    largestBlobSize, largestBlobID = largestBlob(filteredBlobSizes)

    return filteredBlobSizes, largestBlobSize, largestBlobID, filteredBlobCoordinates

def blobStats(filteredBlobSizes):
    sizes = list(filteredBlobSizes.values())

    if not sizes:
        mean_size = 0
        median_size = 0
    else:
        mean_size = np.mean(sizes)
        median_size = np.median(sizes)

    return mean_size, median_size
    #add range in both x and y directions
    #think of other stats to report

def visualizeBlobs(thresholdedImage, blobSizes, minBlobSize, imageArray):
    # Label connected components in the thresholded image
    labeled_image, num_features = ndimage.label(thresholdedImage == 255)

    # Create a black image with the same shape as the original image
    visualizedImage = np.zeros_like(imageArray)

    # Iterate through labeled blobs and draw blobs on the black image
    for blobID in range(1, num_features + 1):
        blobSize = np.sum(labeled_image == blobID)

        if blobSize >= minBlobSize:
            # Set pixels belonging to the current blob to white in the black image
            visualizedImage[labeled_image == blobID] = 255

    # Convert the data type of the array to uint8
    visualizedImage = visualizedImage.astype(np.uint8)

    # Display the visualized image
    Image.fromarray(visualizedImage).show()

def export(data, filename):
    if os.path.exists(filename):
        existing_data = pd.read_excel(filename)
        all_data = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
        all_data.to_excel(filename, index=False)
    else:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)

def process_image(image_path, threshold, minBlobSize, output_file):
    image_name = os.path.basename(image_path)

    image = Image.open(image_path)
    imageArray = np.array(image)

    thresholdedImage = thresholdGreenPixels(imageArray, threshold)

    blobDict, largestBlobSize, largestBlobID, blobCoordinates = countBlobs(thresholdedImage, minBlobSize)

    mean_size, median_size = blobStats(blobDict)

    blobRanges = {}
    for blobID, coordinates in blobCoordinates.items():
        x_values = [coord[1] for coord in coordinates]
        y_values = [coord[0] for coord in coordinates]
        x_range = max(x_values) - min(x_values)
        y_range = max(y_values) - min(y_values)
        blobRanges[blobID] = {'X-Range': x_range, 'Y-Range': y_range}

    #1 pixel is roughly 1.636 microns
    pixel_to_micron = 1.636
    blobAreas = {}
    for blobID, size in blobDict.items():
        area = size * (pixel_to_micron**2)
        area_mm = area / (10**6)
        blobAreas[blobID] = area_mm

    ''' 
    Print out actual images:

    thresholdedImage_uint8 = thresholdedImage.astype(np.uint8)
    Image.fromarray(thresholdedImage_uint8).show()

    visualizeBlobs(thresholdedImage, blobDict, minBlobSize, imageArray)
    '''
    data = {
        "Image Name": [image_name],
        "Threshold": [threshold],
        "Minimum Blob Size": [minBlobSize],
        "Number of Blobs": [len(blobDict)],
        "Blob Areas (mm^2)": [blobAreas],
        "Median Blob Size (mm^2)": [median_size*pixel_to_micron/10**6],
        "Mean Blob Size (mm^2)": [mean_size*pixel_to_micron/10**6],
        "Largest Blob Size (mm^2)": [largestBlobSize*pixel_to_micron/10**6],
        "Largest Blob ID": [largestBlobID],
        "Blob Ranges": [blobRanges]
    }

    export(data, "output.xlsx")

def count_directories(directory):
    num_directories = sum(1 for _ in os.walk(directory)) - 1  # Subtract 1 to exclude the starting directory itself
    return num_directories

def process_directory(directory, threshold, minBlobSize, output_file):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tif") and "RED" not in file.upper() and "GREEN" not in file.upper() and "BLUE" not in file.upper():
                image_path = os.path.join(root, file)
                process_image(image_path, threshold, minBlobSize, output_file)

def main():
    directory = "/Users/hannahpfersch/Library/CloudStorage/OneDrive-QuinnipiacUniversity/Pfersch Blake Ind Study SP24/RelA Immuno Images/MATSEP 01"
    #directory = "/Users/hannahpfersch/Documents/College/Senior/SP24/CSC494/AutomatedCellCounter/venv/lib"
    threshold = int(input("What is the green threshold for neurons (0-255)?: " ))
    minBlobSize = int(input("Enter the minimum blob size: "))
    output_file = "output.xlsx"

    num_directories = count_directories(directory)
    print("Total number of directories to process: ", num_directories)

    current_directory_num = 0

    for root, dirs, files in os.walk(directory):
        for directory in dirs:
            current_directory_num += 1
            print("Processing directory:", directory, "({}/{})".format(current_directory_num, num_directories))
            directory_path = os.path.join(root, directory)
            process_directory(directory_path, threshold, minBlobSize, output_file)
    #process_directory(directory, threshold, minBlobSize, output_file)

if __name__ == "__main__":
    main()