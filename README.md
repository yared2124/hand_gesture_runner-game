# 🖐️ Hand‑Gesture‑Controlled Runner

An **endless running game** that replaces keyboard input with **real‑time hand gestures** – no controller, no keyboard, just you and your webcam.

Move your hand left/right to steer, open your palm to jump, and make a fist to slide. The game uses **MediaPipe** for hand tracking and **Pygame** for rendering, all running locally on your machine.

---

## ✨ Features

- 🎮 **Full hand‑gesture control** – steer, jump, and slide.
- 🖥️ **Real‑time feedback** – live camera debug overlay with hand landmarks.
- 📈 **Dynamic scoring** – score increases as you dodge obstacles; speed ramps up the longer you survive.
- 🏆 **Persistent high score** – your best score is saved locally and displayed every session.
- 🔧 **Configurable** – tweak difficulty, gesture sensitivity, and visuals in `config.py`.
- 🐍 **Python‑based** – easy to understand and extend.

---

## 📋 Requirements

### Hardware
- Webcam (720p recommended)
- CPU: Dual‑core 2.0+ GHz (MediaPipe runs on CPU)
- RAM: 4+ GB

### Software
- **Windows 10/11**, macOS, or Linux
- **Python 3.10** (MediaPipe works best with 3.10 on Windows)
- Dependencies listed in `requirements.txt`

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/your-username/hand_gesture_runner.git
cd hand_gesture_runner
```

### 2. Set up a virtual environment (recommended)
```bash
python -m venv venv
source venv/Scripts/activate    # On Windows (Git Bash)
# or: venv\Scripts\activate     # On Windows (Command Prompt)
# On macOS/Linux: source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

> **⚠️ Important**: MediaPipe 1.0.0 changed its API and won't work with this code.  
> The `requirements.txt` pins the correct version (0.10.8).  
> If you already installed a newer version, fix it with:
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
| No hand detected | Avatar stays idle – safe, but obstacles keep coming! |

---

## 📊 Scoring System

- **Score** increases by **1 point** every time an obstacle safely passes off the left side of the screen.
- **Speed scaling**: The longer you survive, the faster obstacles move. Speed gradually increases as your score climbs, making the game progressively harder.
- **High score** is automatically saved to `highscore.txt` in the project folder and displayed at the top of the screen each session.
- **Game Over**: If you collide with an obstacle, the game ends. Press `R` to restart and try to beat your high score!

---

## 🛠️ Configuration

All tunable parameters are in `config.py`.  
You can adjust:

| Setting | What it does |
| :--- | :--- |
| `SCREEN_WIDTH`, `SCREEN_HEIGHT` | Game window size |
| `FPS_TARGET` | Frame rate (30 or 60) |
| `GRAVITY`, `JUMP_SPEED` | Jump physics |
| `SLIDE_DURATION` | How long the slide lasts (in ms) |
| `OBSTACLE_SPEED_BASE` | Starting obstacle speed |
| `OBSTACLE_SPAWN_INTERVAL` | Frames between new obstacles (lower = more frequent) |
| `GESTURE_DEBOUNCE_MS` | Cooldown to prevent accidental jumps/slides |
| `SMOOTHING_ALPHA` | Steering responsiveness (0 = smooth, 1 = instant) |
| `SHOW_DEBUG_WINDOW` | `True` to see camera feed with landmarks, `False` to hide |

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

### "Module 'mediapipe' has no attribute 'solutions'"
You installed MediaPipe 1.0.0. Downgrade:
```bash
pip uninstall mediapipe -y
pip install mediapipe==0.10.8
```

### Webcam not opening
- Ensure your camera is connected and not used by another app.
- On Windows, check **Settings → Privacy & Security → Camera** and allow access for apps.

### Game lags or runs slowly
- Reduce camera resolution in `config.py` (`CAMERA_WIDTH`, `CAMERA_HEIGHT`).
- Set `FPS_TARGET` to 30 instead of 60.
- Turn off the debug window (`SHOW_DEBUG_WINDOW = False`).

### Gestures not recognised reliably
- Ensure good lighting and a plain background.
- Adjust `GESTURE_DEBOUNCE_MS` to avoid accidental triggers.
- The hand should be clearly visible from wrist to fingertips.

### Score not saving
- Check that you have write permissions in the project folder.
- The file `highscore.txt` will be created automatically.

---

## 📄 License

This project is open‑source and available under the **MIT License**. Feel free to use, modify, and distribute it.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new features, bug fixes, or improvements, please open an issue or submit a pull request.

---

## 🙏 Acknowledgements

- [MediaPipe](https://mediapipe.dev/) – for the hand tracking pipeline.
- [Pygame](https://www.pygame.org/) – for the game engine.
- [OpenCV](https://opencv.org/) – for camera capture.

---

**Now go ahead, show your hand, and start running!** 🏃‍♂️💨  
*Every obstacle you dodge is one point closer to your new high score!*
