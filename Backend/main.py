from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from jose import jwt
from datetime import datetime, timedelta

from database import client, db, users_collection
from pose.camera import generate_frames
from pose import calibration, squat_detector, camera

from passlib.context import CryptContext

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#  JWT CONFIG
from config import SECRET_KEY, ALGORITHM

ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔹 Create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ------------------ STARTUP ------------------

@app.on_event("startup")
async def startup_event():
    try:
        client.admin.command('ismaster')
        print("MongoDB connected successfully!")
        print("Database:", db.name)
    except Exception as e:
        print("❌ Failed to connect:", e)


# ------------------ VIDEO ------------------

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
    camera.mode = "exercise"
    return {"status": "exercise started"}


@app.post("/stop-camera")
def stop_camera():
    camera.stop_camera()
    return {"status": "camera stopped"}


# ---------------- AUTH ----------------

@app.post("/signup")
def signup(user: dict):
    existing_user = users_collection.find_one({"username": user["username"]})

    if existing_user:
        raise HTTPException(status_code=400, detail="Username exists")

    hashed_password = pwd_context.hash(user["password"])

    users_collection.insert_one({
        "username": user["username"],
        "password": hashed_password,
        "calibration": None
    })

    return {"message": "User created"}


@app.post("/login")
def login(user: dict):
    db_user = users_collection.find_one({"username": user["username"]})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not pwd_context.verify(user["password"], db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    token = create_access_token({"sub": db_user["username"]})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# 🔥 IMPORTANT: store token for camera stream
@app.post("/set-token")
def set_token(data: dict):
    token = data.get("token")

    if not token:
        raise HTTPException(status_code=400, detail="Token missing")

    camera.current_token = token
    return {"message": "Token set"}




def save_calibration_to_db(calibration_data):
    username = camera.current_token  # or decode JWT if you prefer

    users_collection.update_one(
        {"username": username},
        {"$set": {"calibration": calibration_data}}
    )



@app.post("/logout")
def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

   

    return {"message": "Logged out"}