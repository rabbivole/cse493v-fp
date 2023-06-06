import cv2
import numpy as np

# https://www.youtube.com/watch?v=3h7wgR5fYik
# wanted to do charuco calibration, looked at a billion tutorials, could not figure
# out how to make it work after the overhaul they did.
# all i have is a stackoverflow reply i came across from like 3 months ago: "The aruco library
# is a complete mess right now and will continue to be a mess until somebody bothers to fix it."

chessboardSize = (10,7)
frameSize = (1280, 720)

criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0], 0:chessboardSize[1]].T.reshape(-1,2)

objPoints = []
imgPoints = []

for i in range(0, 23):
    img = cv2.imread("calib-" + str(i) + ".png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ret, corners = cv2.findChessboardCorners(gray, chessboardSize)

    if ret:
        objPoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgPoints.append(corners)

        cv2.drawChessboardCorners(img, chessboardSize, corners2, ret)
        cv2.imshow('img', img)
        cv2.waitKey(1000)
    else:
        print("not found! at img " + str(i))

ret, cameraMatrix, dist, rvecs, tvecs = cv2.calibrateCamera(objPoints, imgPoints, frameSize, None, None)
print("calibration results:")
print("\nmtx: ", cameraMatrix)
print("\ndist: ", dist)
print("\nrvecs: ", rvecs)
print("\ntvecs: ", tvecs)

# undistortion?

img = cv2.imread('calib-5.png')
h, w = img.shape[:2]
newCameraMtx, roi = cv2.getOptimalNewCameraMatrix(cameraMatrix, dist, (w,h), 1, (w,h))

dst = cv2.undistort(img, cameraMatrix, dist, None, newCameraMtx)
x, y, w, h = roi
dst = dst[y:y+h, x:x+w]
cv2.imwrite("result.png", dst)