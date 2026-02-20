from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pose.camera import generate_frames
from pose import calibration, squat_detector, camera
# from pose.audio import speak

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/video-feed")
def video_feed():
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

@app.post("/start-calibration")
def start_calibration():
    calibration.reset()
    camera.mode = "calibration"
    return {"status": "calibration started"}

@app.post("/start-exercise")
def start_exercise():
    squat_detector.reset()
    # speak(" You can start doing squats now. Stand straight with your feet shoulder width apart.")
    camera.mode = "exercise"
    return {"status": "exercise started"}
