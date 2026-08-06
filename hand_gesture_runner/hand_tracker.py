"""
Vision Module: Hand tracking via MediaPipe and gesture extraction.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from config import (
    CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT,
    MIN_DETECTION_CONFIDENCE, WRIST_ID, FINGERTIP_IDS, PIP_IDS,
    HAND_SCALE_REFERENCE_ID, SMOOTHING_ALPHA, GESTURE_DEBOUNCE_MS,
    SHOW_DEBUG_WINDOW
)

class HandTracker:
    """Manages webcam capture, MediaPipe hand tracking, and gesture recognition."""

    def __init__(self):
        # Initialise MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=MIN_DETECTION_CONFIDENCE,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils

        # Open webcam
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam. Check camera connection.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        # Smoothing state
        self.smooth_x = 0.5          # Normalised X (0..1), start at centre
        self.last_gesture = 0        # 0=idle, 1=jump, 2=slide
        self.last_gesture_time = 0   # timestamp for debounce
        self.hand_detected = False

    def get_gesture_and_position(self):
        """
        Capture a frame, process it, and return (gesture_code, normalised_x, debug_frame).
        gesture_code: 0=idle, 1=jump, 2=slide
        normalised_x: float in [0, 1] (0=left, 1=right)
        debug_frame: annotated camera frame (or None if SHOW_DEBUG_WINDOW is False)
        """
        ret, frame = self.cap.read()
        if not ret:
            return 0, self.smooth_x, False, None

        # Mirror horizontally so left hand = left on screen
        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        gesture = 0
        norm_x = self.smooth_x
        detected = False
        debug_frame = frame.copy() if SHOW_DEBUG_WINDOW else None

        if results.multi_hand_landmarks:
            detected = True
            landmarks = results.multi_hand_landmarks[0]

            # Extract wrist and reference points
            wrist = landmarks.landmark[WRIST_ID]
            mid_mcp = landmarks.landmark[HAND_SCALE_REFERENCE_ID]

            # Scale-normalisation factor: palm height
            palm_height = abs(wrist.y - mid_mcp.y)
            if palm_height < 0.001:
                palm_height = 0.001   # avoid division by zero

            # --- Steering: Wrist X mapped to screen width ---
            raw_x = wrist.x   # MediaPipe x is in [0,1]
            # Apply exponential moving average smoothing
            self.smooth_x = (SMOOTHING_ALPHA * raw_x) + ((1 - SMOOTHING_ALPHA) * self.smooth_x)
            norm_x = np.clip(self.smooth_x, 0.0, 1.0)

            # --- Gesture: Open Palm vs Fist ---
            # Check if fingertips are ABOVE (y <) PIP joints (open palm)
            open_palm = True
            fist = True
            for tip_id, pip_id in zip(FINGERTIP_IDS, PIP_IDS):
                tip = landmarks.landmark[tip_id]
                pip = landmarks.landmark[pip_id]
                # Normalise by palm height to be scale-invariant
                tip_y_norm = (tip.y - wrist.y) / palm_height
                pip_y_norm = (pip.y - wrist.y) / palm_height

                if tip_y_norm >= pip_y_norm:   # not extended upward
                    open_palm = False
                if tip_y_norm <= pip_y_norm:   # not folded downward
                    fist = False

            # Debounce: prevent rapid toggling
            now = time.time() * 1000  # milliseconds
            if now - self.last_gesture_time > GESTURE_DEBOUNCE_MS:
                if open_palm:
                    gesture = 1   # Jump
                    self.last_gesture_time = now
                elif fist:
                    gesture = 2   # Slide
                    self.last_gesture_time = now
                else:
                    gesture = 0   # Idle / Running
            else:
                # Still in cooldown – keep previous gesture if still within cooldown
                # but if gesture was released, revert to idle
                if open_palm or fist:
                    # If the gesture is still held, we might want to keep it
                    # For simplicity, we'll just keep last_gesture
                    gesture = self.last_gesture if (now - self.last_gesture_time < GESTURE_DEBOUNCE_MS) else 0
                else:
                    gesture = 0

            self.last_gesture = gesture
            self.hand_detected = True

            # Draw landmarks on debug frame
            if SHOW_DEBUG_WINDOW and debug_frame is not None:
                self.mp_drawing.draw_landmarks(
                    debug_frame, landmarks, self.mp_hands.HAND_CONNECTIONS
                )
                # Also show gesture text
                gesture_text = ["IDLE", "JUMP", "SLIDE"][gesture]
                cv2.putText(debug_frame, f"Gesture: {gesture_text}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        else:
            # No hand detected: fall back to idle
            self.hand_detected = False
            gesture = 0

        return gesture, norm_x, detected, debug_frame

    def release(self):
        """Release camera and MediaPipe resources."""
        self.cap.release()
        self.hands.close()
        cv2.destroyAllWindows()