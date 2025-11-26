import pyttsx3
import speech_recognition as sr
import eel
import time

def speak(text):
    text = str(text)
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices') 
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', 174)
    eel.DisplayMessage(text)
    engine.say(text)
    eel.receiverText(text)
    engine.runAndWait()


def takecommand(timeout=3, phrase_time_limit=5):
    r = sr.Recognizer()
    
    # Adjust these parameters for better recognition
    r.energy_threshold = 3000  # Adjust based on your environment (lower for more sensitivity)
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    
    print("\nListening... (speak now)")
    eel.DisplayMessage("Listening...")
    
    try:
        with sr.Microphone() as source:
            # Adjust for ambient noise
            r.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                # Listen with shorter timeouts
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                print("Recognizing...")
                eel.DisplayMessage("Recognizing...")
                
                # Try Google Web Speech API
                try:
                    query = r.recognize_google(audio, language='en-in')
                    print(f"You said: {query}")
                    eel.DisplayMessage(query)
                    return query.lower().strip()
                    
                except sr.UnknownValueError:
                    print("Google Speech Recognition could not understand audio")
                    return ""
                    
                except sr.RequestError as e:
                    print(f"Could not request results from Google Speech Recognition service; {e}")
                    return ""
                
            except sr.WaitTimeoutError:
                print("No speech detected within the timeout period.")
                return ""
                
    except OSError as e:
        print(f"Microphone error: {e}")
        print("Please check if your microphone is properly connected.")
        eel.DisplayMessage("Microphone not found")
        return ""
        
    except Exception as e:
        print(f"Unexpected error in speech recognition: {e}")
        return ""
    
    return ""


@eel.expose
def allCommands(message=1):

#   query = takecommand() this query is getting message from mic
    if message == 1:
        query = takecommand() 
        print(query)
        eel.senderText(query)
    else:
#   eel.senderText(query) this query is getting message from  chatbox
        query = message
        eel.senderText(query)
    
    try:
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)
        
        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if(contact_no != 0):
                speak("Which mode you want to use whatsapp or mobile")
                preferance = takecommand()
                print(preferance)

                if "mobile" in preferance:
                    if "send message" in query or "send sms" in query: 
                        speak("what message to send")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("please try again")
                elif "whatsapp" in preferance:
                    message = ""
                    if "send message" in query:
                        message = 'message'
                        speak("what message to send")
                        query = takecommand()
                                        
                    elif "phone call" in query:
                        message = 'call'
                    else:
                        message = 'video call'
                                        
                    whatsApp(contact_no, query, message, name)

        else:
            from engine.features import chatBot
            chatBot(query)
    except:
        print("error")
    
    eel.ShowHood()
    