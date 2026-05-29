# Raspberry Pi Camera-Based Line & Color Follower Robot

This repository contains the code for a camera-guided autonomous robot that runs on a Raspberry Pi. Instead of using standard infrared (IR) sensor arrays, this robot uses a single Raspberry Pi camera module and **OpenCV** to track a black path on the floor. It also detects green and red floor markers to trigger sharp, pre-programmed turns.

The hardware side is driven by the **gpiozero** library, which uses PWM (Pulse-Width Modulation) to control the speed and direction of the motors.

---

## 📂 Project Files

Here is the file structure of this project:

```text
.
├── main.py          # The main control loop, vision pipeline, and motor mapping
├── requirements.txt # Python package requirements
└── README.md        # This setup guide and explanation
```

---

## 🚀 Key Features

* **Camera-Based Navigation:** Captures high-res frames using the modern `picamera2` library and scales them down to `960x720` for speedy frame rates.
* **Centroid-Based Line Tracking:** Focuses on the bottom third of the camera frame (our Region of Interest) and computes image moments to locate the center of the black path.
* **Color Marker Detection:** Recognizes green and red cards or tape on the floor using HSV color masks, triggering sharp pivot turns.
* **PWM Motor Control:** Employs `gpiozero.PWMOutputDevice` for speed control (forward speed runs at 30% duty cycle, and turning pivots run at 25%).
* **Failsafe & Clean Exit:** Halts the motors safely if you hit `Ctrl + C` or press the `q` key. Also includes a failsafe that stops the robot if it loses the line track entirely.

---

## ⚙️ Hardware Setup

### What You'll Need
1. **Raspberry Pi:** A Raspberry Pi 3B+, 4B, or 5 running Raspberry Pi OS.
2. **Camera:** Any Raspberry Pi Camera Module that is compatible with the new `picamera2` stack (like the V2 or Camera Module 3).
3. **Chassis & Motors:** A standard 2WD robot chassis with two DC gear motors.
4. **Motor Driver:** An H-bridge motor driver (e.g., L298N, L293D, or TB6612FNG) wired to the Pi's GPIO pins.
5. **Power:** Separated power sources—one for the Raspberry Pi (like a power bank) and another battery pack for the motor driver to avoid power drop issues.

### GPIO Wiring Map

The motors are controlled via four GPIO pins connected to your H-bridge driver inputs:

| Component | What it does | GPIO Pin | Control Type | Speed (PWM Duty Cycle) |
| :--- | :--- | :---: | :---: | :---: |
| **Left Motor Forward** | Drives left wheel forward | **GPIO 24** | PWM Output | `0.30` (30%) |
| **Left Motor Backward** | Drives left wheel backward | **GPIO 23** | PWM Output | `0.30` (30%) |
| **Right Motor Forward** | Drives right wheel forward | **GPIO 27** | PWM Output | `0.30` (30%) |
| **Right Motor Backward** | Drives right wheel backward | **GPIO 22** | PWM Output | `0.30` (30%) |

---

## 🧠 How It Works

Here is a quick look at the logic inside the robot's main loop:

```mermaid
graph TD
    A[Grab Frame from PiCamera2] --> B[Resize Frame to 960x720]
    B --> C[Crop Bottom ROI: frame[480:720, :]]
    C --> D[Convert ROI to HSV Color Space]
    D --> E{Any Color Marker Detected?}
    
    E -- Green (>500 px) --> F[Pivot Left for 1.0s]
    E -- Red (>500 px) --> G[Pivot Right for 1.0s]
    
    E -- None --> H[Filter for Black Line & Calculate Moments]
    H --> I{Is Black Line Visible?}
    
    I -- Yes --> J[Find Centroid CX]
    I -- No --> K[Drive Forward for 4s, Stop, and Exit]
    
    J --> L{Evaluate Centroid Position}
    L -- CX < 350 --> M[Pivot Left]
    L -- CX > 610 --> N[Pivot Right]
    L -- 350 <= CX <= 610 --> O[Drive Forward]
    
    F & G & M & N & O --> P[Show GUI window and check for 'q' key]
    P --> A
```

### 1. Prepping the Frame
The script starts the camera stream and resizes each frame to `960x720`. To make sure the robot only looks at the road immediately in front of it (and ignores background clutter), it crops out a **Region of Interest (ROI)** using the bottom third of the image:
`roi = frame[480:720, :]`

### 2. Searching for Color Markers
First, the ROI is converted to the HSV (Hue, Saturation, Value) color space. It scans the cropped frame for green and red markers using these HSV ranges:
* **Green:** Lower `[50, 125, 54]`, Upper `[83, 255, 255]`
* **Red:** Lower `[0, 121, 100]`, Upper `[179, 255, 255]`

