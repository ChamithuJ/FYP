import time
import joblib
import numpy as np
import os
import warnings

warnings.filterwarnings("ignore", message="X does not have valid feature names")

rep_count = 0
state = "UP"
last_feedback_time = 0

PROFESSIONAL_DEPTH_THRESHOLD = 90  
PROFESSIONAL_EXTENSION_THRESHOLD = 160 



current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "..", "ml_traning", "squat_rf_model.pkl")

# LOAD YOUR AI MODEL HERE!
try:
    
    squat_model = joblib.load(model_path)
    print("AI Model loaded successfully into squat_detector!")
except Exception as e:
    print(f"Warning: Could not load model. Error: {e}")
    squat_model = None

def reset():
    global rep_count, state, last_feedback_time
    rep_count = 0
    state = "UP"
    last_feedback_time = 0

def process(knee_angle, features, calibration_data, speak):
    global rep_count, state, last_feedback_time

    calibrated_standing = calibration_data.get("STAND STRAIGHT", 170)
    calibrated_deep = calibration_data.get("GO INTO A DEEP SQUAT", 70)

    standing_threshold = max(PROFESSIONAL_EXTENSION_THRESHOLD, calibrated_standing - 10)
    
    # 1. STANDING UP PHASE
    if knee_angle > standing_threshold:
        if state == "DOWN":
            state = "UP"
            rep_count += 1
            speak(f"Rep {rep_count}")
        return "STANDING", rep_count

    # 2. REACHING THE BOTTOM (The perfect time to use the AI!)
    if knee_angle <= max(PROFESSIONAL_DEPTH_THRESHOLD, calibrated_deep + 10):
        if state == "UP":
            state = "DOWN"
            
           
            if squat_model is not None:
                prediction = squat_model.predict([features])[0]
                
                # Mapped exactly to your Kaggle Dataset Labels!
                if prediction == 0:
                    pass # 0 = Correct Squat (No correction needed)
                elif prediction == 1:
                    trigger_feedback("Try to go a bit deeper", speak) # 1 = Shallow squat
                elif prediction == 2:
                    trigger_feedback("Keep your back straight!", speak) # 2 = Forward lean
                elif prediction == 3:
                    trigger_feedback("Don't push your knees too far forward", speak) # 3 = Knees caving in
                elif prediction == 4:
                    trigger_feedback("Keep your heels on the ground!", speak) # 4 = Heels off ground
                elif prediction == 5:
                    trigger_feedback("Keep your body balanced!", speak) # 5 = Asymmetric squat
            # -----------------------------------

        return "DEEP SQUAT", rep_count

    # 3. INTERMEDIATE PHASE
    elif state == "UP" and knee_angle < 140:
        return "DESCENDING", rep_count

    return "IN MOTION", rep_count

def trigger_feedback(message, speak_func):
    global last_feedback_time
    current_time = time.time()
    
    # Prevent spamming the TTS engine (wait 3 seconds between feedback)
    if current_time - last_feedback_time > 3:
        speak_func(message)
        last_feedback_time = current_time