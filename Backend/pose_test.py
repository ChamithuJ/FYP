import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import json
import queue
import time

# ================= TTS SYSTEM (WINDOWS-SAFE) =================
speech_queue = queue.Queue()

engine = pyttsx3.init()
engine.setProperty("rate", 165)
engine.startLoop(False)

def speak(text):
    print("TTS:", text)
    speech_queue.put(text)

def process_speech():
    if not engine.isBusy() and not speech_queue.empty():
        engine.say(speech_queue.get())
    engine.iterate()

# ================= MediaPipe =================
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose = mp_pose.Pose(
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# ================= Helpers =================
def get_point(landmarks, index):
    lm = landmarks[index]
    return np.array([lm.x, lm.y])

def calculate_angle(a, b, c):
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

def is_pose_valid(stage, angle):
    if stage == "STAND STRAIGHT":
        return angle > 160
    elif stage == "GO INTO A DEEP SQUAT":
        return angle < 100
    return False

# ================= Calibration =================
CALIBRATION_STAGES = ["STAND STRAIGHT", "GO INTO A DEEP SQUAT"]
STABLE_FRAMES_REQUIRED = 25

calibration_data = {}
current_stage = 0
calibrated = False

instruction_spoken = False
stable_frame_count = 0
pose_was_valid = False

# ================= Exercise Tracking =================
rep_count = 0
squat_state = "UP"   # UP or DOWN

last_audio_time = {}
AUDIO_COOLDOWN = 2.0  # seconds

def speak_with_cooldown(text):
    now = time.time()
    if text not in last_audio_time or now - last_audio_time[text] > AUDIO_COOLDOWN:
        speak(text)
        last_audio_time[text] = now

# ================= Webcam =================
cap = cv2.VideoCapture(0)

print("Press C to start calibration")

# ================= Main Loop =================
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)

    status_text = "PRESS C TO CALIBRATE"

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark

        hip = get_point(lm, mp_pose.PoseLandmark.RIGHT_HIP.value)
        knee = get_point(lm, mp_pose.PoseLandmark.RIGHT_KNEE.value)
        ankle = get_point(lm, mp_pose.PoseLandmark.RIGHT_ANKLE.value)

        knee_angle = calculate_angle(hip, knee, ankle)

        # ---------- CALIBRATION ----------
        if not calibrated and current_stage < len(CALIBRATION_STAGES):
            stage = CALIBRATION_STAGES[current_stage]
            status_text = f"CALIBRATION {current_stage + 1}/2"

            if not instruction_spoken:
                speak(stage)
                instruction_spoken = True

            pose_valid = is_pose_valid(stage, knee_angle)

            if pose_valid:
                if not pose_was_valid:
                    stable_frame_count = 0
                    speak("Hold")

                stable_frame_count += 1
                progress = int((stable_frame_count / STABLE_FRAMES_REQUIRED) * 100)

                cv2.putText(frame, f"Stabilizing... {progress}%",
                            (30, 120), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, (0, 255, 0), 2)

                if stable_frame_count >= STABLE_FRAMES_REQUIRED:
                    calibration_data[stage] = knee_angle
                    speak(f"{stage} captured")

                    current_stage += 1
                    instruction_spoken = False
                    stable_frame_count = 0
                    pose_was_valid = False

                    if current_stage == len(CALIBRATION_STAGES):
                        calibrated = True
                        speak("Calibration complete. You can start exercising.")

                        with open("calibration.json", "w") as f:
                            json.dump(calibration_data, f, indent=4)
            else:
                stable_frame_count = 0

            pose_was_valid = pose_valid

        # ---------- EXERCISE MODE ----------
        elif calibrated:
            standing = calibration_data["STAND STRAIGHT"]
            deep = calibration_data["GO INTO A DEEP SQUAT"]

            rom = standing - deep
            tolerance = rom * 0.08

            if knee_angle <= deep + tolerance:
                status_text = "GOOD SQUAT"

                if squat_state == "UP":
                    squat_state = "DOWN"
                    # speak_with_cooldown("Good squat")

            elif knee_angle < standing - tolerance:
                status_text = "GO LOWER"
                speak_with_cooldown("Go lower")

            else:
                status_text = "STANDING"

                if squat_state == "DOWN":
                    squat_state = "UP"
                    rep_count += 1
                    # speak_with_cooldown(f"Rep {rep_count}")

        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # ---------- UI ----------
    cv2.putText(frame, f"Status: {status_text}", (30, 420),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.putText(frame, f"Reps: {rep_count}", (30, 460),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Squat Coach", frame)

    process_speech()

    key = cv2.waitKey(1)
    if key == ord("q"):
        break
    elif key == ord("c") and not calibrated:
        speak("Starting calibration")
        current_stage = 0
        instruction_spoken = False
        stable_frame_count = 0
        pose_was_valid = False

cap.release()
cv2.destroyAllWindows()
engine.endLoop()
