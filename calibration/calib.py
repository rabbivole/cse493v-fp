import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

i = 0
while True:
    ret, frame = cam.read()
    cv2.imshow('frame', frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    if key == ord('c'):
        cv2.imwrite("calib-" + str(i) + ".png", frame)
        i += 1

cv2.destroyAllWindows()