import cv2
import cv2.aruco as aruco
import numpy as np

# https://www.youtube.com/watch?v=GEWoGDdjlSc
# pose estimation (i mean. kinda. it gives me an axis.)

BLUE = (255, 0, 0)
chosenDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
# doublecheck format on matrix/dist
# calculated camera intrinsic matrix coefficients, i think?
matrix = np.array([[657.10847519, 0., 644.30783951],
 [0., 657.96298689, 375.44091335],
 [0., 0., 1.]])
# calculated camera distortion coefficients, i think?
dist = np.array([[0.17608815, -0.26971785, -0.00138746, 0.00203728, 0.13184202]])


def aruco_display(corners, ids, rejected, image):
    if len(corners) > 0:
        ids = ids.flatten()

        for (markerCorner, markerID) in zip(corners, ids):
            corners = markerCorner.reshape((4,2))

            # returned in this order
            (tL, tR, bR, bL) = corners
            # convert everything to integers
            tL = (int(tL[0]), int(tL[1]))
            tR = (int(tR[0]), int(tR[1]))
            bR = (int(bR[0]), int(bR[1]))
            bL = (int(bL[0]), int(bL[1]))
            cX = int((tL[0] + bR[0]) / 2.0)
            cY = int((tL[1] + bR[1]) / 2.0)

            # do drawing, write ID, etc
            cv2.line(image, tL, tR, BLUE, 4)
            cv2.line(image, tR, bR, BLUE, 4)
            cv2.line(image, bR, bL, BLUE, 4)
            cv2.line(image, bL, tL, BLUE, 4)
            cv2.circle(image, (cX, cY), 4, (0, 0, 255))
            cv2.putText(image, str(markerID), (tL[0], tL[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            return image

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
                                                                           0.057,
                                                                           mtxCoefficients,
                                                                           distCoefficients)
            cv2.aruco.drawDetectedMarkers(frame, corners)
            cv2.drawFrameAxes(frame, mtxCoefficients, distCoefficients, rvec, tvec, 0.05)

    return frame

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    while cap.isOpened():
        ret, img = cap.read()

        if not ret:
            break

        output = pose_estimation(img, chosenDict, matrix, dist)

        cv2.imshow('estimated pose', output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

