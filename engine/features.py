import os
import shlex
quote = shlex.quote
import sqlite3
import struct
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
from engine.command import speak
from engine.config import ASSISTANT_NAME
import pywhatkit as kit
import pvporcupine
import google.generativeai as genai
from engine.helper import extract_yt_term, remove_words

# Gemini configuration (Replace with your own API key)
GEMINI_API_KEY = "AIzaSyA19QdoztlbzrmK1ZAh58818rJbUgG6Rj8"
genai.configure(api_key=GEMINI_API_KEY)

con = sqlite3.connect("zia.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "web\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query_lower = query.lower()
    app_name = query_lower.strip()

    if app_name != "":
        try:
            cursor.execute('SELECT path FROM sys_command WHERE name IN (?)', (app_name,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening "+app_name)
                os.startfile(results[0][0])
            elif len(results) == 0: 
                cursor.execute('SELECT url FROM web_command WHERE name IN (?)', (app_name,))
                results = cursor.fetchall()
                if len(results) != 0:
                    speak("Opening "+app_name)
                    webbrowser.open(results[0][0])
                else:
                    speak("Opening "+app_name)
                    try:
                        os.system('start '+app_name)
                    except:
                        speak("not found")
        except:
            speak("some thing went wrong")

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
        porcupine=pvporcupine.create(keywords=["zia","alexa"])
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)
            keyword_index=porcupine.process(keyword)
            if keyword_index>=0:
                print("hotword detected")
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()

# Replace hugchat with Gemini
def chatBot(query):
    user_input = query.lower()
    try:
        # NOTE: Gemini-2.5-flash ajun release zala nahiye. Gemini-1.5-flash vapra.
        model = genai.GenerativeModel("models/gemini-1.5-flash") 
        response_obj = model.generate_content(user_input)
        response = response_obj.text
        if not response:
            response = "I could not get a response."
    except Exception as e:
        print("Gemini error:", e)
        response = "There was an error decoding the Gemini response."
        
    # Speak karnyapurvi response madhun '*' kadhun taka
    cleaned_response = response.replace("*", "")
    
    print("Original Response:", response) # Original response console var dakhva
    speak(cleaned_response) # Aata FAKT CLEAN KELELA RESPONSE BOLAYLA DYA
    
    return response

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)

def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    tapEvents(473.0, 2490.3)
    tapEvents(954.7, 2528.1)
    adbInput(mobileNo)
    tapEvents(396.5, 563.5)
    tapEvents(315.0, 2557.6)
    adbInput(message)
    tapEvents(1105.5, 1548.4)
    speak("message send successfully to "+name)
