import cv2
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import mediapipe as mp
import time
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Create a list to store the selected images
selected_images = []
current_image_index = 0

# Turning off the failsafe
pyautogui.FAILSAFE = False

# Define a cooldown variable for presentation control
presentationCooldown = 5  # Adjust the value as needed (in frames)

# Initialize the cooldown counter
cooldownCounter = 0

# Initialize initial hand position
initial_hand_x = 0
initial_hand_y = 0



def open_file():
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        for file_path in file_paths:
            image = Image.open(file_path)
            image.thumbnail((900, 700))
            selected_images.append(ImageTk.PhotoImage(image))

        show_image(current_image_index)


def show_image(index):
    if 0 <= index < len(selected_images):
        img_label.config(image=selected_images[index])
        img_label.image = selected_images[index]


def next_image():
    global current_image_index
    if current_image_index < len(selected_images) - 1:
        current_image_index += 1
        show_image(current_image_index)


def prev_image():
    global current_image_index
    if current_image_index > 0:
        current_image_index -= 1
        show_image(current_image_index)


# Initialize the hand detection module
# x1 = y1 = x2 = y2 = 0


# Camera Setup
width, height = 640, 480  # Set the desired camera feed resolution
cap = cv2.VideoCapture(0)

detector = HandDetector(detectionCon=0.8)

# Create a GUI window
root = tk.Tk()
root.title("Hand Detection App")

# Set fixed column widths for sidebar and main section
root.grid_columnconfigure(0, minsize=250)
root.grid_columnconfigure(1, weight=1)

# Create a left sidebar using the grid layout manager
sidebar = tk.Frame(root, bg="lightgray")
sidebar.grid(row=0, column=0, sticky="nsew")

# Create a button to open a file picker in the sidebar
open_button = tk.Button(sidebar, text="Select Images", command=open_file)
open_button.pack(pady=10)

# Create a section in the top left corner of the sidebar with a specific width and height
section_frame = tk.Frame(sidebar, bg="white", width=width, height=height)
section_frame.pack(padx=10, pady=10, anchor="nw")

# Create a Canvas to display the video feed
canvas = tk.Canvas(section_frame, width=width, height=height)
canvas.pack()

# Create a section to display the selected image in the main section
image_section = tk.Frame(root)
image_section.grid(row=0, column=1, sticky="nsew")

img_label = tk.Label(image_section)
img_label.pack(fill=tk.BOTH, expand=True)

# Create buttons to navigate between images in the main section
prev_button = tk.Button(image_section, text="Previous", command=prev_image)
prev_button.pack(side=tk.LEFT, padx=10)
next_button = tk.Button(image_section, text="Next", command=next_image)
next_button.pack(side=tk.LEFT, padx=10)

# Make the rows expandable
root.grid_rowconfigure(0, weight=1)


def get_frame():
    global initial_hand_x, initial_hand_y, cooldownCounter
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)  # Mirror the frame for a more intuitive experience
    hands, frame = detector.findHands(frame)
    if hands:
        hand = hands[0]

        fingers = detector.fingersUp(hand)
        cx, cy = hand['center']
        # lmlist = hand['lmList']

        if fingers != [0,0,0,0,0]:
            dx = (cx - initial_hand_x)*5
            dy = (cy - initial_hand_y)*5
            initial_hand_x, initial_hand_y = cx,cy

        # Presentation control
        if fingers == [1, 1, 1, 1, 1]:
            if cooldownCounter == 0:  # Check if cooldown is over
                if dx > 150:  # Swipe right
                    next_image()  # Go to the next image
                    cooldownCounter = presentationCooldown  # Set cooldown
                elif dx < -150:  # Swipe left
                    prev_image()  # Go to the previous image
                    cooldownCounter = presentationCooldown  # Set cooldown

        # Hand pointer
        if fingers == [0, 1, 0, 0, 0]:
            new_x = pyautogui.position().x + dx
            new_y = pyautogui.position().y + dy
            # new_x = min(max(new_x, 0), screen_width)
            # new_y = min(max(new_y, 0), screen_height)
            pyautogui.moveTo(new_x, new_y, duration=0.1)

        # Mouse click
        if fingers == [0, 1, 1, 0, 0]:
            pyautogui.click(interval=0.1)
            print("clicked")
            time.sleep(0.5)  # Wait for 0.5 seconds after clicking

        # Mouse scroll
        if fingers == [0, 1, 1, 1, 0]:
            print("scrolling - ", dy)
            scroll_factor = 2  # Adjust this value to control scrolling speed
            pyautogui.scroll(dy * scroll_factor)

        # Volume control
        # if fingers == [1, 1, 1, 0, 0]:
        #     # Hand detector for volume control
        #     my_hands = mp.solutions.hands.Hands()
        #     drawing_utils = mp.solutions.drawing_utils

        #     frame_height, frame_width, _ = frame.shape
        #     rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        #     output = my_hands.process(rgb_image)
        #     hands = output.multi_hand_landmarks

        #     if hands:
        #         for hand in hands:

        #             drawing_utils.draw_landmarks(frame, hand)
        #             landmarks = hand.landmark
        #             for id, landmark in enumerate(landmarks):
        #                 x = int(landmark.x * frame_width)
        #                 y = int(landmark.y * frame_height)
        #                 if id == 8:
        #                     cv2.circle(img=frame, center=(x, y), radius=8, color=(0, 255, 255), thickness=3)
        #                     x1 = x
        #                     y1 = y
        #                 if id == 4:
        #                     cv2.circle(img=frame, center=(x, y), radius=8, color=(0, 0, 255), thickness=3)
        #                     x2 = x
        #                     y2 = y
        #             dist = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 4
        #             cv2.line(frame, (x1, y1), (x2, y2), color=(0, 255, 0), thickness=5)
        #             if dist > 30:
        #                 pyautogui.press("volumeup")
        #                 pyautogui.press("volumedown")
        #             else:
        #                 pyautogui.press("volumedown")

    cooldownCounter = max(0, cooldownCounter - 1)

    if frame is not None:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, image=img, anchor=tk.NW)
        canvas.img = img
        canvas.after(10, get_frame)


# Start capturing and displaying the video feed
get_frame()

# Run the Tkinter main loop
root.mainloop()

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
