from gpiozero import PWMOutputDevice
from picamera2 import Picamera2
import cv2
import numpy as np
import time

# ----- Motor Setup -----
left_motor_forward = PWMOutputDevice(24)
left_motor_backward = PWMOutputDevice(23)
right_motor_forward = PWMOutputDevice(27)
right_motor_backward = PWMOutputDevice(22)

def stop():
    left_motor_forward.value = 0
    left_motor_backward.value = 0
    right_motor_forward.value = 0
    right_motor_backward.value = 0

def forward():
    left_motor_forward.value = 0.3
    left_motor_backward.value = 0
    right_motor_forward.value = 0.3
    right_motor_backward.value = 0

def instant_left():
    left_motor_forward.value = 0
    left_motor_backward.value = 0
    right_motor_forward.value = 0.25
    right_motor_backward.value = 0

def instant_right():
    left_motor_forward.value = 0.25
    left_motor_backward.value = 0
    right_motor_forward.value = 0
    right_motor_backward.value = 0
   
def backward():
    left_motor_forward.value = 0
    left_motor_backward.value = 0.3
    right_motor_forward.value = 0
    right_motor_backward.value = 0.3

# --- Color Detection ---
def detect_color(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Green color (instant left)
    lower_green = np.array([50, 125, 54])
    upper_green = np.array([83, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Red color (instant right)
    lower_red = np.array([0, 121, 100])
    upper_red = np.array([179, 255, 255])
    mask_red = cv2.inRange(hsv, lower_red, upper_red)

    if cv2.countNonZero(mask_green) > 500:
        return "green"
    elif cv2.countNonZero(mask_red) > 500:
        return "red"
    else:
        return "none"

# --- Camera Setup ---
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format":"RGB888", "size": (1280, 720)}))
picam2.start()
time.sleep(2)

try:
    while True:
        frame = picam2.capture_array()
        frame = cv2.resize(frame, (960, 720))  # Resize for display
        roi = frame[480:720, :]  # Bottom portion for line tracking

        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        lower_black = np.array([0, 0, 0])
        upper_black = np.array([179, 255, 150])
        mask_black = cv2.inRange(hsv, lower_black, upper_black)

        M = cv2.moments(mask_black)
        color = detect_color(roi)

        if color == "green":
            instant_left()
            time.sleep(1)

        elif color == "red":
            instant_right()
            time.sleep(1)

        elif M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            cv2.circle(frame, (cx, cy + 480), 5, (255, 0, 0), -1)

            if cx < 350:
                instant_left()
            elif cx > 610:
                instant_right()
            else:
                forward()
        else:
            forward()
            time.sleep(4)
            stop()
            break

          
        cv2.imshow("Line + Color Tracking", frame)

        if cv2.waitKey(1) == ord('q'):
            break

except KeyboardInterrupt:
    print("Stopped by user.")

finally:
    stop()
    cv2.destroyAllWindows()
