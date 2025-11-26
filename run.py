import multiprocessing
import os
import subprocess
import time
import eel

# --- Main.py madhun import kelele functions ---
from engine.features import *
from engine.command import *
from engine.auth import recoganize
from engine.features import playAssistantSound
from engine.features import hotword

# ✅ Add Gemini API setup here
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Access Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=api_key)


# Process 1: Ha Jarvis cha main UI aani logic sambhalto
def startJarvis():
    """Ha function Eel UI start karto aani saglya JS calls la handle karto."""
    print("Process 1 (Zia UI) is starting...")
    
    # Eel la sanga ki web files 'web' folder madhe ahet
    eel.init("web")

    @eel.expose
    def init():
        print("Frontend connected. Starting initialization sequence.")
        
        # Skip device connection
        print("Skipping device connection...")
            
        eel.hideLoader()
        
        # Try face authentication if files exist, otherwise skip
        try:
            import os
            trainer_file = os.path.join('engine', 'auth', 'trainer', 'trainer.yml')
            haarcascade_file = os.path.join('engine', 'auth', 'haarcascade_frontalface_default.xml')
            
            if os.path.exists(trainer_file) and os.path.exists(haarcascade_file):
                print("Starting face authentication...")
                flag = recoganize.AuthenticateFace()
                if flag == 1:
                    eel.hideFaceAuth()
                    speak("Face authentication successful")
                    eel.hideFaceAuthSuccess()
                else:
                    speak("Face authentication failed, continuing in limited mode")
                    eel.hideFaceAuth()
                    eel.hideFaceAuthSuccess()
            else:
                print("Face authentication files not found, skipping...")
                eel.hideFaceAuth()
                eel.hideFaceAuthSuccess()
                
            # Initialize Gemini API with error handling
            try:
                load_dotenv()
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY not found in .env file")
                genai.configure(api_key=api_key)
                speak("Initialization complete. How can I help you today?")
            except Exception as e:
                print(f"Gemini API initialization warning: {e}")
                speak("Warning: Some features may be limited due to configuration issues.")
                
            eel.hideStart()
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            # Continue with minimal functionality
            eel.hideFaceAuth()
            eel.hideFaceAuthSuccess()
            eel.hideStart()
            speak("Starting in limited mode. Some features may not be available.")

    try:
        eel.start(
            'index.html',
            mode='edge',
            size=(1200, 700),
            port=8000
        )
    except (SystemExit, MemoryError, KeyboardInterrupt):
        print("Zia UI process has been closed.")


# Process 2: Ha "Zia" hotword aiknyacha kaam karto
def listenHotword():
    """Ha function continuously hotword aikat rahto."""
    print("Process 2 (Hotword Detection) is starting...")
    hotword()


# === Main Program itun start hoto ===
if __name__ == '__main__':
    print("Starting Jarvis Application...")

    p1 = multiprocessing.Process(target=startJarvis)
    p2 = multiprocessing.Process(target=listenHotword)

    p1.start()
    time.sleep(5)
    p2.start()

    p1.join()

    if p2.is_alive():
        print("UI closed. Terminating hotword process.")
        p2.terminate()
        p2.join()
    
    print("Zia application has stopped.")
