from PIL import (Image, ImageOps)
import numpy as np
from scipy import ndimage
import sys

threshold = int(input("What is the green threshold for neurons? (0-255) " ""))
# Thresholds the image so that green pixels become white
def thresholdGreenPixels(imageArray):
    greenChannel = imageArray[:, :, 1]
    thresholdedImage = np.where(greenChannel > threshold, 255, 0)

    return thresholdedImage

def printThreshold(image, threshold):
    greenChannel = image.split()[1]
    thresholdedImage = greenChannel.point(lambda x: 255 if x > threshold else 0)
    image.show()
    thresholdedImage.show()

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
def countBlobs(thresholdedImage):
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
        #print(f"FOUND BLOB {blobID}")

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

def visualizeBlobs(thresholdedImage, blobSizes, minBlobSize):
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

# Load the image
image = Image.open("lib/Photos/image2.tif")
#image = Image.open("lib/Photos/Matsep 01_RelA_Iba1_NeuN_ VH_MODG LEFT (B_5_30) (G_6_20) (R_7_20)1.tif")

# Convert image to an array
imageArray = np.array(image)

# Green pixels become white
thresholdedImage = thresholdGreenPixels(imageArray)

# Set minimum number of pixels
minBlobSize = int(input("Enter the minimum blob size: "))

# Count the number of blobs and find the largest collection.
blobDict, largestBlobSize, largestBlobID = countBlobs(thresholdedImage)

blobStats(blobDict)

print(f"The largest blob has {largestBlobSize} pixels at ID:{largestBlobID}.")
print(f"There are {len(blobDict)} blobs.")

printThreshold(image, threshold)
# Visualize the image with blobs above the minimum size threshold
visualizeBlobs(thresholdedImage, blobDict, minBlobSize)