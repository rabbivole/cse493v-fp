import numpy as np
import cv2

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

dark_green = np.uint8([[[42, 125, 0]]])
lt_green = np.uint8([[198, 255, 70]])

while True:
    _, image = cam.read()
    blurred = cv2.GaussianBlur(image, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    lower_green_hsv = np.array([50, 125, 60])
    upper_green_hsv = np.array([90, 255, 255])

    mask = cv2.inRange(hsv, lower_green_hsv, upper_green_hsv)
    mask = cv2.erode(mask, None, iterations=2) # clean up mask a bit, remove holes, etc
    mask = cv2.dilate(mask, None, iterations=2)
    result = cv2.bitwise_and(image, image, mask=mask)

    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(contours) > 0:
        c = max(contours, key=cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        m = cv2.moments(c)
        center = (int(m["m10"] / m["m00"]), int(m["m01"] / m["m00"])) # what even

        if radius > 10:
            cv2.circle(image, (int(x), int(y)), int(radius), (255, 0, 255), 2)
            cv2.circle(image, center, 5, (0, 0, 255), -1)
    cv2.imshow("balls lol", image)
    if cv2.waitKey(20) & 0xFF == 27:
        break
cv2.destroyAllWindows()