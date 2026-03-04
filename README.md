# 🖱️ IP-Cam Virtual Mouse - MediaPipe Hand Tracking

A computer vision application that turns your smartphone camera into a wireless virtual mouse using Python, OpenCV, and Google's MediaPipe.

## 🏗️ Project Management & AI Collaboration

This project is a product of modern AI-assisted development. I served as the **System Architect and Prompt Engineer**, while Gemini AI generated the underlying code based on my logical flow. 

My architectural contributions to this project include:
* **Solving the "Distance Blindness":** Instructing the AI to calculate a dynamic distance ratio (using the wrist and middle-finger base as a reference) so that click gestures work flawlessly regardless of how close or far the hand is from the camera.
* **Sniper/Freeze Mode:** Designing the logic to stabilize the cursor when fingers get close to a click gesture, preventing unwanted jittering just before clicking.
* **Network Integration:** Routing the video feed via an IP Webcam stream instead of a standard local webcam for mobile flexibility.

## ✨ Key Features

* **Mobile as a Controller:** Uses your smartphone's camera via a local IP stream, allowing you to control your PC from across the room.
* **Dynamic Hand Scaling:** Left and right-click gestures automatically scale based on your hand's distance from the camera.
* **Smart Cursor Stabilization:** Implements a velocity-based smoothing algorithm. Fast hand movements move the cursor rapidly, while slow movements trigger a "sniper mode" for precise clicking.
* **Drag and Drop:** Supports holding the left click for dragging windows or items.

## 🛠️ Prerequisites & Setup

To run this project, you need to connect your smartphone and PC to the same Wi-Fi network.

1. **Smartphone Setup:**
   * Download an app like **IP Webcam** (Android) or **EpocCam** (iOS) on your phone.
   * Start the video server in the app and note the provided IP address (e.g., `http://192.168.1.X:8080/video`).
2. **PC Setup:**
   * Clone this repository.
   * Open the Python script and replace the `url` variable with your phone's IP address.
   * Install the required libraries:
        pip install opencv-python mediapipe pyautogui
     ```
3. **Run the script:**
     python virtual_mouse.py
How to Use (Gestures)
Move Cursor: Move your index and thumb fingers together around the screen.

Left Click / Drag: Pinch your Index Finger and Thumb together. Hold to drag.

Right Click: Pinch your Middle Finger and Thumb together.

Exit: Press the q key on your physical keyboard to terminate the program.
