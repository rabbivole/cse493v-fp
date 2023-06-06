import cv2
import cv2.aruco as aruco
import numpy as np

DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# calculated camera intrinsic matrix coefficients
MATRIX = np.array([[657.10847519, 0., 644.30783951],
 [0., 657.96298689, 375.44091335],
 [0., 0., 1.]])
# calculated camera distortion coefficients
DIST = np.array([[0.17608815, -0.26971785, -0.00138746, 0.00203728, 0.13184202]])
MARKER_SIZE = 0.057  # in meters


def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print("Place a marker tag on the floor where you want the origin to be.")
    print("Ensure the detected marker z-axis is pointing up. Press c to choose an origin.")

    while cap.isOpened():
        ret, img = cap.read()
        if not ret:
            break

        out_frame, rvec, tvec = pose_estimate(img, DICT, MATRIX, DIST)

        cv2.imshow('estimated pose', out_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            recordOrigin(rvec, tvec)
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Utility for choosing an origin based on some marker pose on the floor, then spitting out the
# quantities needed to compute stuff with it. See world pose equation.
def recordOrigin(rvec, tvec):
    # create rotation matrix R and invert it
    r_mat, _ = cv2.Rodrigues(rvec)  # discard jacobian
    r_inv = np.linalg.inv(r_mat)
    # record origin location in camera space coordinates, ie tvec
    origin_c_out = tvec
    print("rvec to rotate from camera space to world space, we hope: ")
    print(rvec)
    print("recover worldspace coords with: ")
    print("np.matmul(r_inv, POINT - origin_c)")
    print("r_inv = ")
    print(r_inv)
    print("origin_c= ")
    print(origin_c_out)


# Copy/pasted code for doing ArUco detection. Only looks for one marker.
def pose_estimate(frame, aruco_dict, mtx_coeff, dist_coeff):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # undistort the frame according to camera intrinsics
    corrected = cv2.undistort(gray, mtx_coeff, dist_coeff)
    # detect
    corners, ids, rejected = detector.detectMarkers(corrected)

    rvec_out, tvec_out = None, None
    # if we found a marker, estimate its pose
    if len(corners) > 0:
        rvec, tvec, marker_pts = cv2.aruco.estimatePoseSingleMarkers(corners[0],
                                                                     MARKER_SIZE,
                                                                     mtx_coeff,
                                                                     dist_coeff)

        # draw things
        cv2.aruco.drawDetectedMarkers(frame, corners)
        cv2.drawFrameAxes(frame, mtx_coeff, dist_coeff, rvec, tvec, 0.05)

        # everything's bundled in 40 array layers for some reason so un-wrap it
        rvec_out = rvec[0][0]
        tvec_out = tvec[0][0]

    return frame, rvec_out, tvec_out

if __name__ == "__main__":
    main()