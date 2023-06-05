import cv2
import cv2.aruco as aruco
import numpy as np
import socket

# some earlier code:
# https://www.youtube.com/watch?v=GEWoGDdjlSc
# the distance estimation:
# https://www.youtube.com/watch?v=mn-M6Qzx6SE
# although tihs guy's code gives me hives and really only pointed out 'tvec is a t vec'

UDP_IP = "127.0.0.1"
UDP_PORT = 7999
SOCK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# doublecheck format on matrix/dist
# calculated camera intrinsic matrix coefficients, i think?
MATRIX = np.array([[657.10847519, 0., 644.30783951],
 [0., 657.96298689, 375.44091335],
 [0., 0., 1.]])
# calculated camera distortion coefficients, i think?
DIST = np.array([[0.17608815, -0.26971785, -0.00138746, 0.00203728, 0.13184202]])
MARKERSIZE = 0.057 # in meters

R_INVERSE = np.array([[-0.02080542, -0.55828519,  0.8293882],
                     [-0.99952058, -0.00741072, -0.03006161],
                     [0.02292931, -0.82961601, -0.55786335]])
ORIGIN_C = np.array([-0.00906836, 0.27812592, 1.06672039])

def pose_estimation(frame, arucoDict, mtxCoefficients, distCoefficients):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict, parameters)

    corrected = cv2.undistort(gray, mtxCoefficients, distCoefficients)
    corners, ids, rejected_img_pts = detector.detectMarkers(corrected)
    # ok we can't do refineDetectedMarkers because that's for boards only

    if len(corners) > 0:
        for i in range(0, len(ids)):
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i],
                                                                           MARKERSIZE,
                                                                           mtxCoefficients,
                                                                           distCoefficients)

            pvec = moveToWorld(tvec[0][0])
            blastData(pvec)
            print(rvec)

            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, mtxCoefficients, distCoefficients, rvec, tvec, 0.05)

    return frame

def moveToWorld(tvec):
    return np.matmul(R_INVERSE, tvec - ORIGIN_C)


# Fling pose data at the UDP port and hope they hear it.
# All units are meters. All positions are maybe in world frame. All positions are also in a right-
# handed coordinate system, which is going to explode in Unity.
def blastData(pvec):
    # format our output
    out = "X=" + str(round(pvec[0], 5)) + " "
    out += "Y=" + str(round(pvec[1], 5)) + " "
    out += "Z=" + str(round(pvec[2], 5))

    # blast it
    SOCK.sendto(out.encode(), (UDP_IP, UDP_PORT))

    # also print
    #print(out)



def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while cap.isOpened():
        ret, img = cap.read()

        if not ret:
            break

        output = pose_estimation(img, DICT, MATRIX, DIST)

        #cv2.imshow('estimated pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

