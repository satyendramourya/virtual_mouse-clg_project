import cv2
import os
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import mediapipe as mp
import time

# Turning off the failsafe
pyautogui.FAILSAFE = False

# Variables
folderPath = "slides"
imageNumber = 0

screen_width, screen_height = pyautogui.size()
width, height = screen_width, screen_height
gestureThreshold = 300

# Camera Setup
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

ws, hs = int(420 * 1), int(303 * 1)

# Get the list of presentation images.
pathImages = sorted(os.listdir(folderPath), key=len)

# Hand detector for presentation control
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Hand detector for volume control
my_hands = mp.solutions.hands.Hands()
drawing_utils = mp.solutions.drawing_utils

x1 = y1 = x2 = y2 = 0

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

        # Presentation control
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

        # Hand pointer
        if fingers == [0, 1, 0, 0, 0]:
            new_x = pyautogui.position().x + dx
            new_y = pyautogui.position().y + dy
            new_x = min(max(new_x, 0), screen_width)
            new_y = min(max(new_y, 0), screen_height)
            pyautogui.moveTo(new_x, new_y, duration=0.1)

        # Mouse click
        if fingers == [0, 1, 1, 0, 0]:
            pyautogui.click(interval=0.1)
            print("clicked")
            time.sleep(1)  # Wait for 2 seconds after clicking

        # Mouse scroll
        if fingers == [0, 1, 1, 1, 0]:
            print("scrolling - ", dy)
            pyautogui.scroll(dy)

        if fingers == [1, 1, 1, 0, 0]:
            # Volume control
            frame_height, frame_width, _ = img.shape
            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            output = my_hands.process(rgb_image)
            hands = output.multi_hand_landmarks

            if hands:
                for hand in hands:
                    drawing_utils.draw_landmarks(img, hand)
                    landmarks = hand.landmark
                    for id, landmark in enumerate(landmarks):
                        x = int(landmark.x * frame_width)
                        y = int(landmark.y * frame_height)
                        if id == 8:
                            cv2.circle(img=img, center=(x, y), radius=8, color=(0, 255, 255), thickness=3)
                            x1 = x
                            y1 = y
                        if id == 4:
                            cv2.circle(img=img, center=(x, y), radius=8, color=(0, 0, 255), thickness=3)
                            x2 = x
                            y2 = y
                    dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 4
                    cv2.line(img, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=5)
                    if dist > 30:
                        pyautogui.press("volumeup")
                    else:
                        pyautogui.press("volumedown")

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


