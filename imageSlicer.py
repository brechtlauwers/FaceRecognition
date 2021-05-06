import cv2
import numpy
import glob

tileSize = 128
name = "n9"
counter = 0

for filename in glob.glob("../Faces database/negatief/monke/n9/*jpg"):
    img = cv2.imread(filename)
    counter += 1
    for r in range(0, img.shape[0], tileSize):

        for c in range(0, img.shape[1], tileSize):
            test = img[r:r+tileSize, c:c+tileSize,:]
            height, width = test.shape[:2]

            if (height == tileSize and width == tileSize):
                cv2.imwrite(f"../Faces database/crops/monke/n9/img{name}_{counter}_{r}_{c}.png",img[r:r+tileSize, c:c+tileSize,:])

print("ready!")