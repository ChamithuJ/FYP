from pose.audio import speak

CALIBRATION_STAGES = ["STAND STRAIGHT", "GO INTO A DEEP SQUAT"]
STABLE_FRAMES_REQUIRED = 25

MAX_INVALID_FRAMES = 5

calibration_data = {}
current_stage = 0
stable_frames = 0
calibrated = False

pose_was_valid = False
last_stage = None


def reset():
    global calibration_data, current_stage, stable_frames
    global calibrated, pose_was_valid, last_stage, invalid_frames

    calibration_data = {}
    current_stage = 0
    invalid_frames = 0
    stable_frames = 0
    calibrated = False
    pose_was_valid = False
    last_stage = None


def is_pose_valid(stage, knee_angle):
    if stage == "STAND STRAIGHT":
        return knee_angle > 160
    elif stage == "GO INTO A DEEP SQUAT":
        return knee_angle < 120
    return False

def process(knee_angle):
    global current_stage, stable_frames, calibrated
    global pose_was_valid, last_stage, invalid_frames

    if calibrated:
        return "CALIBRATED"

    stage = CALIBRATION_STAGES[current_stage]

    # print(
    #     f"[CALIB] stage={stage}, "
    #     f"knee_angle={int(knee_angle)}, "
    #     f"stable_frames={stable_frames}"
    # )

    # Announce stage when first entered
    if stage != last_stage:
        speak(stage)
        last_stage = stage
        stable_frames = 0
        pose_was_valid = False
        invalid_frames = 0  # reset invalid frames on new stage

    pose_valid = is_pose_valid(stage, knee_angle)

    if pose_valid:
        if not pose_was_valid:
            speak("Hold")
            stable_frames = 0

        stable_frames += 1
        invalid_frames = 0  # reset invalid frame count
        progress = int((stable_frames / STABLE_FRAMES_REQUIRED) * 100)

        if stable_frames >= STABLE_FRAMES_REQUIRED:
            calibration_data[stage] = knee_angle
            speak(f"{stage} captured")

            current_stage += 1
            stable_frames = 0
            pose_was_valid = False
            last_stage = None
            invalid_frames = 0

            if current_stage == len(CALIBRATION_STAGES):
                calibrated = True
                speak("Calibration complete. You can start exercising.")
                return "CALIBRATION COMPLETE"

        pose_was_valid = True
        return f"HOLD {progress}%"

    else:
        # Increment invalid frames instead of resetting immediately
        invalid_frames += 1
        if invalid_frames > MAX_INVALID_FRAMES:
            stable_frames = 0
            pose_was_valid = False

        return f"DO {stage}"
