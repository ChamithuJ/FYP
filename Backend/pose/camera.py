import cv2
import mediapipe as mp
import numpy as np

from pose import calibration, squat_detector
from pose.audio import speak

from database import users_collection
from jose import jwt
from config import SECRET_KEY, ALGORITHM


mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

cap = None

mode = "idle"
running = False

# 🔐 store JWT token
current_token = None


def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))


def distance(a, b):
    return np.linalg.norm(a - b)


def extract_features(landmarks):
    l_sh = np.array([landmarks[11].x, landmarks[11].y])
    r_sh = np.array([landmarks[12].x, landmarks[12].y])
    l_hip = np.array([landmarks[23].x, landmarks[23].y])
    r_hip = np.array([landmarks[24].x, landmarks[24].y])
    l_knee = np.array([landmarks[25].x, landmarks[25].y])
    r_knee = np.array([landmarks[26].x, landmarks[26].y])
    l_ankle = np.array([landmarks[27].x, landmarks[27].y])
    r_ankle = np.array([landmarks[28].x, landmarks[28].y])
    l_foot = np.array([landmarks[31].x, landmarks[31].y])
    r_foot = np.array([landmarks[32].x, landmarks[32].y])

    left_knee_angle = calculate_angle(l_hip, l_knee, l_ankle)
    right_knee_angle = calculate_angle(r_hip, r_knee, r_ankle)
    left_hip_angle = calculate_angle(l_sh, l_hip, l_knee)
    right_hip_angle = calculate_angle(r_sh, r_hip, r_knee)
    left_ankle_angle = calculate_angle(l_knee, l_ankle, l_foot)
    right_ankle_angle = calculate_angle(r_knee, r_ankle, r_foot)

    spine_angle = (left_hip_angle + right_hip_angle) / 2.0

    mid_shoulder = (l_sh + r_sh) / 2.0
    mid_hip = (l_hip + r_hip) / 2.0
    vertical_pt = np.array([mid_hip[0], mid_hip[1] - 0.5])
    torso_lean = calculate_angle(mid_shoulder, mid_hip, vertical_pt)

    left_knee_lateral = abs(l_knee[0] - l_ankle[0])
    right_knee_lateral = abs(r_knee[0] - r_ankle[0])

    symmetry_score = abs(left_knee_angle - right_knee_angle) + abs(left_hip_angle - right_hip_angle)

    hip_depth = mid_hip[1]

    return [
        left_knee_angle, right_knee_angle, left_hip_angle, right_hip_angle,
        left_ankle_angle, right_ankle_angle, spine_angle, torso_lean,
        left_knee_lateral, right_knee_lateral, symmetry_score, hip_depth
    ]


def start_camera():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        print("Camera started")


def stop_camera():
    global running, mode, cap

    running = False
    mode = "idle"

    if cap is not None:
        cap.release()
        cap = None  # 🔥 VERY IMPORTANT

    print("Camera stopped")


def generate_frames():
    global mode, running, cap

    # if not cap.isOpened():
    #     cap = cv2.VideoCapture(0)

    start_camera()

    running = True

    while running:
        success, frame = cap.read()
        if not success:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        status = "NO BODY"

        if results.pose_landmarks:
            lm = results.pose_landmarks.landmark
            features = extract_features(lm)
            knee_angle = features[1]

            if mode == "calibration":
                result = calibration.process(knee_angle, lm)

                # 🔥 HANDLE NEW RETURN FORMAT
                if isinstance(result, dict):
                    status = result.get("status", "")

                    # ✅ AUTO SAVE CALIBRATION
                    if result.get("status") == "CALIBRATION COMPLETE":
                        if current_token:
                            try:
                                payload = jwt.decode(current_token, SECRET_KEY, algorithms=[ALGORITHM])
                                username = payload.get("sub")

                                users_collection.update_one(
                                    {"username": username},
                                    {"$set": {"calibration": result["data"]}}
                                )

                                print(f"✅ Calibration saved for {username}")

                            except Exception as e:
                                print("Token error:", e)
                else:
                    status = result

            elif mode == "exercise" and calibration.calibrated:
                status, reps = squat_detector.process(
                    knee_angle, features, calibration.calibration_data, speak
                )
                cv2.putText(frame, f"Reps: {reps}", (30, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

            mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        cv2.putText(frame, f"Status: {status}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)

        ret, buffer = cv2.imencode(".jpg", frame)
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")