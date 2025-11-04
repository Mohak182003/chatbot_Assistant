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
        subprocess.call([r'device.bat'])
        eel.hideLoader()
        speak("Ready for Face Authentication")
        
        flag = recoganize.AuthenticateFace()

        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Successful")
            eel.hideFaceAuthSuccess()
            speak("Hello, Welcome Sir, How can I Help You?")
            eel.hideStart()
            playAssistantSound()
        else:
            speak("Face Authentication Failed")

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
