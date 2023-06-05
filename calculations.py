import cv2
import numpy as np

# so we have a translation vector which indicates marker's position relative to the camera
tvec = np.array([0.00254988, 0.24471246, 1.04891921])
# we have a rotation vector defining an axis of rotation (where magnitude is the rotation in radians)
rvec = np.array([2.18227069e+00, -3.49198308e-02, -7.59573209e-04])

# create a rotation matrix
rMat, _ = cv2.Rodrigues(rvec)

# let P_w be the point in world coordinates. for the system we set up, we're deciding the marker
# in this one picture is on a box placed at world origin
p_w = np.array([0, 0, 0.042]) # the box is 42mm tall

print(np.matmul(rMat, p_w) + tvec)

p_cComputed = np.array([0.00197676, 0.21033427, 1.02479844])

inverseR = np.linalg.inv(rMat)

print(np.matmul(inverseR, p_cComputed - tvec))
# so this computes p_world as
# ~0, ~0, .042. so this is a valid equation

# so let's compute p_w given a different tvec as our point
p1 = np.array([-0.04307415, 0.04322366, 1.31356474])
print("worldspace estimate for p1, relative to chosen origin: ")
print(np.matmul(inverseR, p1 - p_cComputed))

p2 = np.array([-0.25912928, 0.25876421, 1.05572097])
print("worldspace estimate for p2, relative to chosen origin: ")
print(np.matmul(inverseR, p2 - p_cComputed))