# 🖐️ Hand‑Gesture‑Controlled Runner

An **endless running game** that replaces keyboard input with **real‑time hand gestures** – no controller, no keyboard, just you and your webcam.

Move your hand left/right to steer, open your palm to jump, and make a fist to slide.  
The game uses **MediaPipe** for hand tracking and **Pygame** for rendering – all running locally on your machine.

![Gameplay Demo](assets/gameplay.gif) <!-- Optional: add a screenshot/gif later -->

---

## ✨ Features

- 🖐️ **Full hand‑gesture control** – steer, jump, and slide.
- 🧍 **Cute toy character** – with head, body, arms, hands, legs, and shoes.
- 🪟 **Resizable window** – click the maximize button for full screen.
- 🏆 **Persistent high score** – your best score is saved locally.
- 🔧 **Configurable** – tweak difficulty, gesture sensitivity, and visuals in `config.py`.
- 🐍 **Pure Python** – easy to understand and extend.

---

## 📋 Requirements

### Hardware
- **Webcam** – 720p recommended (works with most built‑in or USB webcams).
- **CPU** – Dual‑core 2.0+ GHz (MediaPipe runs on CPU).
- **RAM** – 4 GB or more.

### Software
- **Windows 10/11**, macOS, or Linux.
- **Python 3.10** – MediaPipe supports 3.10 on Windows (3.11+ may not work).
- The following Python packages (see `requirements.txt`):
  - `opencv-python`
  - `mediapipe==0.10.8` – **important**: newer versions use a different API.
  - `pygame`
  - `numpy`

---

##  Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/yared2124/hand_gesture_runner-game.git
cd hand_gesture_runner-game/hand_gesture_runner
```

### 2. Set up a virtual environment (recommended)

**Windows (Command Prompt)**:
```cmd
python -m venv venv
venv\Scripts\activate
```

**Windows (Git Bash)**:
```bash
python -m venv venv
source venv/Scripts/activate
```

**macOS/Linux**:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ **Troubleshooting**: If you get `AttributeError: module 'mediapipe' has no attribute 'solutions'`, you have installed MediaPipe ≥ 1.0.0.  
> **Fix**:  
> ```bash
> pip uninstall mediapipe -y
> pip install mediapipe==0.10.8
> ```

### 4. Run the game

```bash
python main.py
```

---

## 🎮 How to Play

| Your Hand Gesture | Action |
| :--- | :--- |
| Move hand **left/right** | Steer the avatar left/right |
| **Open palm** (all fingers up) | **Jump** over obstacles |
| **Fist** (all fingers folded) | **Slide** under obstacles |
| No hand detected | Avatar stays idle – but obstacles keep coming! |

**Keyboard shortcuts** (for testing or when camera isn't working):
- `ESC` – Quit the game.
- `R` – Restart after Game Over.

---

## 📊 Scoring

- **Score** increases by **1** each time an obstacle safely passes off‑screen.
- **Speed scaling** – obstacle speed gradually increases with your score.
- **High score** is saved in `highscore.txt` and displayed at the top.

---

## 🛠️ Configuration

All settings are in `config.py`. Here are some useful tweaks:

| Setting | What it does |
| :--- | :--- |
| `SCREEN_WIDTH`, `SCREEN_HEIGHT` | Game window size |
| `FPS_TARGET` | Frame rate (30 or 60) |
| `GRAVITY`, `JUMP_SPEED` | Jump physics |
| `SLIDE_DURATION` | How long slide lasts (in ms) |
| `OBSTACLE_SPEED_BASE` | Starting obstacle speed |
| `OBSTACLE_SPAWN_INTERVAL` | Frames between new obstacles (lower = more frequent) |
| `GESTURE_DEBOUNCE_MS` | Cooldown to prevent accidental jumps/slides |
| `SMOOTHING_ALPHA` | Steering responsiveness (0 = smooth, 1 = instant) |
| `SHOW_DEBUG_WINDOW` | `True` to see camera feed with hand landmarks, `False` to hide |
| `CAMERA_WIDTH`, `CAMERA_HEIGHT` | Camera resolution – lower for better performance |

---

## 📁 Project Structure

```
hand_gesture_runner/
│
├── config.py          # All configuration constants
├── hand_tracker.py    # MediaPipe vision module (hand tracking & gesture logic)
├── game_engine.py     # Pygame game loop (player, obstacles, physics, rendering)
├── main.py            # Entry point – glues everything together
├── requirements.txt   # Python dependencies
├── highscore.txt      # Created automatically – stores your best score
└── README.md          # This file
```

---

## 🐛 Troubleshooting

### `AttributeError: module 'mediapipe' has no attribute 'solutions'`
- You have MediaPipe **1.0.0** or newer installed.
- Downgrade to **0.10.8**:
  ```bash
  pip uninstall mediapipe -y
  pip install mediapipe==0.10.8
  ```

### Webcam not opening
- Ensure your camera is connected and not used by another app.
- On Windows: go to **Settings → Privacy & Security → Camera** and allow apps to access it.

### Game is slow / lags
- Reduce camera resolution (`CAMERA_WIDTH`, `CAMERA_HEIGHT`).
- Lower `FPS_TARGET` to 30.
- Turn off debug window (`SHOW_DEBUG_WINDOW = False`).

### Gestures not recognised reliably
- Ensure **good lighting** and a plain background.
- Keep your hand clearly visible from wrist to fingertips.
- Adjust `GESTURE_DEBOUNCE_MS` and `SMOOTHING_ALPHA` in `config.py`.

### The character floats in the air after jumping
- This has been fixed in the latest code. If you still see it, make sure you have the latest `game_engine.py` – the jump now clamps to ground.

---

## 🤝 Contributing

Contributions are welcome! If you find a bug or have an idea for improvement:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'Add amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

---

## 📄 License

This project is open‑source under the **MIT License**.  
You are free to use, modify, and distribute it.

---

## 🙏 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) – for the hand tracking pipeline.
- [Pygame](https://www.pygame.org/) – for the game engine.
- [OpenCV](https://opencv.org/) – for camera capture.

---

**Now go ahead, show your hand, and start running!** 🏃‍♂️💨  
*Every obstacle you dodge is one point closer to your new high score!*