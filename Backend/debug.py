import mediapipe
import os

print("--- DIAGNOSIS START ---")
try:
    print(f"File location: {mediapipe.__file__}")
except:
    print("Could not find file location.")

print(f"Folder contents: {os.listdir('.')}")
print("--- DIAGNOSIS END ---")