"""
Configuration constants for the hand-gesture runner game.
Adjust these to tune gameplay feel and gesture sensitivity.
"""

# ─── Display ────────────────────────────────────────────────
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS_TARGET = 60

# ─── Camera ──────────────────────────────────────────────────
CAMERA_INDEX = 0
CAMERA_WIDTH = 420
CAMERA_HEIGHT = 360
SHOW_DEBUG_WINDOW = True        # Set to False to hide camera feed

# ─── Player Physics ─────────────────────────────────────────
GRAVITY = 0.6
JUMP_SPEED = -12.0          # Negative = upward
SLIDE_DURATION = 500        # milliseconds
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_Y_GROUND = SCREEN_HEIGHT - PLAYER_HEIGHT - 50

# ─── Obstacles ──────────────────────────────────────────────
OBSTACLE_WIDTH = 30
OBSTACLE_HEIGHT = 40
OBSTACLE_SPEED_BASE = 5.0
OBSTACLE_SPAWN_INTERVAL = 120       # frames between spawns
OBSTACLE_MIN_GAP = 150              # pixels between obstacles

# ─── Gesture Recognition ────────────────────────────────────
GESTURE_DEBOUNCE_MS = 300           # cooldown after jump/slide
SMOOTHING_ALPHA = 0.3               # steering smoothing (0=no smoothing, 1=instant)
MIN_DETECTION_CONFIDENCE = 0.7
HAND_SCALE_REFERENCE_ID = 9         # Middle finger MCP for scale normalisation

# ─── Landmark IDs (MediaPipe) ──────────────────────────────
WRIST_ID = 0
FINGERTIP_IDS = [8, 12, 16, 20]     # Index, Middle, Ring, Pinky
PIP_IDS = [6, 10, 14, 18]           # Corresponding PIP joints

# ─── File Paths ─────────────────────────────────────────────
HIGH_SCORE_FILE = "highscore.txt"