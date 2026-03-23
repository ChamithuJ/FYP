from pose.audio import speak

CALIBRATION_STAGES = ["STAND STRAIGHT", "GO INTO A DEEP SQUAT"]
STABLE_FRAMES_REQUIRED = 25
MAX_INVALID_FRAMES = 5

calibration_data = {}
current_stage = 0
stable_frames = 0
calibrated = False
invalid_frames = 0
pose_was_valid = False
last_stage = None
visibility_warning_spoken = False  # To prevent TTS spam

def reset():
    global calibration_data, current_stage, stable_frames
    global calibrated, pose_was_valid, last_stage, invalid_frames
    global visibility_warning_spoken

    calibration_data = {}
    current_stage = 0
    invalid_frames = 0
    stable_frames = 0
    calibrated = False
    pose_was_valid = False
    last_stage = None
    visibility_warning_spoken = False

def is_pose_valid(stage, knee_angle):
    if stage == "STAND STRAIGHT":
        return knee_angle > 160
    elif stage == "GO INTO A DEEP SQUAT":
        return knee_angle < 120
    return False

def check_body_visibility(landmarks, threshold=0.5):
    """Checks if at least one side of the body is clearly visible (perfect for side profile)."""
    
    # Get the max visibility between the left and right side for each joint pair.
    # If you face right, the right joints will score high (e.g., 0.9) and left low (e.g., 0.1).
    # The max() ensures we only care about the side the camera can actually see.
    
    shoulder_vis = max(landmarks[11].visibility, landmarks[12].visibility)
    hip_vis = max(landmarks[23].visibility, landmarks[24].visibility)
    knee_vis = max(landmarks[25].visibility, landmarks[26].visibility)
    ankle_vis = max(landmarks[27].visibility, landmarks[28].visibility)
    
    # If any of the required body parts are completely out of frame, return False
    if min(shoulder_vis, hip_vis, knee_vis, ankle_vis) < threshold:
        return False
        
    return True 

def process(knee_angle, landmarks):
    global current_stage, stable_frames, calibrated
    global pose_was_valid, last_stage, invalid_frames
    global visibility_warning_spoken

    if calibrated:
        return "CALIBRATED"

  
    if not check_body_visibility(landmarks):
        stable_frames = 0
        pose_was_valid = False
        
       
        if not visibility_warning_spoken:
            speak("Please step back. Entire body must be visible.")
            visibility_warning_spoken = True
            
        return "BODY NOT VISIBLE"
    
  
    visibility_warning_spoken = False
  

    stage = CALIBRATION_STAGES[current_stage]

   
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
    