import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import pyautogui
import win32clipboard
from PIL import ImageGrab
import io
import pygetwindow as gw
import pywinauto
import time
import requests
import json
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class UniversalAIChatTester:
    def __init__(self, root):
        self.root = root
        self.root.title('🎯 Universal AI Chat Tester - Kokoro Edition')
        self.root.geometry('600x700')
        
        # State variables
        self.selected_window = None
        self.screenshot = None
        self.kokoro_connected = False
        self.available_voices = []
        self.selected_voice = "default"
        self.speech_speed = 1.0
        self.driver = None
        
        # Kokoro API endpoint
        self.kokoro_url = "http://localhost:8880"
        
        self.setup_ui()
        self.test_kokoro_connection()
        
    def setup_ui(self):
        """Create the enhanced interface"""
        # Main title
        title_frame = tk.Frame(self.root)
        title_frame.pack(pady=10, fill=tk.X)
        tk.Label(title_frame, text="🎯 Universal AI Chat Tester", 
                font=("Arial", 16, "bold")).pack()
        tk.Label(title_frame, text="Building the AI-Machine Symbiosis", 
                font=("Arial", 10, "italic")).pack()
        
        # === SECTION 1: Window Connection (from 4.1's code) ===
        window_frame = tk.LabelFrame(self.root, text="🎯 Window Targeting", padx=10, pady=5)
        window_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Button(window_frame, text='📱 Select Target Window', 
                 command=self.select_window, bg='lightblue').pack(pady=5)
        self.window_status = tk.Label(window_frame, text="No window selected", fg="red")
        self.window_status.pack(pady=2)
        
        tk.Button(window_frame, text='📸 Take Screenshot', 
                 command=self.take_screenshot, bg='lightgreen').pack(pady=5)
        tk.Button(window_frame, text='📤 Send Screenshot', 
                 command=self.send_screenshot, bg='orange').pack(pady=5)
        
        # === SECTION 2: Kokoro Voice Integration ===
        kokoro_frame = tk.LabelFrame(self.root, text="🎤 Kokoro Voice Engine", padx=10, pady=5)
        kokoro_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Connection status
        self.kokoro_status = tk.Label(kokoro_frame, text="Connecting...", fg="orange")
        self.kokoro_status.pack(pady=2)
        
        # Voice selection
        voice_frame = tk.Frame(kokoro_frame)
        voice_frame.pack(pady=5, fill=tk.X)
        tk.Label(voice_frame, text="Voice:").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar(value="default")
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.voice_var, width=20)
        self.voice_combo.pack(side=tk.LEFT, padx=5)
        
        # Speed control
        speed_frame = tk.Frame(kokoro_frame)
        speed_frame.pack(pady=5, fill=tk.X)
        tk.Label(speed_frame, text="Speed:").pack(side=tk.LEFT)
        self.speed_var = tk.DoubleVar(value=1.0)
        self.speed_scale = tk.Scale(speed_frame, from_=0.5, to=2.0, resolution=0.1, 
                                   orient=tk.HORIZONTAL, variable=self.speed_var)
        self.speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Test buttons
        test_frame = tk.Frame(kokoro_frame)
        test_frame.pack(pady=5, fill=tk.X)
        tk.Button(test_frame, text='� Test Connection', 
                 command=self.test_kokoro_connection, bg='lightblue').pack(side=tk.LEFT, padx=2)
        tk.Button(test_frame, text='�🔊 Test Voice', 
                 command=self.test_voice, bg='lightcoral').pack(side=tk.LEFT, padx=2)
        tk.Button(test_frame, text='🔄 Refresh Voices', 
                 command=self.load_voices, bg='lightcyan').pack(side=tk.LEFT, padx=2)
        tk.Button(test_frame, text='🌐 Open Web UI', 
                 command=self.open_web_ui, bg='lightgreen').pack(side=tk.LEFT, padx=2)
        
        # === SECTION 3: Chat Scraping (Future) ===
        scrape_frame = tk.LabelFrame(self.root, text="🕷️ Chat Response Scraping", padx=10, pady=5)
        scrape_frame.pack(pady=10, padx=10, fill=tk.X)
        
        tk.Button(scrape_frame, text='🌐 Connect to Browser', 
                 command=self.connect_browser, bg='lightyellow').pack(pady=5)
        tk.Button(scrape_frame, text='📝 Scrape Last Response', 
                 command=self.scrape_response, bg='lightgray').pack(pady=5)
        tk.Button(scrape_frame, text='🔄 Send to Kokoro', 
                 command=self.send_to_kokoro, bg='lightpink').pack(pady=5)
        
        # === SECTION 4: Auto Loop ===
        loop_frame = tk.LabelFrame(self.root, text="🔄 Auto Loop Mode", padx=10, pady=5)
        loop_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.loop_active = tk.BooleanVar()
        tk.Checkbutton(loop_frame, text="Enable Auto-Loop (Monitor → Scrape → Speak)", 
                      variable=self.loop_active, command=self.toggle_loop).pack(pady=5)
        
        # Status display
        status_frame = tk.LabelFrame(self.root, text="📊 System Status", padx=10, pady=5)
        status_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(status_frame, height=8, width=70)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("🚀 Universal AI Chat Tester initialized!")
        self.log("💡 This is your testing ground for AI-machine symbiosis!")
        
    def log(self, message):
        """Add message to status log"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def test_kokoro_connection(self):
        """Test connection to kokoro and load voices"""
        def test_connection():
            try:
                response = requests.get(f"{self.kokoro_url}/health", timeout=5)
                if response.status_code == 200:
                    self.kokoro_connected = True
                    self.kokoro_status.config(text="✅ Kokoro Connected", fg="green")
                    self.log("✅ Kokoro connection successful!")
                    self.load_voices()
                else:
                    raise Exception(f"HTTP {response.status_code}")
            except Exception as e:
                self.kokoro_connected = False
                self.kokoro_status.config(text=f"❌ Connection Failed: {str(e)}", fg="red")
                self.log(f"❌ Kokoro connection failed: {e}")
                
        # Run in thread to avoid blocking UI
        threading.Thread(target=test_connection, daemon=True).start()
        
    def load_voices(self):
        """Load available voices from kokoro"""
        if not self.kokoro_connected:
            self.log("⚠️ Not connected to Kokoro")
            return
            
        def fetch_voices():
            try:
                response = requests.get(f"{self.kokoro_url}/voices", timeout=5)
                if response.status_code == 200:
                    voices_data = response.json()
                    self.available_voices = voices_data.get('voices', ['default'])
                    self.voice_combo['values'] = self.available_voices
                    self.log(f"🎵 Loaded {len(self.available_voices)} voices")
                else:
                    self.log("⚠️ Could not load voices")
            except Exception as e:
                self.log(f"❌ Error loading voices: {e}")
                
        threading.Thread(target=fetch_voices, daemon=True).start()
        
    def test_voice(self):
        """Test the selected voice with a sample message"""
        if not self.kokoro_connected:
            messagebox.showerror("Error", "Not connected to Kokoro!")
            return
            
        test_message = "Hello! This is a test of the Universal AI Chat system. The future is here!"
        voice = self.voice_var.get()
        speed = self.speed_var.get()
        
        def speak_test():
            try:
                payload = {
                    "text": test_message,
                    "voice": voice,
                    "speed": speed
                }
                response = requests.post(f"{self.kokoro_url}/speak", json=payload, timeout=10)
                if response.status_code == 200:
                    self.log(f"🔊 Voice test successful! Voice: {voice}, Speed: {speed}")
                else:
                    self.log(f"❌ Voice test failed: HTTP {response.status_code}")
            except Exception as e:
                self.log(f"❌ Voice test error: {e}")
                
        threading.Thread(target=speak_test, daemon=True).start()
        
    def open_web_ui(self):
        """Open kokoro web interface in browser"""
        import webbrowser
        webbrowser.open('http://localhost:8880/web/')
        self.log("🌐 Opened Kokoro web interface in browser")
        
    # === Original 4.1 functions (enhanced) ===
    def take_screenshot(self):
        """Take screenshot and copy to clipboard (from 4.1)"""
        self.screenshot = ImageGrab.grab()
        output = io.BytesIO()
        self.screenshot.save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        self.log("📸 Screenshot taken and copied to clipboard")

    def select_window(self):
        """Select target window (from 4.1, enhanced)"""
        windows = gw.getAllTitles()
        windows = [w for w in windows if w.strip() and 'Universal AI Chat Tester' not in w]
        if not windows:
            messagebox.showerror('Error', 'No windows found.')
            return
            
        sel_win = tk.Toplevel(self.root)
        sel_win.title('Select Target Window')
        sel_win.geometry('500x400')
        tk.Label(sel_win, text='🎯 Select the AI chat window to monitor:', 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(sel_win, width=70, height=20)
        listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        for w in windows:
            listbox.insert(tk.END, w)

        def on_select(event=None):
            selection = listbox.curselection()
            if selection:
                win = listbox.get(selection[0])
                self.selected_window = win
                self.window_status.config(text=f"✅ Connected: {win[:50]}...", fg="green")
                self.log(f"🎯 Target window selected: {win}")
                sel_win.destroy()

        listbox.bind('<Double-Button-1>', on_select)
        tk.Button(sel_win, text='✅ Select Window', command=on_select, 
                 bg='lightgreen').pack(pady=10)

    def send_screenshot(self):
        """Send screenshot to selected window (from 4.1)"""
        if not self.selected_window:
            messagebox.showerror('Error', 'No window selected.')
            return
        try:
            app = pywinauto.Application().connect(title=self.selected_window)
            win = app.window(title=self.selected_window)
            win.set_focus()
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
            self.log(f"📤 Screenshot sent to: {self.selected_window}")
        except Exception as e:
            self.log(f"❌ Failed to send screenshot: {e}")
            
    # === New Chat Scraping Functions ===
    def connect_browser(self):
        """Connect to browser for chat scraping"""
        self.log("🌐 Connecting to browser...")
        # This will be implemented for different chat platforms
        messagebox.showinfo("Info", "Browser connection feature coming soon!")
        
    def scrape_response(self):
        """Scrape the last response from the chat"""
        self.log("📝 Scraping chat response...")
        # This will implement the intelligent response detection
        messagebox.showinfo("Info", "Response scraping feature coming soon!")
        
    def send_to_kokoro(self):
        """Send scraped text to kokoro for speech"""
        self.log("🔄 Sending to Kokoro...")
        # This will connect the scraped text to voice output
        messagebox.showinfo("Info", "Auto-send to Kokoro feature coming soon!")
        
    def toggle_loop(self):
        """Toggle the auto-loop monitoring"""
        if self.loop_active.get():
            self.log("🔄 Auto-loop mode ACTIVATED")
            # Start monitoring thread
        else:
            self.log("⏹️ Auto-loop mode DEACTIVATED")
            # Stop monitoring thread

if __name__ == '__main__':
    root = tk.Tk()
    app = UniversalAIChatTester(root)
    root.mainloop()
