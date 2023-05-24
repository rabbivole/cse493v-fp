import cv2
import cv2.aruco

cap = cv2.VideoCapture(0)
# care of https://stackoverflow.com/a/68790110
# note that turning the resolution up adds *significant* delay!
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
# lowering framerate does not seem to have any effect on this delay
# cap.set(cv2.CAP_PROP_FPS, 15)

arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
params = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(arucoDict, params)

def draw_markers(corners, ids, img):
    if len(corners) > 0:
        ids = ids.flatten()

        for (markerCorner, markerId) in zip(corners, ids):
            # always returned in tl, tr, br, bl order
            corners = markerCorner.reshape((4, 2))
            topLeft, topRight, bottomRight, bottomLeft = corners

            # convert x,y coord pairs to integers (from float, i assume?)
            topRight = (int(topRight[0]), int(topRight[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))

            cv2.line(img, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(img, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(img, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(img, bottomLeft, topLeft, (0, 255, 0), 2)

            # draw center
            c_x = int((topLeft[0] + bottomRight[0]) / 2.0)
            c_y = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(img, (c_x, c_y), 4, (0, 0, 255))

            # draw id
            cv2.putText(img, str(markerId), (topLeft[0], topLeft[1] - 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0))

def main():
    while True:
        ret, frame = cap.read()
        (corners, ids, rejected) = detector.detectMarkers(frame)
        draw_markers(corners, ids, frame)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    main()

