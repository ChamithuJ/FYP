import cv2
import mediapipe as mp
import numpy as np

from pose import calibration, squat_detector
from pose.audio import speak


mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

cap = cv2.VideoCapture(0)

mode = "idle"  # idle | calibration | exercise

def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine, -1, 1)))

def distance(a, b):
    return np.linalg.norm(a - b)


def generate_frames():
    global mode

    while True:
        success, frame = cap.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        status = "NO BODY"

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark

            hip = np.array([lm[24].x, lm[24].y])
            knee = np.array([lm[26].x, lm[26].y])
            ankle = np.array([lm[28].x, lm[28].y])

            knee_angle = calculate_angle(hip, knee, ankle)

            if mode == "calibration":
                status = calibration.process(knee_angle)

            elif mode == "exercise" and calibration.calibrated:
                status, reps = squat_detector.process(
                    knee_angle, calibration.calibration_data, speak
                )
                cv2.putText(frame, f"Reps: {reps}", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.putText(frame, f"Status: {status}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        

        ret, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")
