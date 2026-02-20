import time

rep_count = 0
state = "UP"
last_feedback_time = 0


PROFESSIONAL_DEPTH_THRESHOLD = 90  # Degrees (Parallel or below)
PROFESSIONAL_EXTENSION_THRESHOLD = 160 # Degrees (Legs straight)

def reset():
    global rep_count, state, last_feedback_time
    rep_count = 0
    state = "UP"
    last_feedback_time = 0

def process(knee_angle, calibration_data, speak):
    global rep_count, state, last_feedback_time

    # Get user specific calibration
    calibrated_standing = calibration_data.get("STAND STRAIGHT", 170)
    calibrated_deep = calibration_data.get("GO INTO A DEEP SQUAT", 70)

    # 1. CHECK STANDING (RESET PHASE)
    # We use the max of professional vs calibrated to ensure they actually straighten their legs
    standing_threshold = max(PROFESSIONAL_EXTENSION_THRESHOLD, calibrated_standing - 10)
    
    if knee_angle > standing_threshold:
        if state == "DOWN":
            state = "UP"
            rep_count += 1
            speak(f"Rep {rep_count}")
        return "STANDING", rep_count

   # the squat is considered perfect if the knee angle is at or below the professional depth threshold, regardless of calibration
    if knee_angle <= PROFESSIONAL_DEPTH_THRESHOLD:
        if state == "UP":
            state = "DOWN"
            # speak("Perfect depth")
        return "PERFECT SQUAT", rep_count

    # if the squat is below the user's calibrated depth but above the professional threshold, we give feedback to go lower for better form
    elif knee_angle <= (calibrated_deep + 10):
        if state == "UP":
            state = "DOWN"
          
            if calibrated_deep > PROFESSIONAL_DEPTH_THRESHOLD:
                trigger_feedback("Go lower for better form", speak)
            else:
                speak("")
        return "GOOD SQUAT", rep_count

    # 3. INTERMEDIATE PHASE (Going down but not deep enough)
    elif state == "UP" and knee_angle < 140:
        trigger_feedback("Go Lower", speak)
        return "GO LOWER", rep_count

    return "DESCENDING", rep_count

def trigger_feedback(message, speak_func):
   
    global last_feedback_time
    current_time = time.time()
    
    
    if current_time - last_feedback_time > 2.5:
        speak_func(message)
        last_feedback_time = current_time