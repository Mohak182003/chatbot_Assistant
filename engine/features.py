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

# Gemini configuration - Load from environment variables
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable or use empty string if not found
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

# Configure Gemini with the API key
if GEMINI_API_KEY:
    try:
        # Initialize with the API key
        genai.configure(
            api_key=GEMINI_API_KEY,
            transport='rest',  # Try with REST transport if default fails
        )
        
        # Test the connection
        try:
            genai.list_models()
        except Exception as e:
            print(f"Warning: Could not connect to Gemini API: {str(e)}")
            
    except Exception as e:
        print(f"Error initializing Gemini: {str(e)}")
else:
    print("Warning: GEMINI_API_KEY not found in environment variables")

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
    if not query or query.strip() == "":
        error_msg = "I didn't catch that. Could you please repeat?"
        eel.DisplayMessage(error_msg)  # Show in UI
        return error_msg
        
    user_input = query.lower()
    
    # Handle specific greetings
    if any(greeting in user_input for greeting in ["hello zia", "hi zia", "hey zia"]):
        response = "I'm doing great, thank you for asking! How about you?"
        eel.DisplayMessage(response)  # Show in UI
        speak(response.replace("#", ""))  # Remove # before speaking
        return response
    
    # Show thinking message in UI
    eel.DisplayMessage("Thinking...")
    
    # Check if we have a valid API key
    if not GEMINI_API_KEY:
        error_msg = "Gemini API key is not configured. Please set it in the .env file."
        print(error_msg)
        eel.DisplayMessage(error_msg)  # Show in UI
        speak("I'm sorry, but I can't connect to the AI service right now. Please check my configuration.")
        return error_msg
    
    try:
        # Get list of available models
        try:
            available_models = genai.list_models()
            model_names = [m.name for m in available_models if 'generateContent' in m.supported_generation_methods]
            
            if not model_names:
                error_msg = "No suitable Gemini models found with generateContent support"
                print(error_msg)
                eel.DisplayMessage(error_msg)  # Show in UI
                speak("I'm sorry, but I can't find a suitable AI model right now.")
                return error_msg
                
            # Try to find a working model
            working_model = None
            response = None
            for model_name in model_names:
                try:
                    # Extract just the model name without the full path
                    short_name = model_name.split('/')[-1]
                    if short_name.startswith('gemini'):
                        model = genai.GenerativeModel(short_name)
                        response_obj = model.generate_content(user_input)
                        response = response_obj.text
                        if response:
                            working_model = short_name
                            break
                except Exception as e:
                    print(f"Tried {model_name} but got error: {str(e)}")
                    continue
            
            if not working_model or not response:
                error_msg = "Could not find a working Gemini model or get a valid response"
                print(error_msg)
                eel.DisplayMessage(error_msg)  # Show in UI
                speak("I'm having trouble connecting to the AI service right now.")
                return error_msg
                
            print(f"Using model: {working_model}")
            
            # Clean and process the response
            cleaned_response = response.replace("*", "").strip()
            
            # Display the response in the UI
            eel.DisplayMessage(cleaned_response)  # Show in UI
            
            # Speak the response after removing #
            speak(cleaned_response.replace("#", ""))
            
            return cleaned_response
            
        except Exception as e:
            error_msg = f"Error initializing Gemini: {str(e)}"
            print(error_msg)
            eel.DisplayMessage(error_msg)  # Show in UI
            speak("I'm having trouble connecting to the AI service right now.")
            return error_msg
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        speak("Sorry, I encountered an unexpected error. Please try again.")
        return error_msg

def makeCall(name, mobileNo):
    mobileNo = mobileNo.replace(" ", "")
    speak(f"Mobile calling is disabled. Would have called {name} at {mobileNo}")

def sendMessage(message, mobileNo, name):
    speak(f"Mobile messaging is disabled. Would have sent to {name} at {mobileNo}: {message}")
    speak("Message sending functionality requires mobile device connection which is currently disabled")

