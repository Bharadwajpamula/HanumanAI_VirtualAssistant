import speech_recognition as sr
import pyttsx3
import pywhatkit
import webbrowser
import os
import subprocess
import google.generativeai as genai
import re
import shutil

# Initialize recognizer and speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Setup Gemini
genai.configure(api_key="API key")  # Replace with your API key
model = genai.GenerativeModel("model")

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def open_website(command):
    match = re.search(r"open (.+)", command.lower())
    if match:
        site = match.group(1).strip().replace(" ", "")
        if not site.startswith("http"):
            url = f"https://{site}.com"
        else:
            url = site
        try:
            webbrowser.open(url)
            speak(f"Opening {site}")
        except Exception as e:
            speak(f"Couldn't open {site}")
    else:
        speak("Couldn't figure out the website to open.")

def open_application(command):
    match = re.search(r"open (.+)", command.lower())
    if match:
        app_name = match.group(1).strip().lower()
        try:
            if shutil.which(app_name):  # Check if app is in system PATH
                subprocess.Popen([app_name])
                speak(f"Opening {app_name}")
                return
            else:
                possible_paths = [
                    f"C:/Program Files/{app_name}/{app_name}.exe",
                    f"C:/Program Files (x86)/{app_name}/{app_name}.exe",
                    f"C:/Windows/System32/{app_name}.exe"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        os.startfile(path)
                        speak(f"Opening {app_name}")
                        return
                speak(f"App '{app_name}' not found.")
        except Exception as e:
            speak(f"Error launching {app_name}")
    else:
        speak("Couldn't figure out the app to open.")

def play_on_yt(command):
    if "play" in command:
        song = command.replace('play', '')
        pywhatkit.playonyt(song)
        speak(f"Playing {song.strip()}")

def ask_gemini(prompt):
    try:
        # Ask Gemini for a short, natural explanation
        refined_prompt = (
            f"Answer this like a friendly voice assistant, keep it within 1–2 paragraphs or around 100–200 words:\n\n{prompt}"
        )
        response = model.generate_content(refined_prompt)
        reply = response.text.strip()

        print("Gemini:", reply)
        speak(reply)
    except Exception as e:
        print("Gemini Error:", e)
        speak("Hmm, I had trouble answering that.")

def process_command(command):
    command = command.lower()
    if "open" in command:
        open_website(command)
        open_application(command)
    elif "play" in command:
        play_on_yt(command)
    else:
        ask_gemini(command)

# --- Main Loop ---
if __name__ == "__main__":
    speak("Hanuman assistant is ready.")
    while True:
        print("Listening for 'Hanuman' wake word...")
        speak("Listening for 'Hanuman' wake word...")

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)
                wake_word = recognizer.recognize_google(audio)

                if wake_word.lower() == "hanuman":
                    print("Wake word detected.")
                    speak("Yeah, what do you need?")

                    while True:
                        try:
                            with sr.Microphone() as source:
                                recognizer.adjust_for_ambient_noise(source)
                                print("Listening...")
                                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                                command = recognizer.recognize_google(audio)
                                print("User:", command)

                                if command.lower() in ["exit", "quit", "stop hanuman"]:
                                    speak("Goodbye!")
                                    exit()

                                process_command(command)
                                speak("Anything else?")
                        except sr.UnknownValueError:
                            print("Didn't catch that.")
                            speak("Didn't get that. Can you say it again?")
                        except Exception as err:
                            print(f"Error: {err}")
                            speak("Something went wrong.")

        except sr.UnknownValueError:
            continue
        except sr.RequestError as e:
            print(f"Request error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            speak("Goodbye!")
            break
