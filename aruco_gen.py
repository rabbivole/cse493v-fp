import os

import numpy as np
import argparse
import cv2
import sys

FOLDER_PATH = "C:/python-experiment/tags"

ARUCO_DICT = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_4X4_1000": cv2.aruco.DICT_4X4_1000,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_5X5_1000": cv2.aruco.DICT_5X5_1000,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_6X6_1000": cv2.aruco.DICT_6X6_1000,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_7X7_1000": cv2.aruco.DICT_7X7_1000,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
    "DICT_APRILTAG_16h5": cv2.aruco.DICT_APRILTAG_16h5,
    "DICT_APRILTAG_25h9": cv2.aruco.DICT_APRILTAG_25h9,
    "DICT_APRILTAG_36h10": cv2.aruco.DICT_APRILTAG_36h10,
    "DICT_APRILTAG_36h11": cv2.aruco.DICT_APRILTAG_36h11
}

ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", required=True, help="path to output tag image")
ap.add_argument("-i", "--id", type=int, required=True, help="id of tag to generate")
ap.add_argument("-t", "--type", type=str, default="DICT_ARUCO_ORIGINAL",
                help="type of tag to generate (dict)")
args = vars(ap.parse_args())

# verify dict option
# if ARUCO_DICT.get(args["type"], None) is None:
#     print("incorrect dict type for aruco markers")
#     sys.exit(0)

# new version of dictionary_get
arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# parameters =  cv.aruco.DetectorParameters()
# detector = cv.aruco.ArucoDetector(dictionary, parameters)

# allocate mem, draw tag on output image
print("generating tag with id " + str(args["id"]))
tag = np.zeros((300, 300, 1), dtype="uint8")
# new version of drawMarker

cv2.aruco.generateImageMarker(arucoDict, args["id"], 300, tag, 1)

# write tag to disk, display
cv2.imwrite(os.path.join(FOLDER_PATH, args["output"]), tag)
cv2.imshow("aruco tag id " + str(args["id"]), tag)
cv2.waitKey(0)
