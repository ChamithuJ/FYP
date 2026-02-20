import pyttsx3
import queue
import threading
import sys

# Try to import pythoncom (Windows specific)
try:
    import pythoncom
except ImportError:
    pythoncom = None

# Queue for TTS messages
speech_queue = queue.Queue()

def speak(text: str):
    """Add text to the TTS queue"""
    speech_queue.put(text)
    print(f"TTS queued: {text}")

def audio_worker():
    """Dedicated TTS thread with Windows COM safety"""
    
   
    if pythoncom:
        pythoncom.CoInitialize()

    while True:
        text = speech_queue.get()
        if text:
            try:
                # 2. Re-initialize engine per utterance to clear internal buffers
                engine = pyttsx3.init()
                engine.setProperty("rate", 165)
                
                engine.say(text)
                engine.runAndWait()
                engine.stop()
                
                # 3. Explicitly cleanup engine reference
                del engine
                
            except Exception as e:
                print(f"TTS error on '{text}':", e)
        
        speech_queue.task_done()

# Start TTS worker thread at import time
threading.Thread(target=audio_worker, daemon=True).start()