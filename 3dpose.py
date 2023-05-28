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

BLUE = (255, 0, 0)
DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# doublecheck format on matrix/dist
# calculated camera intrinsic matrix coefficients, i think?
MATRIX = np.array([[657.10847519, 0., 644.30783951],
 [0., 657.96298689, 375.44091335],
 [0., 0., 1.]])
# calculated camera distortion coefficients, i think?
DIST = np.array([[0.17608815, -0.26971785, -0.00138746, 0.00203728, 0.13184202]])
# and then hopefully our rvecs/tvecs?
RVECS =  np.array((np.array([[-0.64118725],
       [-0.174055  ],
       [ 0.0693866 ]]), np.array([[ 0.04190104],
       [-0.12093472],
       [ 0.04410305]]), np.array([[-0.66294751],
       [-0.68540124],
       [ 1.32265599]]), np.array([[0.68403977],
       [0.6279388 ],
       [1.58953421]]), np.array([[ 1.17896259],
       [-0.45644572],
       [ 1.22213011]]), np.array([[-0.75254021],
       [ 0.9027882 ],
       [ 1.82836991]]), np.array([[-0.06546616],
       [-0.33029715],
       [ 1.60300867]]), np.array([[ 0.60872508],
       [-0.00816964],
       [-2.92625199]]), np.array([[-0.33240032],
       [-0.11335889],
       [-2.75824192]]), np.array([[ 1.72283511],
       [ 0.21813688],
       [-2.59741142]]), np.array([[0.06400964],
       [0.96996122],
       [0.21892373]]), np.array([[-0.51528544],
       [ 0.32612445],
       [ 1.36969965]]), np.array([[ 0.46776994],
       [ 0.54225436],
       [-0.10367118]]), np.array([[ 0.76137121],
       [-0.13963901],
       [-1.58102577]]), np.array([[-0.24420128],
       [ 0.56685697],
       [ 1.75593715]]), np.array([[0.57100096],
       [0.17252347],
       [2.23378108]]), np.array([[0.52427416],
       [0.00670348],
       [1.80086399]]), np.array([[ 0.08222109],
       [-0.53315131],
       [ 1.89678662]]), np.array([[ 0.12315978],
       [ 0.81373144],
       [-2.96228496]])))
TVECS = np.array((np.array([[-4.73662521],
       [ 2.49031943],
       [31.88915573]]), np.array([[-3.28493857],
       [-3.84408981],
       [13.71511318]]), np.array([[-10.9399742 ],
       [ -7.88245575],
       [ 33.38498491]]), np.array([[14.78992713],
       [-2.69522943],
       [22.405281  ]]), np.array([[ 5.511798  ],
       [-8.26246626],
       [17.41160863]]), np.array([[ 3.11542131],
       [ 2.93992297],
       [26.07313395]]), np.array([[ 5.20462777],
       [-4.27369398],
       [14.94794895]]), np.array([[-0.28125879],
       [ 4.11192799],
       [22.72546684]]), np.array([[-1.68087982],
       [-4.10198761],
       [35.21419461]]), np.array([[-5.74016205],
       [ 0.64679004],
       [21.72278309]]), np.array([[ 8.93381877],
       [-2.17176325],
       [24.13691881]]), np.array([[ 5.35852163],
       [-3.34518349],
       [21.85606131]]), np.array([[26.65562584],
       [-4.01257862],
       [57.71103432]]), np.array([[-7.64596786],
       [ 4.59896135],
       [25.11332959]]), np.array([[ 4.08492793],
       [ 6.70759027],
       [40.1045997 ]]), np.array([[-1.22426408],
       [-7.30309089],
       [34.4710443 ]]), np.array([[-7.02610462],
       [-7.8050421 ],
       [25.19658368]]), np.array([[17.32423041],
       [-5.98490178],
       [26.00839957]]), np.array([[ 7.2255217 ],
       [-6.88862504],
       [37.86997167]])))
MARKERSIZE = 0.057 # in meters

def pose_estimation(frame, arucoDict, mtxCoefficients, distCoefficients):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(arucoDict, parameters)

    # probably want to undistort the frame here. make this 'gray' if we want gray.
    # i'm not sure if making it gray actually helps, honestly.
    corrected = cv2.undistort(frame, mtxCoefficients, distCoefficients)
    corners, ids, rejected_img_pts = detector.detectMarkers(corrected)
    # ok we can't do refineDetectedMarkers because that's for boards only

    if len(corners) > 0:
        for i in range(0, len(ids)):
            rvec, tvec, markerPoints = cv2.aruco.estimatePoseSingleMarkers(corners[i],
                                                                           MARKERSIZE,
                                                                           mtxCoefficients,
                                                                           distCoefficients)

            # i don't know why corners is bundled in like 5 layers of array, but the [0][0] unwraps it
            # so we just pass an array of 4 x,y points
            drawDist(frame, corners[0][0], rvec[i], tvec[i])
            blastData(tvec[i], rvec[i])

            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, mtxCoefficients, distCoefficients, rvec, tvec, 0.05)

    return frame

# Fling pose data at the UDP port and hope they hear it.
# All units are meters. All positions are in the camera frame. All positions are also in a right-
# handed coordinate system, which is going to explode in Unity.
def blastData(tvec, rvec):
    # format our output
    out = "X=" + str(round(tvec[0][0], 5)) + " "
    out += "Y=" + str(round(tvec[0][1], 5)) + " "
    out += "Z=" + str(round(tvec[0][2], 5))

    # blast it
    SOCK.sendto(out.encode(), (UDP_IP, UDP_PORT))


def drawDist(image, corners, rvec, tvec):
    (tL, tR, bR, bL) = corners
    # convert everything to integers
    tL = (int(tL[0]), int(tL[1]))
    tR = (int(tR[0]), int(tR[1]))
    bR = (int(bR[0]), int(bR[1]))
    bL = (int(bL[0]), int(bL[1]))
    cX = int((tL[0] + bR[0]) / 2.0)
    cY = int((tL[1] + bR[1]) / 2.0)

    # calculate distance
    distance = np.linalg.norm(tvec[0])

    cv2.putText(image,
                f"distance: {distance}",
                (tL[0], tL[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2)
    cv2.putText(image,
                f"x: {round(tvec[0][0], 3)}, y: {round(tvec[0][1], 3)}, z: {round(tvec[0][2], 3)}",
                (bR[0], bR[1] - 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                BLUE,
                2)

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while cap.isOpened():
        ret, img = cap.read()

        if not ret:
            break

        output = pose_estimation(img, DICT, MATRIX, DIST)

        cv2.imshow('estimated pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

