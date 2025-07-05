from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
import threading
import time
# Import your existing JarvisAssistant class
from main import JarvisAssistant

app = Flask(__name__)
CORS(app)

# Initialize Jarvis
jarvis = JarvisAssistant()

@app.route('/')
def index():
    return render_template('jarvis_ui.html')

@app.route('/api/process_command', methods=['POST'])
def process_command():
    try:
        data = request.json
        command = data.get('command', '')
        
        if not command:
            return jsonify({'error': 'No command provided'}), 400
        
        # Process the command using your existing logic
        response = handle_command(command)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

def handle_command(command):
    """
    Handle commands using your existing Jarvis logic
    """
    cmd = command.lower().strip()
    
    try:
        # Time command
        if "time" in cmd:
            import datetime
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        # Date command
        elif "date" in cmd:
            import datetime
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}"
        
        # System info command
        elif "system info" in cmd:
            try:
                import psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                return f"CPU usage: {cpu_percent}%, Memory usage: {memory.percent}%"
            except:
                return "Could not get system information"
        
        # Application commands
        elif "chrome" in cmd:
            threading.Thread(target=jarvis.open_chrome).start()
            return "Opening Chrome browser..."
        
        elif "firefox" in cmd:
            threading.Thread(target=jarvis.open_firefox).start()
            return "Opening Firefox browser..."
        
        elif "notepad" in cmd:
            import subprocess
            threading.Thread(target=lambda: subprocess.Popen(["notepad"])).start()
            return "Opening Notepad..."
        
        elif "calculator" in cmd:
            import subprocess
            threading.Thread(target=lambda: subprocess.Popen(["calc"])).start()
            return "Opening Calculator..."
        
        elif "task manager" in cmd:
            import subprocess
            threading.Thread(target=lambda: subprocess.Popen(["taskmgr"])).start()
            return "Opening Task Manager..."
        
        # Search commands
        elif "search" in cmd and "google" in cmd:
            query = jarvis.extract_search_query(cmd, ["search", "google", "for"])
            if query:
                import webbrowser
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return f"Searching Google for: {query}"
            return "What would you like to search for?"
        
        elif "youtube" in cmd:
            query = jarvis.extract_search_query(cmd, ["youtube", "search", "for"])
            if query:
                import webbrowser
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                return f"Searching YouTube for: {query}"
            else:
                import webbrowser
                webbrowser.open("https://www.youtube.com")
                return "Opening YouTube..."
        
        # Volume controls
        elif "volume up" in cmd:
            try:
                import pyautogui
                for _ in range(3):
                    pyautogui.press('volumeup')
                return "Volume increased"
            except:
                return "Could not adjust volume"
        
        elif "volume down" in cmd:
            try:
                import pyautogui
                for _ in range(3):
                    pyautogui.press('volumedown')
                return "Volume decreased"
            except:
                return "Could not adjust volume"
        
        elif "mute" in cmd:
            try:
                import pyautogui
                pyautogui.press('volumemute')
                return "Volume muted"
            except:
                return "Could not mute volume"
        
        # Screenshot
        elif "screenshot" in cmd:
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot.save("screenshot.png")
                return "Screenshot saved as screenshot.png"
            except:
                return "Could not take screenshot"
        
        # File operations
        elif "open folder" in cmd:
            folder_name = jarvis.extract_folder_name(cmd)
            if folder_name:
                jarvis.open_folder(folder_name)
                return f"Opening {folder_name} folder"
            return "Which folder would you like to open?"
        
        elif "create folder" in cmd:
            folder_name = jarvis.extract_folder_name(cmd)
            if folder_name:
                jarvis.create_folder(folder_name)
                return f"Created folder: {folder_name}"
            return "What would you like to name the folder?"
        
        elif "list files" in cmd:
            try:
                import os
                files = os.listdir('.')
                file_count = len(files)
                folder_count = len([f for f in files if os.path.isdir(f)])
                file_only_count = file_count - folder_count
                return f"Found {file_only_count} files and {folder_count} folders in current directory"
            except:
                return "Could not list files"
        
        # System control commands
        elif "shutdown" in cmd:
            return "System shutdown initiated. Please confirm this action manually for security."
        
        elif "restart" in cmd:
            return "System restart initiated. Please confirm this action manually for security."
        
        elif "sleep" in cmd:
            return "System sleep initiated. Please confirm this action manually for security."
        
        # Help command
        elif "help" in cmd:
            return """Available commands:
• System: time, date, system info, shutdown, restart, sleep
• Apps: chrome, firefox, notepad, calculator, task manager
• Search: search google for [query], youtube [query]
• Volume: volume up, volume down, mute
• Files: open folder [name], create folder [name], list files
• Screenshot: screenshot
• AI: Ask me anything else for AI-powered responses!"""
        
        # Default: Use AI for everything else
        else:
            return jarvis.chat_with_ai(command)
    
    except Exception as e:
        return f"Error processing command: {str(e)}"

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': time.time(),
        'service': 'Jarvis Assistant API'
    })

if __name__ == '__main__':
    print("🚀 Starting Jarvis Web Interface...")
    print("🌐 Access the UI at: http://localhost:5000")
    print("📡 API endpoint: http://localhost:5000/api/process_command")
    app.run(debug=True, host='0.0.0.0', port=5000)