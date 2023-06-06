import cv2
import cv2.aruco as aruco
import numpy as np
import socket

# tutorial for aruco pose estimation. the actual functions have changed a bit but i still used this
# general structure
# https://www.youtube.com/watch?v=GEWoGDdjlSc

# sockets library stuff for sending data to unity. i had to make a burner account just to see 3
# salient lines of this starter python code. https://www.kodeco.com/5475-introduction-to-using-opencv-with-unity
# saved me 100 bucks on the OpenCV For Unity plugin though
UDP_IP = "127.0.0.1"
UDP_PORT = 7999
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# i rarely saw numbers smaller than about 0.001, but this is a div-by-zero guard
EPSILON = 0.00001

# aruco dictionary to look for; this is the new version of Dictionary_get
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)

# calculated camera intrinsic matrix coefficients, which i was too lazy to read/write to a file
MATRIX = np.array([[657.10847519, 0., 644.30783951],
 [0., 657.96298689, 375.44091335],
 [0., 0., 1.]])
# calculated camera distortion coefficients
DIST = np.array([[0.17608815, -0.26971785, -0.00138746, 0.00203728, 0.13184202]])
MARKER_SIZE = 0.057  # in meters

# for calculating world coordinates relative to a chosen origin
# inverse of the rotation that takes camera space to world space
R_INVERSE = np.array([[0.99831605, -0.01492152,  0.05605724],
                     [-0.0545568, -0.56990949, 0.81989434],
                     [0.01971348, -0.82157198, -0.56976386]])
# camera coordinates of the chosen origin
ORIGIN_C = np.array([1.87551812e-04, 2.47558008e-01, 1.04777571e+00])
# for a failed attempt at computing a rotation for the object, which i have left in because... i'm
# not sure actually. but i was so sure it could work. :(
ROT_TO_WORLD = np.array([2.17696047, -0.04820015, 0.05256546])

# Detects one ArUco marker. Estimates a pose for it, calculates pose information, draws some axes,
# and sends the data to Unity. Returns the frame with marker info drawn on it.
def pose_estimation(frame, aruco_dict, mtx_coefficients, dist_coefficients):
    # it's generally recommended to go to grayscale for aruco detection, though anecdotally i didn't
    # really notice a detection quality difference with BGR
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # newer aruco detection involves an ArucoDetector object with DetectorParameters
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)

    # try to use the calculated distortion info from calibration to un-distort
    corrected = cv2.undistort(gray, mtx_coefficients, dist_coefficients)
    # actually do the detection; this is now done as an ArucoDetector class function
    corners, ids, rejected_img_pts = detector.detectMarkers(corrected)

    if len(corners) > 0:
        for i in range(0, len(ids)):
            rvec, tvec, marker_points = cv2.aruco.estimatePoseSingleMarkers(corners[i],
                                                                            MARKER_SIZE,
                                                                            mtx_coefficients,
                                                                            dist_coefficients)

            # calculate P_w for tvec (eg P_cam)
            p_vec = moveToWorld(tvec[0][0])
            # calculate 'forward' vector and 'up' vector so unity can do work for us
            f_vec, u_vec = computeLookAtVectors(rvec[0][0])
            # send info to unity
            sendData(f_vec, u_vec, p_vec)

            # draw some stuff on the frame. this can be omitted if we're running 'silently', ie
            # no imshow
            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, mtx_coefficients, dist_coefficients, rvec, tvec, 0.05)

    return frame

# Formats data into a parseable string and then sends it to Unity.
# f_vec: front
# u_vec: up
# p_vec: world coordinates (position_vec)
def sendData(f_vec, u_vec, p_vec):
    # format our output
    fv = np.around(f_vec, 5)  # 5 decimal places seems reasonable given the numbers involved
    uv = np.around(u_vec, 5)
    out = "POS("  # world position
    out += str(round(p_vec[0], 5)) + " "
    out += str(round(p_vec[1], 5)) + " "
    out += str(round(p_vec[2], 5)) + ")"

    out += "|F("  # then the f and u vectors
    out += str(fv[0]) + " "
    out += str(fv[1]) + " "
    out += str(fv[2]) + ")"

    out += "|U("
    out += str(uv[0]) + " "
    out += str(uv[1]) + " "
    out += str(uv[2]) + ")"

    # blast data at the UDP port and hope they hear it
    SOCK.sendto(out.encode(), (UDP_IP, UDP_PORT))

# Given the rvec that rotates from camera space to a marker pose, compute 'up' and 'front' vectors
# in world space and return them.
def computeLookAtVectors(rvec):
    r_mat, _ = cv2.Rodrigues(rvec)
    # this seems like it's in the camera frame, so we use the original R for our origin to move it
    # to world
    r_mat = np.matmul(np.linalg.inv(R_INVERSE), r_mat)
    front_vec = r_mat[:, 1]
    up_vec = r_mat[:, 2]
    return front_vec, up_vec

# Given the tvec that describes a marker's camera coordinates, computes and returns world
# coordinates for the marker's center.
def moveToWorld(tvec):
    # derived from an equation from this explanation of pinhole camera model
    # https://stackoverflow.com/a/46370215
    return np.matmul(R_INVERSE, tvec - ORIGIN_C)

# A failed attempt at computing an object orientation.
def doExperiment(rvec):
    # my thinking was: we essentially want to calculate a rotation that transforms the origin axes
    # to the direction of the object. the colloquial 'difference between' these two vectors would
    # theoretically be how we needed to rotate the box in unity (after a translation to
    # left-handedness, obv)
    v_world = normalize(ROT_TO_WORLD)  # rotation to get from camera to world
    v_obj = normalize(rvec)  # actual orientation of the object

    # calculate axis of this rotation
    axis = normalize(np.cross(v_obj, v_world))
    # calculate amount of rotation
    angle = np.arccos(np.dot(v_obj, v_world))

    # this didn't work, sadly. rotating about one axis irl did not produce a rotation about one
    # axis in unity; each one was wonky in one direction or another. but uh. at least i tried?

    # send unity axis and angle, since it has quaternion rotations, and go from there
    return axis, angle


# Returns a normalized copy of a 3d 'vec'.
def normalize(vec):
    norm = np.linalg.norm(vec)
    if norm <= EPSILON:
        return vec
    return vec / norm


def main():
    # set up camera
    # 0 is the device index; if you only have one device plugged in, it's 0. my macbook has an
    # embedded webcam so it tended to be 1 there
    cap = cv2.VideoCapture(0)
    # https://stackoverflow.com/a/68790110 because on PC this defaults to a tiny cropped version
    # note that this delays the camera by about a second. but only on PC. never figured this out.
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while cap.isOpened():
        ret, img = cap.read()

        if not ret:
            break

        output = pose_estimation(img, DICT, MATRIX, DIST)

        # remove this to run 'silently', though i didn't notice a speed difference between showing
        # the camera output vs not doing that
        cv2.imshow('estimated pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

