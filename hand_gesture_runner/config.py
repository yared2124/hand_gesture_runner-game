# System & Screen Display Settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
FPS_TARGET = 60

# Gesture Thresholds & Feature Parameters (NFR-ACC, FR-GS)
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7
GESTURE_DEBOUNCE_MS = 300      # 300 ms cooldown to prevent jump/slide flickering
SMOOTHING_ALPHA = 0.3          # Exponential Moving Average factor for steering

# Physics & Player Mechanics (FR-PM)
GRAVITY = 1.2
JUMP_SPEED = -20
SLIDE_DURATION_MS = 600        # Duration of duck/slide state
PLAYER_NORMAL_WIDTH = 50
PLAYER_NORMAL_HEIGHT = 70
PLAYER_SLIDE_HEIGHT = 35

# Obstacle & Scoring Parameters (FR-OB, FR-SC)
OBSTACLE_BASE_SPEED = 7
OBSTACLE_SPAWN_INTERVAL_MS = 1400
SCORE_FILE = "highscore.txt"

# Color Palette (RGB)
COLOR_BG = (25, 28, 36)
COLOR_PLAYER = (0, 230, 153)
COLOR_OBSTACLE_JUMP = (255, 75, 75)   # Red: Jump over
COLOR_OBSTACLE_SLIDE = (255, 180, 0)  # Amber: Duck under
COLOR_TEXT = (240, 240, 240)
COLOR_HUD_ACCENT = (0, 180, 216)