If the script counts more than **500 matching pixels** in either color mask:
* **Green:** Pivots left (`instant_left()`) for **1 second** by running the right motor forward and stopping the left.
* **Red:** Pivots right (`instant_right()`) for **1 second** by running the left motor forward and stopping the right.

### 3. Tracking the Black Line
If there are no colored markers, it isolates the black track using this HSV range:
* **Black:** Lower `[0, 0, 0]`, Upper `[179, 255, 150]`

It calculates the centroid ($C_x$, $C_y$) of the black mask using OpenCV image moments:
$$C_x = \frac{M_{10}}{M_{00}}$$

* **Line is to the Left ($C_x < 350$):** Pivots left to correct course.
* **Line is to the Right ($C_x > 610$):** Pivots right to correct course.
* **Line is Centered ($350 \le C_x \le 610$):** Drives straight forward with both motors set to `0.30` speed.

### 4. What if the Line Disappears?
If no black pixels are detected ($M_{00} = 0$), the robot enters a failsafe state: it drives straight forward for **4 seconds**, stops completely, and exits the loop.

---

## 🛠️ Software & Setup

This code is written to run directly on Raspberry Pi OS using Python 3 and the modern `picamera2` API.

### Getting Dependencies Ready
Make sure your system packages are up to date, then install the required libraries:
```bash
# Update package list
sudo apt update

# Install OpenCV, NumPy, GPIO Zero, and PiCamera2 packages
sudo apt install -y python3-opencv python3-numpy python3-gpiozero python3-picamera2
```

---

## 💻 Running the Code on Raspberry Pi (Thonny IDE)

**Thonny IDE** is the default pre-installed Python IDE on Raspberry Pi OS. Running your robot tracking script through it is simple:

### Step 1: Physical Assembly
1. **Connect the Camera:** Plug your Raspberry Pi Camera Module into the camera port (CSI interface) on your Pi using the ribbon cable.
2. **Wire the H-Bridge:** Connect your motor driver inputs to the Pi's GPIO pins:
   * GPIO 24 & 23 to the Left Motor inputs.
   * GPIO 27 & 22 to the Right Motor inputs.
3. **Common Ground:** Make sure the ground (GND) pin of your motor driver's power supply is connected to a Ground pin on the Raspberry Pi's GPIO header. **This is critical** for the PWM signals to work.

### Step 2: Open Thonny IDE
1. Boot up your Raspberry Pi and access the desktop (either directly on a monitor or via VNC).
2. Click the Raspberry Pi icon in the top-left corner of the screen.
3. Hover over **Programming** and select **Thonny Python IDE**.

### Step 3: Load the Code
1. In Thonny, click the **Open** folder icon in the toolbar.
2. Navigate to your project folder and open `main.py`.

### Step 4: Run the Script
1. Place the robot at the starting point of your black line track.
2. Click the green **Run** button (the Play icon) in Thonny's toolbar, or press **F5** on your keyboard.
3. The camera will take about 2 seconds to warm up, and then a live window titled `"Line + Color Tracking"` will pop up on your Pi's desktop. 
4. You will see a **blue dot** on the screen showing the detected center of the line, and the robot's wheels will begin to drive!

### Step 5: How to Stop
* **Inside Thonny:** Click the red **Stop** button (the Stop sign icon) in the toolbar.
* **On Screen:** Click onto the visual preview window and press the **`q`** key on your keyboard.
* **Emergency:** If the robot runs off the track and cannot find any black pixels, the script will automatically drive forward for 4 seconds and shut down both motors for safety.

---

## ⚠️ Limitations & Notes

Here are a few things to keep in mind if you are running this track setup:

* **Blocking Delay on Colors:** When the robot spots a red or green marker, it calls `time.sleep(1)`. This completely freezes the main loop for a full second. During this time, the camera feed won't update, and the robot won't adjust its steering if it goes off course.
* **Lighting Vulnerability:** The HSV color ranges are hardcoded. If you move the track to a different room, turn on a bright light, or cast heavy shadows, the robot might lose the track or mistake standard background elements for colored markers.
* **No-Look Failsafe:** If the robot loses the line, it drives blind for 4 seconds. If there's an obstacle or wall right at the end of your track, it will drive straight into it.
* **Hardware Bound:** Because this uses `gpiozero` and `picamera2` directly, the code cannot be easily run or simulated on standard Windows or Mac computers without mocking those hardware libraries.
