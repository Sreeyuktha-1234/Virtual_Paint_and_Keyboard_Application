import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
from time import sleep
import cvzone

# Button Class - Move this to the top of the code
class Button:
    def __init__(self, pos, text, size=[85, 85]):
        self.pos = pos
        self.size = size
        self.text = text

# Mediapipe Hands
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Paint Settings
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]
blue_index = green_index = red_index = yellow_index = 0
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0

# Keyboard Settings
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
        ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/"]]
finalText = ""
keyboard = Controller()
buttonList = [Button([100 * j + 50, 100 * i + 50], key) for i in range(len(keys)) for j, key in enumerate(keys[i])]

# Hand Detector
detector = HandDetector(detectionCon=0.8)

# Mode Toggle
mode = "Paint"  # Default mode

# Helper function to draw buttons
def drawAll(img, buttonList):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (button.pos[0], button.pos[1], button.size[0], button.size[1]), 20, rt=0)
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
    return img

# Video Capture
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while True:
    # Inside the while loop where you capture the frames
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img = detector.findHands(img)  # Detect hands
    
    # Get hand landmarks
    lmList = detector.findPosition(img)  # Corrected method call
    
    if lmList:  # Check if hands are detected
        # Paint Mode Logic
        fore_finger = (lmList[8][0], lmList[8][1])
        thumb = (lmList[4][0], lmList[4][1])
        cv2.circle(img, fore_finger, 5, (0, 255, 0), -1)

        if abs(thumb[1] - fore_finger[1]) < 30:  # Clear canvas gesture
            bpoints = [deque(maxlen=1024)]
            gpoints = [deque(maxlen=1024)]
            rpoints = [deque(maxlen=1024)]
            ypoints = [deque(maxlen=1024)]
            blue_index = green_index = red_index = yellow_index = 0

        elif fore_finger[1] <= 100:
            if 30 <= fore_finger[0] <= 110:
                bpoints = [deque(maxlen=1024)]
                gpoints = [deque(maxlen=1024)]
                rpoints = [deque(maxlen=1024)]
                ypoints = [deque(maxlen=1024)]
            elif 160 <= fore_finger[0] <= 240:
                colorIndex = 0  # Blue
            elif 290 <= fore_finger[0] <= 370:
                colorIndex = 1  # Green
            elif 420 <= fore_finger[0] <= 500:
                colorIndex = 2  # Red
            elif 545 <= fore_finger[0] <= 625:
                colorIndex = 3  # Yellow
        else:
            if colorIndex == 0:
                bpoints[blue_index].appendleft(fore_finger)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(fore_finger)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(fore_finger)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(fore_finger)
        
        # Drawing
        for points, color in zip([bpoints, gpoints, rpoints, ypoints], colors):
            for i in range(len(points)):
                for j in range(1, len(points[i])):
                    if points[i][j - 1] is None or points[i][j] is None:
                        continue
                    cv2.line(img, points[i][j - 1], points[i][j], color, 5)

    elif mode == "Keyboard":
        # Keyboard Mode Logic
        img = drawAll(img, buttonList)
        if lmList:
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                if x < lmList[8][0] < x + w and y < lmList[8][1] < y + h:
                    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 20, y + 65), cv2.FONT_HERSHEY_PLAIN, 4, (255, 255, 255), 4)
                    if detector.findDistance(8, 12, img, draw=False)[0] < 30:
                        keyboard.press(button.text)
                        finalText += button.text
                        sleep(0.15)

        cv2.rectangle(img, (50, 350), (700, 450), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, finalText, (60, 430), cv2.FONT_HERSHEY_PLAIN, 5, (255, 255, 255), 5)

    # Toggle Mode
    key = cv2.waitKey(1)
    if key == ord('m'):
        mode = "Keyboard" if mode == "Paint" else "Paint"
    elif key == ord('q'):
        break

    cv2.imshow("Combined Application", img)

cap.release()
cv2.destroyAllWindows()
