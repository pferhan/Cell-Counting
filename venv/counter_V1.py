from PIL import (Image, ImageOps)
import numpy as np
import pandas as pd
from scipy import ndimage
import sys
import os

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
    # Array to mark pixels visited - all values start set to false
    visitedArray = np.zeros_like(thresholdedImage, dtype=bool)

    blobSizes = {}  # track the sizes of each blob found; key = blob ID / value = size

    # Adds neighboring pixels to existing blob
    def addPixel(new_i, new_j, blobID):

        blobSizes[blobID] = blobSizes.get(blobID,0) + 1

        # explores the 8 pixels around the one being explored
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                new_i2 = new_i + di
                new_j2 = new_j + dj

                if (0 <= new_i2 < visitedArray.shape[0] and 0 <= new_j2 < visitedArray.shape[1]):
                    if (not visitedArray[new_i2, new_j2] and thresholdedImage[new_i2, new_j2] == 255):
                        visitedArray[new_i, new_j] = True
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

    largestBlobSize, largestBlobID = largestBlob(filteredBlobSizes)

    return filteredBlobSizes, largestBlobSize, largestBlobID

def blobStats(filteredBlobSizes):
    sizes = list(filteredBlobSizes.values())

    if not sizes:
        print("No blobs found.")
        return

    mean_size = np.mean(sizes)
    median_size = np.median(sizes)

    print(f"Mean Blob Size: {mean_size:.2f} pixels")
    print(f"Median Blob Size: {median_size} pixels")
    #print blob id with stats
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

def process_image(image_path, threshold, minBlobSize):
    image = Image.open(image_path)
    imageArray = np.array(image)

    thresholdedImage = thresholdGreenPixels(imageArray, threshold)

    blobDict, largestBlobSize, largestBlobID = countBlobs(thresholdedImage, minBlobSize)

    print(f"Statistic for image: {image_path}")
    blobStats(blobDict)
    print(f"The largest blob has {largestBlobSize} pixels at ID:{largestBlobID}.")
    print(f"There are {len(blobDict)} blobs.")

    visualizeBlobs(thresholdedImage, blobDict, minBlobSize, imageArray)

def process_directory(directory, threshold, minBlobSize):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tif"):
                image_path = os.path.join(root, file)
                process_image(image_path, threshold, minBlobSize)

def main():
    #directory = "/Users/hannahpfersch/Library/CloudStorage/OneDrive-QuinnipiacUniversity/Pfersch Black Ind Study SP24"
    directory = "/Users/hannahpfersch/Documents/College/Senior/SP24/AutomatedCellCounter/venv/lib"
    threshold = int(input("What is the green threshold for neurons (0-255)?: " ))
    minBlobSize = int(input("Enter the minimum blob size: "))

    process_directory(directory, threshold, minBlobSize)

if __name__ == "__main__":
    main()



