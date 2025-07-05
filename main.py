import speech_recognition as sr
import pyttsx3
import requests
import json
import re
import os
import subprocess
import webbrowser
import threading
import time
import psutil
import datetime
import pyautogui
from pathlib import Path
import queue

# 🔐 Configuration
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://your-site-or-project.com",
    "X-Title": "Enhanced Jarvis Assistant"
}

class JarvisAssistant:
    def __init__(self):
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 3000
        self.recognizer.pause_threshold = 0.8
        self.recognizer.dynamic_energy_threshold = True
        
        try:
            self.mic = sr.Microphone()
            self.mic_available = True
        except:
            print("⚠️ Microphone not available - using text input only")
            self.mic_available = False
        
        # Conversation history
        self.conversation_history = []
        
        # Input mode
        self.voice_mode = False
        self.text_mode = True
        
        # Calibrate microphone if available
        if self.mic_available:
            self.calibrate_microphone()

    def calibrate_microphone(self):
        """Calibrate microphone for better recognition"""
        print("🎤 Calibrating microphone... Please stay quiet for 2 seconds.")
        try:
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print(f"✅ Microphone calibrated! Energy threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            print(f"❌ Microphone calibration failed: {e}")
            self.mic_available = False

    def speak(self, text):
        """Speak text and wait for completion"""
        print(f"🤖 Jarvis: {text}")
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")

    def get_text_input(self):
        """Get text input from user"""
        try:
            user_input = input("💬 You: ").strip()
            if user_input:
                print(f"📝 Input received: {user_input}")
                return user_input.lower()
            return None
        except KeyboardInterrupt:
            return "quit"
        except Exception as e:
            print(f"❌ Input error: {e}")
            return None

    def listen_for_speech(self):
        """Listen for speech input"""
        if not self.mic_available:
            return None
            
        try:
            with self.mic as source:
                print("🎤 Listening... (speak now)")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            print("🔍 Recognizing speech...")
            result = self.recognizer.recognize_google(audio, language='en-US')
            result_lower = result.lower().strip()
            print(f"📝 You said: '{result}'")
            return result_lower
            
        except sr.WaitTimeoutError:
            print("⏰ Speech timeout - no speech detected")
            return None
        except sr.UnknownValueError:
            print("❓ Could not understand speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected speech error: {e}")
            return None

    def get_input(self):
        """Get input from user (text or voice)"""
        if self.text_mode:
            return self.get_text_input()
        elif self.voice_mode and self.mic_available:
            return self.listen_for_speech()
        else:
            return self.get_text_input()

    def show_menu(self):
        """Show input mode menu"""
        print("\n" + "="*50)
        print("🎯 JARVIS ASSISTANT - INPUT MODE SELECTION")
        print("="*50)
        print("1. 📝 Text Input Mode (Default)")
        print("2. 🎤 Voice Input Mode")
        print("3. ❌ Exit")
        print("-"*50)

    def select_input_mode(self):
        """Let user select input mode"""
        while True:
            self.show_menu()
            choice = input("Choose input mode (1-3): ").strip()
            
            if choice == "1":
                self.text_mode = True
                self.voice_mode = False
                print("✅ Text input mode selected")
                break
            elif choice == "2":
                if self.mic_available:
                    self.text_mode = False
                    self.voice_mode = True
                    print("✅ Voice input mode selected")
                    break
                else:
                    print("❌ Microphone not available. Using text mode.")
                    self.text_mode = True
                    self.voice_mode = False
                    break
            elif choice == "3":
                print("👋 Goodbye!")
                return False
            else:
                print("❌ Invalid choice. Please select 1, 2, or 3.")
        
        return True

    def process_command(self, command):
        """Process user command"""
        if not command:
            return True
            
        cmd = command.strip()
        print(f"🎯 Processing: '{cmd}'")
        
        # Mode switching commands
        if "switch to text mode" in cmd or "text mode" in cmd:
            self.text_mode = True
            self.voice_mode = False
            self.speak("Switched to text input mode")
            return True
        elif "switch to voice mode" in cmd or "voice mode" in cmd:
            if self.mic_available:
                self.text_mode = False
                self.voice_mode = True
                self.speak("Switched to voice input mode")
            else:
                self.speak("Microphone not available. Staying in text mode.")
            return True
        
        # Exit commands
        elif any(word in cmd for word in ["exit", "quit", "stop", "bye", "goodbye"]):
            self.speak("Goodbye! Have a great day.")
            return False
        
        # System commands
        elif "shutdown" in cmd:
            self.speak("Shutting down the system in 5 seconds.")
            os.system("shutdown /s /t 5")
            return False
            
        elif "restart" in cmd:
            self.speak("Restarting the system in 5 seconds.")
            os.system("shutdown /r /t 5")
            return False
            
        elif "sleep" in cmd:
            self.speak("Putting the system to sleep.")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            
        # Application commands
        elif "chrome" in cmd:
            self.speak("Opening Chrome.")
            self.open_chrome()
            
        elif "firefox" in cmd:
            self.speak("Opening Firefox.")
            self.open_firefox()
            
        elif "notepad" in cmd:
            self.speak("Opening Notepad.")
            try:
                subprocess.Popen(["notepad"])
            except:
                self.speak("Could not open Notepad.")
            
        elif "calculator" in cmd:
            self.speak("Opening Calculator.")
            try:
                subprocess.Popen(["calc"])
            except:
                self.speak("Could not open Calculator.")
            
        elif "task manager" in cmd:
            self.speak("Opening Task Manager.")
            try:
                subprocess.Popen(["taskmgr"])
            except:
                self.speak("Could not open Task Manager.")
            
        # Search commands
        elif "search" in cmd and "google" in cmd:
            query = self.extract_search_query(cmd, ["search", "google", "for"])
            if query:
                self.speak(f"Searching Google for {query}")
                webbrowser.open(f"https://www.google.com/search?q={query}")
            else:
                self.speak("What should I search for?")
                
        elif "youtube" in cmd:
            query = self.extract_search_query(cmd, ["youtube", "search", "for"])
            if query:
                self.speak(f"Searching YouTube for {query}")
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
            else:
                self.speak("Opening YouTube")
                webbrowser.open("https://www.youtube.com")
                
        elif "wikipedia" in cmd:
            query = self.extract_search_query(cmd, ["wikipedia", "search", "for"])
            if query:
                self.speak(f"Searching Wikipedia for {query}")
                webbrowser.open(f"https://en.wikipedia.org/wiki/{query}")
            else:
                self.speak("What should I search on Wikipedia?")
        
        # Information commands
        elif "time" in cmd:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            self.speak(f"The time is {current_time}")
            
        elif "date" in cmd:
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.speak(f"Today is {current_date}")
            
        elif "system info" in cmd:
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.speak(f"CPU usage is {cpu_percent}%. Memory usage is {memory.percent}%")
            except:
                self.speak("Could not get system information.")
        
        # Volume controls
        elif "volume up" in cmd:
            self.speak("Increasing volume.")
            try:
                for _ in range(3):
                    pyautogui.press('volumeup')
            except:
                self.speak("Could not adjust volume.")
                
        elif "volume down" in cmd:
            self.speak("Decreasing volume.")
            try:
                for _ in range(3):
                    pyautogui.press('volumedown')
            except:
                self.speak("Could not adjust volume.")
                
        elif "mute" in cmd:
            self.speak("Muting volume.")
            try:
                pyautogui.press('volumemute')
            except:
                self.speak("Could not mute volume.")
        
        # Screenshot
        elif "screenshot" in cmd or "take screenshot" in cmd:
            self.speak("Taking a screenshot.")
            try:
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")
                self.speak("Screenshot saved as screenshot.png")
            except:
                self.speak("Could not take screenshot.")
        
        # File operations
        elif "open folder" in cmd:
            folder_name = self.extract_folder_name(cmd)
            if folder_name:
                self.open_folder(folder_name)
            else:
                self.speak("Which folder should I open?")
                
        elif "create folder" in cmd:
            folder_name = self.extract_folder_name(cmd)
            if folder_name:
                self.create_folder(folder_name)
            else:
                self.speak("What should I name the folder?")
                
        elif "list files" in cmd:
            self.list_files()
            
        # Help command
        elif "help" in cmd or "what can you do" in cmd:
            self.show_help()
        
        # AI chat for everything else
        else:
            print(f"🤖 Processing AI request: {cmd}")
            response = self.chat_with_ai(cmd)
            print(f"🤖 AI Response: {response}")
            self.speak(response)
            
        return True

    def extract_search_query(self, command, remove_words):
        """Extract search query from command"""
        query = command
        for word in remove_words:
            query = query.replace(word, "")
        return query.strip()

    def extract_folder_name(self, command):
        """Extract folder name from command"""
        folder_name = command.replace("open", "").replace("create", "").replace("folder", "").strip()
        return folder_name if folder_name else None

    def show_help(self):
        """Show available commands"""
        help_text = """Available commands:
        • System: shutdown, restart, sleep
        • Apps: chrome, firefox, notepad, calculator, task manager
        • Search: search google for [query], youtube [query], wikipedia [query]
        • Info: time, date, system info
        • Volume: volume up, volume down, mute
        • Files: open folder [name], create folder [name], list files
        • Other: screenshot, help, exit
        • AI: Ask me anything else!"""
        
        print(help_text)
        self.speak("I can help with system controls, opening apps, web searches, file management, and answer questions using AI.")

    def open_chrome(self):
        """Open Chrome browser"""
        try:
            subprocess.Popen(["chrome"])
        except:
            try:
                subprocess.Popen([r"C:\Program Files\Google\Chrome\Application\chrome.exe"])
            except:
                try:
                    subprocess.Popen([r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"])
                except:
                    self.speak("Chrome not found on this system.")

    def open_firefox(self):
        """Open Firefox browser"""
        try:
            subprocess.Popen(["firefox"])
        except:
            try:
                subprocess.Popen([r"C:\Program Files\Mozilla Firefox\firefox.exe"])
            except:
                self.speak("Firefox not found on this system.")

    def open_folder(self, folder_name):
        """Open a folder"""
        try:
            # Common folders mapping
            common_folders = {
                "documents": Path.home() / "Documents",
                "downloads": Path.home() / "Downloads",
                "desktop": Path.home() / "Desktop",
                "pictures": Path.home() / "Pictures",
                "music": Path.home() / "Music",
                "videos": Path.home() / "Videos"
            }
            
            folder_name_lower = folder_name.lower()
            
            if folder_name_lower in common_folders and common_folders[folder_name_lower].exists():
                self.speak(f"Opening {folder_name} folder")
                os.startfile(str(common_folders[folder_name_lower]))
            else:
                # Try as direct path
                folder_path = Path(folder_name)
                if folder_path.exists():
                    self.speak(f"Opening folder {folder_name}")
                    os.startfile(str(folder_path))
                else:
                    self.speak(f"Folder {folder_name} not found.")
        except Exception as e:
            print(f"Error opening folder: {e}")
            self.speak("Could not open folder.")

    def create_folder(self, folder_name):
        """Create a new folder"""
        try:
            os.makedirs(folder_name, exist_ok=True)
            self.speak(f"Created folder {folder_name}")
        except Exception as e:
            print(f"Error creating folder: {e}")
            self.speak("Could not create folder.")

    def list_files(self):
        """List files in current directory"""
        try:
            files = os.listdir('.')
            file_count = len(files)
            folder_count = len([f for f in files if os.path.isdir(f)])
            file_only_count = file_count - folder_count
            
            self.speak(f"There are {file_only_count} files and {folder_count} folders in the current directory.")
        except Exception as e:
            print(f"Error listing files: {e}")
            self.speak("Could not list files.")

    def chat_with_ai(self, prompt):
        """Chat with AI"""
        try:
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Keep last 6 messages for context
            if len(self.conversation_history) > 6:
                self.conversation_history.pop(0)
            
            data = {
                "model": "openrouter/cypher-alpha:free",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are Jarvis, an intelligent AI assistant. Give concise, helpful responses under 50 words. Be friendly and helpful."
                    }
                ] + self.conversation_history,
                "max_tokens": 100,
                "temperature": 0.7
            }
            
            response = requests.post(API_URL, headers=HEADERS, data=json.dumps(data))
            print(f"🔗 API Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                raw_answer = result["choices"][0]["message"]["content"]
                clean_answer = self.clean_response(raw_answer)
                print("🧠 AI Raw Response:", raw_answer)

                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": clean_answer})
                
                return clean_answer
            else:
                print(f"❌ API Error: {response.status_code}")
                return "Sorry, I couldn't process that request right now."
                
        except requests.exceptions.Timeout:
            return "The request timed out. Please try again."
        except Exception as e:
            print(f"❌ AI Error: {str(e)}")
            return "There was a problem with the AI service."

    def clean_response(self, text):
        """Clean AI response"""
        text = re.sub(r'\\n|\n|\r', ' ', text)
        text = re.sub(r'[*_#>\[\]{}|]', '', text)
        text = re.sub(r'\s{2,}', ' ', text)
        return text.strip()

    def run(self):
        """Main execution loop"""
        print("🤖 Enhanced Jarvis Assistant Starting...")
        
        # Select input mode
        if not self.select_input_mode():
            return
        
        mode_text = "Text Input Mode" if self.text_mode else "Voice Input Mode"
        print(f"\n✅ Starting in {mode_text}")
        self.speak(f"Jarvis Assistant is now active in {mode_text}.")
        
        if self.text_mode:
            print("\n📝 TEXT MODE - Type your commands")
            print("💡 You can switch modes by typing 'voice mode' or 'text mode'")
        else:
            print("\n🎤 VOICE MODE - Speak your commands")
            print("💡 You can switch modes by saying 'voice mode' or 'text mode'")
        
        print("🔹 Type/say 'help' for available commands")
        print("🔹 Type/say 'exit' to quit\n")
        
        try:
            while True:
                # Get input based on current mode
                user_input = self.get_input()
                
                if user_input:
                    if not self.process_command(user_input):
                        break
                else:
                    if self.text_mode:
                        print("⚠️ Please enter a command")
                    else:
                        print("⚠️ No speech detected or could not understand")
                        
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            self.speak("Jarvis shutting down. Goodbye!")

# 🚀 Main execution
if __name__ == "__main__":
    try:
        jarvis = JarvisAssistant()
        jarvis.run()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        input("Press Enter to exit...")