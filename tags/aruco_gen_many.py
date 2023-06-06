import numpy as np
import cv2

# the tags actually used in the assignment were from 5X5_100. i planned to try 4X4_50 with the idea
# that a smaller, simpler dictionary might give better tracking results.
# new version of dictionary_get:
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)

# allocate mem in a np array, draw tag bits into it
for i in range(0, 30):
    print("generating tag with id " + str(i))
    tag = np.zeros((300, 300, 1), dtype="uint8")
    # new version of drawMarker:
    cv2.aruco.generateImageMarker(arucoDict, i, 300, tag, 1)

    # write tag to disk
    cv2.imwrite("DICT_4X4_50_" + str(i) + ".png", tag)

