import cv2
import mediapipe as mp
import numpy as np
import time
from typing import Tuple, Optional
import config

class HandTracker:
    def __init__(self):
        self.cap = cv2.VideoCapture(config.CAMERA_INDEX)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAMERA_HEIGHT)

        if not self.cap.isOpened():
            raise RuntimeError(f"Error: Camera index {config.CAMERA_INDEX} could not be opened.")

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE
        )

        self.last_jump_time = 0.0
        self.last_slide_time = 0.0
        self.smoothed_x: Optional[float] = None
        self.last_valid_timestamp = time.time()

    def process_frame(self) -> Tuple[int, float, Optional[np.ndarray]]:
        """
        Processes a single frame from the webcam.
        Returns:
            gesture_code: 0 = RUNNING/IDLE, 1 = JUMP, 2 = SLIDE
            normalized_x: Horizontal coordinate in range [0.0, 1.0]
            debug_frame: OpenCV BGR frame rendered with landmark annotations
        """
        success, frame = self.cap.read()
        if not success:
            return 0, 0.5, None

        # FR-CAP-03: Horizontal Flip for natural mirroring
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        # Convert to RGB for MediaPipe processing
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture_code = 0  # Default to RUNNING
        raw_x = 0.5

        if results.multi_hand_landmarks:
            self.last_valid_timestamp = time.time()
            hand_landmarks = results.multi_hand_landmarks[0]

            # Convert normalized MediaPipe coordinates into pixel coordinates
            lm_list = [[int(lm.x * w), int(lm.y * h)] for lm in hand_landmarks.landmark]

            # FR-LM-03: Wrist position (Landmark 0) used for continuous lateral control
            raw_x = lm_list[0][0] / float(w)

            # FR-GS-02: Exponential Moving Average (EMA) to eliminate hand jitter
            if self.smoothed_x is None:
                self.smoothed_x = raw_x
            else:
                self.smoothed_x = (config.SMOOTHING_ALPHA * raw_x) + ((1.0 - config.SMOOTHING_ALPHA) * self.smoothed_x)

            # --- FR-LM-01 & FR-GS: Gesture Classification ---
            tip_ids = [8, 12, 16, 20]   # Index, Middle, Ring, Pinky Tips
            pip_ids = [6, 10, 14, 18]   # Corresponding PIP joints

            # Determine finger extension state (True = extended, False = curled)
            extended_states = [lm_list[tip][1] < lm_list[pip][1] for tip, pip in zip(tip_ids, pip_ids)]

            now = time.time() * 1000.0  # Convert to milliseconds

            # Open Palm Detection (JUMP)
            if all(extended_states):
                if (now - self.last_jump_time) > config.GESTURE_DEBOUNCE_MS:
                    gesture_code = 1
                    self.last_jump_time = now

            # Fist Detection (SLIDE)
            elif not any(extended_states):
                if (now - self.last_slide_time) > config.GESTURE_DEBOUNCE_MS:
                    gesture_code = 2
                    self.last_slide_time = now

            # Visual debug rendering
            mp.solutions.drawing_utils.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
            )
        else:
            # Neutral fallback when hand is out of view for > 1 sec (FR-HT-03)
            if self.smoothed_x is None:
                self.smoothed_x = 0.5

        # Clamp normalized position to [0.0, 1.0]
        final_x = float(np.clip(self.smoothed_x, 0.0, 1.0))
        return gesture_code, final_x, frame

    def release(self):
        """Releases hardware resources (FR-CAP-04)."""
        if self.cap.isOpened():
            self.cap.release()