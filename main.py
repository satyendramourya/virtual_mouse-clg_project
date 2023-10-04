import cv2
import os
from cvzone.HandTrackingModule import HandDetector
# import numpy as np
import pyautogui

# Turning off the failsafe
pyautogui.FAILSAFE = False


# Variables
folderPath = "slides"
imageNumber = 0

screen_width, screen_height = pyautogui.size()
width, height = screen_width, screen_height
gestureThreshold = 300

# camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

ws, hs = int(420 * 1), int(303 * 1)

# Get the list of presentation images.
pathImages = sorted(os.listdir(folderPath), key=len)

# Hand detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Button action to change slides slowly:
buttonPressed = False
buttonCounter = 0
buttonDelay = 15

# Variables to track the hand's position in the previous frame
prevX, prevY = 0, 0

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    pathFullImage = os.path.join(folderPath, pathImages[imageNumber])
    imgCurrent = cv2.imread(pathFullImage)

    hands, img = detector.findHands(img)

    if hands and buttonPressed is False:
        hand = hands[0]
        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        lmList = hand['lmList']

        dx = (cx - prevX) * 5
        dy = (cy - prevY) * 5
        prevX, prevY = cx, cy

        # print("dx - ", dx)    slide forward and backward
        if fingers == [1, 1, 1, 1, 1]:
            if dx > 150:  # Swipe right
                if imageNumber > 0:
                    buttonPressed = True
                    imageNumber -= 1
            elif dx < -150:  # Swipe left
                if imageNumber < len(pathImages) - 1:
                    buttonPressed = True
                    imageNumber += 1

            print("image number - ", imageNumber)
        # else:
        #     print("(0,0,0,0,0)")
        #     print("do nothing")

        if fingers == [0, 1, 0, 0, 0]:  # Gesture 3 - Show pointer
            # Calculate the new cursor position based on the hand's movement
            new_x = pyautogui.position().x + dx
            new_y = pyautogui.position().y + dy

            # Make sure the cursor stays within the screen bounds
            new_x = min(max(new_x, 0), screen_width)
            new_y = min(max(new_y, 0), screen_height)

            # Move the cursor to the new position
            pyautogui.moveTo(new_x, new_y,  duration=0.1)

        if fingers == [0, 1, 1, 0, 0]:
            pyautogui.click(interval=0.1)
            print("clicked")

        if fingers == [0, 1, 1, 1, 0]:
            print("scrolling - ", dy)
            pyautogui.scroll(dy)

    if buttonPressed:
        buttonCounter += 1
        if buttonCounter > buttonDelay:
            buttonCounter = 0
            buttonPressed = False

    imageSmall = cv2.resize(img, (ws, hs))
    h, w, _ = imageSmall.shape
    imgCurrent[0:h, w - ws:w] = imageSmall

    cv2.imshow("Image Current", imgCurrent)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
