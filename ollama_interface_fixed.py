import tkinter as tk
from tkinter import ttk, filedialog
import requests
import json
import threading
import base64
import time
import os
import sys
import subprocess
from datetime import datetime
from PIL import Image
import mss
import pygetwindow as gw
import pyautogui
import win32gui
import win32con
import win32api  # Fixed: moved from inside method to prevent crashes
import pyperclip
from visual_log_window import VisualLogWindow

# Import speech system (with error handling to prevent crashes)
try:
    from flexible_whisper import FlexibleWhisper
    SPEECH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Speech system not available: {e}")
    FlexibleWhisper = None
    SPEECH_AVAILABLE = False

class OllamaInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 Visual Interpretation System v2.0 - DUAL VISION MODES")
        self.root.geometry("1170x1040")  # 30% bigger: 900*1.3=1170, 800*1.3=1040
        self.root.minsize(845, 780)     # 30% bigger: 650*1.3=845, 600*1.3=780
        
        # Force window to be visible and on top initially
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(2000, lambda: self.root.attributes('-topmost', False))  # Remove topmost after 2 seconds
        
        # Ollama configuration
        self.ollama_url = "http://localhost:11434"
        self.connected = False
        self.available_models = []
        self.selected_model = tk.StringVar()
        
        # Screenshot rotation system
        self.screenshots_dir = os.path.join(os.path.dirname(__file__), "screenshots")
        self.vision_log_file = os.path.join(os.path.dirname(__file__), "vision_log.json")
        self.rotation_active = False
        self.rotation_interval = 5  # Default 5 seconds
        self.max_screenshots = 3
        self.screenshot_counter = 0  # Will cycle through 1, 2, 3
        
        # Multi-screen support
        self.screen_selection = tk.StringVar(value="All Screens")
        self.available_screens = []
        self.selected_screen_index = None  # None = all screens, 0 = primary, 1 = secondary, etc.
        
        # Window targeting system
        self.target_windows = []
        self.selected_window = tk.StringVar()
        self.direct_output_enabled = tk.BooleanVar(value=False)
        self.selected_window_handle = None
        self.include_visual_context = tk.BooleanVar(value=False)
        self.auto_press_enter = tk.BooleanVar(value=False)  # Automatically press Enter after delivery
        
        # Vision mode selection - SIMPLE DUAL MODE SYSTEM!
        self.vision_mode = tk.StringVar(value="Vision Text")  # Default to working system
        
        # Screenshot resolution control
        self.screenshot_resolution = tk.StringVar(value="Original (4K)")  # Default to original resolution
        self.available_resolutions = ["Original (4K)", "Reduced (1080p)"]
        
        # Message system
        self.message_queue = []
        self.message_counter = 0
        
        # Message history for up/down arrow navigation
        self.message_history = []
        self.history_index = -1
        
        # Speech-to-text toggle system
        self.speech_listening = False
        self.speech_whisper = None
        self.speech_thread = None
        
        # WHISPER MODEL SWITCHING SYSTEM - YOUR CONTROL!
        self.current_whisper_model = tk.StringVar(value="Not Loaded")
        self.available_whisper_models = []
        self.whisper_model_combo = None
        
        # Keyword activation system - DEFAULT ON since user said it should be
        self.keyword_activation_enabled = tk.BooleanVar(value=True)
        self.trigger_keywords = [
            "I'm done talking"
        ]
        
        # Silence activation system - DEFAULT ON since user said it should work
        self.silence_activation_enabled = tk.BooleanVar(value=True)
        self.silence_duration = tk.StringVar(value="3s")
        self.last_speech_time = 0
        self.silence_timer = None
        self.countdown_active = False
        self.countdown_remaining = 0
        self.countdown_timer = None
        self.silence_buffer_timer = None  # 1-second buffer before activation
        self.silence_buffer_duration = 1.0  # 1 second buffer for soft activation
        
        # AUTO-SILENCE DETECTION - OPTIMIZED for better separation timing
        self.auto_silence_enabled = tk.BooleanVar(value=False)  # Default OFF - user controls
        self.auto_silence_duration = 15.0  # 15 seconds for silence separation timing
        self.auto_silence_timer = None
        
        # ENGLISH-ONLY MODE - Force English transcription only
        self.english_only_mode = tk.BooleanVar(value=False)
        
        # AUTO-CLEANUP - Prevent text accumulation sluggishness
        self.auto_cleanup_enabled = tk.BooleanVar(value=False)
        self.max_text_length = 2000  # Auto-clean when text exceeds this
        
        # Speech accumulation buffer for stable delivery - ULTRA RESPONSIVE APPROACH!
        self.speech_buffer = ""
        self.speech_buffer_timer = None
        self.speech_buffer_delay = 0.1  # ULTRA INSTANT - 0.1 seconds for immediate text appearance! (was 0.5)
        
        # SAFETY NET SYSTEM - Critical initialization to prevent crashes
        self.safety_net_active = tk.BooleanVar(value=False)
        self.safety_net_segments = []
        self.safety_net_current = ""
        self.safety_net_pause_timer = None
        self.safety_net_pause_duration = 5  # 5 seconds for segment creation
        self.safety_net_max_segments = 10  # Keep last 10 segments
        self.safety_net_file = os.path.join(os.path.dirname(__file__), "safety_net.json")
        
        # Browser automation system - NO MOUSE NEEDED!
        self.browser_automation = None
        
        # MESSAGE SEGMENTATION SYSTEM - Only send NEW content after each send!
        self.last_sent_position = "1.0"  # Track where we last sent content from
        self.message_segments = []  # Keep track of individual message segments
        
        # Visual log window
        self.visual_log_window = None
        
        # Model Chat System - dedicated chat interface  
        self.model_chat_window = None
        self.model_chat_history_file = os.path.join(os.path.dirname(__file__), "model_chat_history.json")
        self.model_chat_history = []
        
        # CHAT MEMORY SYSTEM - Preserve all conversations and input text
        self.chat_memory_file = os.path.join(os.path.dirname(__file__), "chat_memory.json")
        self.chat_memory = []  # List of all messages and interactions
        self.input_memory_file = os.path.join(os.path.dirname(__file__), "input_memory.json") 
        self.input_memory = []  # List of all input text history
        
        # Ensure screenshots directory exists
        os.makedirs(self.screenshots_dir, exist_ok=True)
        
        self.create_widgets()
        self.check_connection()
        self.refresh_windows()
        
        # Detect available screens
        self.detect_screens()
        
        # Load memory systems
        self.load_chat_memory()
        self.load_input_memory()
        
        # Add initial instructions
        self.add_initial_instructions()
        
        # Focus message entry for immediate use
        self.root.after(100, self.focus_message_entry)
        
        # Initialize speech system status - UPDATE THE INDICATOR!
        self.root.after(200, self.initialize_speech_status)
        
        # Start periodic status checking to detect external model changes
        self.start_periodic_status_check()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure root grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Configure custom styles for goddess-tier UI
        self.setup_custom_styles()
        
        # Connection status frame
        status_frame = ttk.LabelFrame(main_frame, text="Connection Status", padding="5")
        status_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status indicator
        self.status_label = ttk.Label(status_frame, text="Disconnected", foreground="red")
        self.status_label.grid(row=0, column=0)
        
        # Model selection frame
        model_frame = ttk.LabelFrame(main_frame, text="Model Selection", padding="5")
        model_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Model dropdown
        ttk.Label(model_frame, text="Select Model:").grid(row=0, column=0, sticky=tk.W)
        self.model_combo = ttk.Combobox(model_frame, textvariable=self.selected_model, state="readonly", width=30)
        self.model_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # Refresh models button
        self.refresh_button = ttk.Button(model_frame, text="Refresh Models", command=self.refresh_models)
        self.refresh_button.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        # Window Targeting frame
        window_frame = ttk.LabelFrame(main_frame, text="🎯 Output Targeting", padding="5")
        window_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Window selection dropdown
        ttk.Label(window_frame, text="Target Window:").grid(row=0, column=0, sticky=tk.W)
        self.window_combo = ttk.Combobox(window_frame, textvariable=self.selected_window, state="readonly", width=25)
        self.window_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        self.window_combo.bind('<<ComboboxSelected>>', self.on_window_selected)
        
        # Refresh windows button
        self.refresh_windows_button = ttk.Button(window_frame, text="🔄", command=self.refresh_windows, width=3)
        self.refresh_windows_button.grid(row=0, column=2, padx=(5, 0))
        
        # Direct output toggle button
        self.direct_output_button = ttk.Button(window_frame, text="Direct Output: OFF", 
                                              command=self.toggle_direct_output, style="Accent.TButton")
        self.direct_output_button.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Include visual context checkbox
        self.visual_context_check = ttk.Checkbutton(window_frame, text="Include Visual Context", 
                                                   variable=self.include_visual_context)
        self.visual_context_check.grid(row=1, column=2, padx=(5, 0), pady=(5, 0))
        
        # Auto-press Enter toggle (row 2, center)
        self.auto_enter_check = ttk.Checkbutton(window_frame, text="⚡ Auto-Press Enter", 
                                               variable=self.auto_press_enter)
        self.auto_enter_check.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # Keyword activation toggle (row 2.5, new row)
        self.keyword_activation_check = ttk.Checkbutton(window_frame, text="🎯 Keyword Activation", 
                                                       variable=self.keyword_activation_enabled,
                                                       command=self.on_keyword_activation_toggled)
        self.keyword_activation_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, pady=(2, 0))
        
        # Silence activation frame (row 3.5, new row)
        silence_frame = ttk.Frame(window_frame)
        silence_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(2, 0))
        
        self.silence_activation_check = ttk.Checkbutton(silence_frame, text="🤫 Silence Activation", 
                                                       variable=self.silence_activation_enabled,
                                                       command=self.on_silence_activation_toggled)
        self.silence_activation_check.grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(silence_frame, text="Duration:").grid(row=0, column=1, sticky=tk.W, padx=(10, 2))
        self.silence_duration_combo = ttk.Combobox(silence_frame, textvariable=self.silence_duration, 
                                                  values=["2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "10s"], 
                                                  state="readonly", width=5)
        self.silence_duration_combo.grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.silence_duration_combo.bind('<<ComboboxSelected>>', self.on_silence_duration_changed)
        
        # Visual countdown timer display
        self.countdown_label = ttk.Label(silence_frame, text="", foreground="orange", font=("Arial", 9, "bold"))
        self.countdown_label.grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # AUTO-SILENCE countdown display - VISUAL FEEDBACK for 10-second timer!
        self.auto_silence_countdown_label = ttk.Label(silence_frame, text="", foreground="red", font=("Arial", 8, "bold"))
        self.auto_silence_countdown_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(2, 0))
        
        # Keywords button - moved to same line as duration for better layout
        self.keyword_settings_button = ttk.Button(silence_frame, text="🎯 Keywords", command=self.show_keyword_settings, width=10)
        self.keyword_settings_button.grid(row=0, column=4, padx=(15, 0))
        
        # Vision Mode Selection (SIMPLE DUAL MODE!) - row 5
        ttk.Label(window_frame, text="Vision Mode:").grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        self.vision_mode_combo = ttk.Combobox(window_frame, textvariable=self.vision_mode, 
                                             values=["Vision Text", "Vision Image"], 
                                             state="readonly", width=12)
        self.vision_mode_combo.grid(row=5, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        self.vision_mode_combo.bind('<<ComboboxSelected>>', self.on_vision_mode_changed)
        
        # Vision mode status indicator
        self.vision_mode_label = ttk.Label(window_frame, text="📝 Text Mode", foreground="blue")
        self.vision_mode_label.grid(row=5, column=2, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # Screenshot resolution selector (only visible in Vision Image mode)
        ttk.Label(window_frame, text="Resolution:").grid(row=5, column=3, sticky=tk.W, padx=(15, 0), pady=(5, 0))
        self.resolution_combo = ttk.Combobox(window_frame, textvariable=self.screenshot_resolution, 
                                            values=self.available_resolutions, 
                                            state="readonly", width=14)
        self.resolution_combo.grid(row=5, column=4, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # WHISPER MODEL STATUS INDICATOR - Show current active model
        ttk.Label(window_frame, text="Speech Model:").grid(row=6, column=0, sticky=tk.W, pady=(5, 0))
        self.whisper_status_label = ttk.Label(window_frame, text="🤖 Not Loaded", foreground="orange", font=("Arial", 9, "bold"))
        self.whisper_status_label.grid(row=6, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # SIMPLE MODEL SWITCH BUTTON - Just toggle between small and medium!
        self.simple_switch_button = ttk.Button(window_frame, text="🔄 Switch Model", command=self.simple_model_switch, width=15)
        self.simple_switch_button.grid(row=6, column=2, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # MANUAL SYNC BUTTON - Fix display when models don't match!
        self.sync_models_button = ttk.Button(window_frame, text="🔄 Sync", command=self.manual_sync_models, width=8)
        self.sync_models_button.grid(row=6, column=3, sticky=tk.W, padx=(5, 0), pady=(5, 0))
        
        # SPLIT-PANE CHAT FRAME - ELEGANT DUAL SCREEN SYSTEM!
        chat_frame = ttk.LabelFrame(main_frame, text="💬 Dual Screen Interface", padding="5")
        chat_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create PanedWindow for resizable split interface
        self.paned_window = ttk.PanedWindow(chat_frame, orient=tk.HORIZONTAL)
        self.paned_window.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # LEFT PANE - System Messages & Status
        left_frame = ttk.LabelFrame(self.paned_window, text="🖥️ System Screen", padding="3")
        self.paned_window.add(left_frame, weight=1)
        
        # System chat display (left side)
        self.chat_text = tk.Text(left_frame, height=15, width=25, wrap=tk.WORD, 
                               font=("Consolas", 9), bg="#f8f9fa", fg="#2c3e50")
        self.chat_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add right-click context menu for chat area
        self.create_context_menu()
        
        # Scrollbar for system chat
        chat_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.chat_text.yview)
        chat_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.chat_text.configure(yscrollcommand=chat_scrollbar.set)
        
        # Configure left frame grid
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        # RIGHT PANE - Input & Writing Area
        right_frame = ttk.LabelFrame(self.paned_window, text="✍️ Input Screen", padding="3")
        self.paned_window.add(right_frame, weight=1)
        
        # BIG MESSAGE INPUT AREA - Full right pane!
        input_frame = ttk.Frame(right_frame)
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        # Multi-line text input (BIGGER for beautiful writing experience!)
        self.message_entry = tk.Text(input_frame, height=15, width=40, wrap=tk.WORD, 
                                   font=("Arial", 11), bg="#ffffff", fg="#2c3e50",
                                   insertbackground="#e74c3c", selectbackground="#3498db",
                                   maxundo=50, undo=True)  # Expanded from 12 to 15 lines
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Configure auto-scrolling - ALWAYS show latest text at bottom
        def auto_scroll_to_end(*args):
            self.message_entry.see(tk.END)
        
        # Bind to text changes for auto-scrolling
        self.message_entry.bind('<KeyRelease>', auto_scroll_to_end)
        self.message_entry.bind('<<Modified>>', auto_scroll_to_end)
        
        # Scrollbar for message input
        input_scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=self.message_entry.yview)
        input_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.message_entry.configure(yscrollcommand=input_scrollbar.set)
        
        # Bind events to the text widget
        self.message_entry.bind('<Control-Return>', self.send_message)  # Ctrl+Enter to send
        self.message_entry.bind('<KeyPress-Up>', self.navigate_history_up)  # Up arrow for history
        self.message_entry.bind('<KeyPress-Down>', self.navigate_history_down)  # Down arrow for history
        # Note: Focus events removed for now to avoid issues
        
        # Bind Ctrl+L to focus message entry
        self.root.bind('<Control-l>', lambda e: self.focus_message_entry())
        
        # Add right-click context menu for input area
        self.create_input_context_menu()
        
        # Configure input frame grid
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        # BUTTONS UNDERNEATH INPUT - Streamlined for clean look
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        buttons_frame.columnconfigure(0, weight=1)  # Left side expands
        
        # INPUT CONTROL BUTTONS - Left side for input management
        input_control_frame = ttk.Frame(buttons_frame)
        input_control_frame.grid(row=0, column=0, sticky=tk.W)
        
        self.copy_all_button = ttk.Button(input_control_frame, text="📋 Copy All", command=self.copy_all_input, width=12)
        self.copy_all_button.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_input_button = ttk.Button(input_control_frame, text="🗑️ Clear", command=self.clear_message_input, width=10)
        self.clear_input_button.grid(row=0, column=1, padx=(0, 5))
        
        # PRIMARY BUTTONS - Right side (like typical chat apps)
        primary_buttons_frame = ttk.Frame(buttons_frame)
        primary_buttons_frame.grid(row=0, column=1, sticky=tk.E)
        
        self.send_button = ttk.Button(primary_buttons_frame, text="📤 Send", command=self.send_message, width=12)
        self.send_button.grid(row=0, column=0, padx=(0, 5))
        
        self.speech_button = ttk.Button(primary_buttons_frame, text="🎤 TTS", command=self.activate_speech, width=10, style="Shiny.TButton")
        self.speech_button.grid(row=0, column=1, padx=(0, 5))
        
        # Model Manager button - The ONLY model button you need!
        self.model_manager_button = ttk.Button(primary_buttons_frame, text="🤖 Models", command=self.open_model_manager, width=10, style="Enhanced.Accent.TButton")
        self.model_manager_button.grid(row=0, column=2)
        
        # SECONDARY BUTTONS - Spread underneath
        secondary_buttons_frame = ttk.Frame(buttons_frame)
        secondary_buttons_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Row 1 of secondary buttons
        self.visual_log_button = ttk.Button(secondary_buttons_frame, text="� Visual Log", command=self.show_visual_log, width=15)
        self.visual_log_button.grid(row=0, column=0, padx=(0, 5))
        
        self.talk_to_model_button = ttk.Button(secondary_buttons_frame, text="💬 Talk to Model", command=self.open_model_chat, width=15)
        self.talk_to_model_button.grid(row=0, column=1, padx=(0, 5))
        
        # Debug/Test buttons
        self.debug_delivery_button = ttk.Button(secondary_buttons_frame, text="🎯 Test Delivery", command=self.test_delivery, width=15)
        self.debug_delivery_button.grid(row=0, column=2, padx=(0, 5))
        
        # Row 2 of secondary buttons  
        self.debug_clipboard_button = ttk.Button(secondary_buttons_frame, text="📋 Test Clipboard", command=self.test_clipboard, width=15)
        self.debug_clipboard_button.grid(row=1, column=0, padx=(0, 5), pady=(5, 0))
        
        self.copy_last_button = ttk.Button(secondary_buttons_frame, text="�️ Copy Last", command=self.copy_last_safety_segment, width=15)
        self.copy_last_button.grid(row=1, column=1, padx=(0, 5), pady=(5, 0))
        
        # QUICK TEST BUTTONS - No waiting for AI!
        self.quick_test_button = ttk.Button(secondary_buttons_frame, text="⚡ Quick Test", command=self.quick_test_speech, width=15)
        self.quick_test_button.grid(row=1, column=2, padx=(0, 5), pady=(5, 0))
        
        # Row 3 of secondary buttons - YOUR AWESOME NEW FEATURES!
        self.english_only_button = ttk.Button(secondary_buttons_frame, text="🇺🇸 English Only", command=self.toggle_english_only, width=15)
        self.english_only_button.grid(row=2, column=0, padx=(0, 5), pady=(5, 0))
        
        self.auto_silence_button = ttk.Button(secondary_buttons_frame, text="🤫 Auto-Silence: OFF", command=self.toggle_auto_silence, width=15)
        self.auto_silence_button.grid(row=2, column=1, padx=(0, 5), pady=(5, 0))
        
        self.auto_cleanup_button = ttk.Button(secondary_buttons_frame, text="🧹 Auto-Clean: OFF", command=self.toggle_auto_cleanup, width=15)
        self.auto_cleanup_button.grid(row=2, column=2, padx=(0, 5), pady=(5, 0))
        
        # Row 4 - INSTANT TESTING BUTTONS (Clear descriptions!)
        self.instant_back_button = ttk.Button(secondary_buttons_frame, text="⬅️ History Back", command=self.instant_back_test, width=15)
        self.instant_back_button.grid(row=3, column=0, padx=(0, 5), pady=(5, 0))
        
        self.instant_forward_button = ttk.Button(secondary_buttons_frame, text="➡️ History Forward", command=self.instant_forward_test, width=15)
        self.instant_forward_button.grid(row=3, column=1, padx=(0, 5), pady=(5, 0))
        
        # BROWSER AUTOMATION - Better description!
        self.connection_test_button = ttk.Button(secondary_buttons_frame, text="🔗 Test Connection", command=self.test_window_connection, width=15)
        self.connection_test_button.grid(row=3, column=2, padx=(0, 5), pady=(5, 0))
        
        # Configure right frame grid
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)  # Input area gets most space
        
        # Button area frame
        button_frame = ttk.Frame(main_frame, padding="5")
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Add some nice utility buttons
        self.clear_button = ttk.Button(button_frame, text="Clear Screen", command=self.clear_chat)
        self.clear_button.grid(row=0, column=0, padx=(0, 5))
        
        self.reconnect_button = ttk.Button(button_frame, text="Reconnect", command=self.check_connection)
        self.reconnect_button.grid(row=0, column=1, padx=(0, 5))
        
        # Screenshot rotation controls
        self.rotation_button = ttk.Button(button_frame, text="Start Rotation", command=self.toggle_rotation)
        self.rotation_button.grid(row=0, column=2, padx=(0, 5))
        
        # Screen selector frame
        screen_frame = ttk.Frame(button_frame)
        screen_frame.grid(row=0, column=3, padx=(0, 5))
        
        ttk.Label(screen_frame, text="Screen:").pack(side="left")
        self.screen_combo = ttk.Combobox(screen_frame, textvariable=self.screen_selection, 
                                        state="readonly", width=12)
        self.screen_combo.pack(side="left", padx=(2, 0))
        self.screen_combo.bind('<<ComboboxSelected>>', self.on_screen_selected)
        
        # Interval selector
        interval_frame = ttk.Frame(button_frame)
        interval_frame.grid(row=0, column=4, padx=(0, 5))
        
        ttk.Label(interval_frame, text="Interval:").pack(side="left")
        self.interval_var = tk.StringVar(value="5s")
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, 
                                     values=["3s", "5s", "10s"], state="readonly", width=5)
        interval_combo.pack(side="left", padx=(2, 0))
        interval_combo.bind('<<ComboboxSelected>>', self.update_interval)
        
        # Configure grid weights for the MAIN FRAME
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)  # Chat frame is now row 3
        model_frame.columnconfigure(1, weight=1)
        window_frame.columnconfigure(1, weight=1)
        
        # Configure grid weights for SPLIT-PANE SYSTEM
        chat_frame.columnconfigure(0, weight=1)  # PanedWindow gets full width
        chat_frame.rowconfigure(0, weight=1)     # PanedWindow gets full height
        
    def setup_custom_styles(self):
        """Setup custom styles for a more polished UI"""
        try:
            style = ttk.Style()
            
            # Modern button styles with gradients and shine
            style.configure("Shiny.TButton",
                          relief="raised",
                          borderwidth=2,
                          focuscolor="none")
            
            style.configure("SpeechActive.TButton",
                          foreground="white",
                          background="#E74C3C",  # Red for active
                          relief="raised",
                          borderwidth=2,
                          focuscolor="none")
            
            style.configure("DirectOutput.TButton",
                          foreground="#FFFFFF",  # Pure white text
                          background="#00B050",  # Brighter green
                          relief="raised",
                          borderwidth=2,
                          focuscolor="none")
            
            # Even brighter style for toggle states
            style.configure("ToggleActive.TButton",
                          foreground="#FFFFFF",  # Pure white text
                          background="#00AA44",  # Extra bright green  
                          relief="raised",
                          borderwidth=3,
                          focuscolor="none")
            
            # Enhanced accent style
            style.configure("Enhanced.Accent.TButton",
                          relief="raised",
                          borderwidth=2,
                          focuscolor="none")
                          
        except Exception as e:
            # Fallback if styling fails
            pass
        
    def detect_screens(self):
        """Detect available screens/monitors"""
        try:
            import tkinter as tk
            
            # Get screen information
            root_temp = tk.Tk()
            root_temp.withdraw()  # Hide temporary window
            
            # Get primary screen dimensions
            screen_width = root_temp.winfo_screenwidth()
            screen_height = root_temp.winfo_screenheight()
            
            root_temp.destroy()
            
            # SIMPLIFIED: Just two options - Screen 1 and Screen 2
            screens = []
            
            # Method 1: Using PIL ImageGrab to detect virtual screen size
            try:
                from PIL import ImageGrab
                # Get the virtual screen size using MSS
                with mss.mss() as sct:
                    # All monitors combined
                    all_monitors = sct.monitors[0]
                    virtual_width, virtual_height = all_monitors['width'], all_monitors['height']
                
                self.add_chat_message("Debug", f"🔍 SIMPLIFIED Screen Detection:")
                self.add_chat_message("Debug", f"  Primary Screen: {screen_width}x{screen_height}")
                self.add_chat_message("Debug", f"  Virtual Desktop: {virtual_width}x{virtual_height}")
                
                # Always add primary screen FIRST (default)
                screens.append(("Screen 1", 0, f"{screen_width}x{screen_height}"))
                
                # Always add secondary screen
                if virtual_width > screen_width:
                    # Calculate secondary screen dimensions
                    secondary_width = virtual_width - screen_width
                    screens.append(("Screen 2", 1, f"{secondary_width}x{virtual_height}"))
                    self.add_chat_message("System", f"🖥️ Dual monitor setup detected!")
                else:
                    # Add Screen 2 anyway for testing
                    screens.append(("Screen 2", 1, f"{screen_width}x{screen_height}"))
                    self.add_chat_message("System", f"�️ Added Screen 2 option (may be same as Screen 1)")
                    
            except Exception as e:
                # Fallback: add basic options
                screens.append(("Screen 1", 0, f"{screen_width}x{screen_height}"))
                screens.append(("Screen 2", 1, f"{screen_width}x{screen_height}"))
                self.add_chat_message("Debug", f"Screen detection fallback: {e}")
            
            # Update the dropdown
            self.available_screens = screens
            screen_options = [f"{name} ({resolution})" for name, index, resolution in screens]
            self.screen_combo['values'] = screen_options
            
            # Default to "Screen 1" (monitor index 1 for MSS)
            if screen_options:
                self.screen_combo.set(screen_options[0])
                self.selected_screen_index = 1
                
            # Show what we detected
            self.add_chat_message("System", f"📋 Available screen options: {len(screen_options)}")
            for option in screen_options:
                self.add_chat_message("Debug", f"  • {option}")
                
        except Exception as e:
            self.add_chat_message("Error", f"Screen detection failed: {e}")
            # Fallback to basic setup with all options
            self.available_screens = [
                ("All Screens", None, "Unknown"),
                ("Screen 1 (Primary)", 0, "Unknown"), 
                ("Screen 2 (Secondary)", 1, "Unknown")
            ]
            self.screen_combo['values'] = [
                "All Screens (Unknown)",
                "Screen 1 (Primary) (Unknown)",
                "Screen 2 (Secondary) (Unknown)"
            ]
            self.screen_combo.set("All Screens (Unknown)")
    
    def on_screen_selected(self, event=None):
        """Handle screen selection change - MSS VERSION"""
        try:
            selected = self.screen_combo.get()
            self.add_chat_message("System", f"🔄 SCREEN SWITCH: '{selected}'")
            
            # MSS LOGIC: Screen 1 = monitor 1, Screen 2 = monitor 2
            if "Screen 1" in selected:
                self.selected_screen_index = 1  # MSS monitor 1
                self.add_chat_message("System", f"✅ SWITCHED TO SCREEN 1 (MSS monitor=1)")
            elif "Screen 2" in selected:
                self.selected_screen_index = 2  # MSS monitor 2
                self.add_chat_message("System", f"✅ SWITCHED TO SCREEN 2 (MSS monitor=2)")
            else:
                self.add_chat_message("Error", f"❌ Unknown selection: '{selected}'")
                
        except Exception as e:
            self.add_chat_message("Error", f"Screen selection error: {e}")

    def on_vision_mode_changed(self, event=None):
        """Handle vision mode change between Text and Image"""
        try:
            mode = self.vision_mode.get()
            if mode == "Vision Text":
                self.vision_mode_label.config(text="📝 Text Mode", foreground="blue")
                self.add_chat_message("System", "🔄 VISION MODE: Text (Current working system)")
            elif mode == "Vision Image":
                self.vision_mode_label.config(text="📸 Image Mode", foreground="green")  
                self.add_chat_message("System", "🔄 VISION MODE: Image (Screenshot attachments)")
                self.add_chat_message("System", "⚠️ Note: Image uploads may take 1-2 seconds")
            else:
                self.add_chat_message("Error", f"❌ Unknown vision mode: {mode}")
                
        except Exception as e:
            self.add_chat_message("Error", f"Vision mode change error: {e}")
    
    def on_keyword_activation_toggled(self):
        """Handle keyword activation toggle"""
        try:
            if self.keyword_activation_enabled.get():
                self.add_chat_message("System", "🎯 Keyword activation ENABLED")
            else:
                self.add_chat_message("System", "🎯 Keyword activation DISABLED")
                
        except Exception as e:
            self.add_chat_message("Error", f"Keyword toggle error: {e}")
    
    def on_silence_activation_toggled(self):
        """Handle silence activation toggle - RESET TIMER LOGIC"""
        try:
            if self.silence_activation_enabled.get():
                self.add_chat_message("System", "🤫 Silence activation ENABLED - timer will reset on toggle")
            else:
                self.add_chat_message("System", "🤫 Silence activation DISABLED")
                
            # SMART RESET LOGIC - Reset timer whenever toggled
            self.reset_silence_timer()
            
            # If there's existing text and silence is enabled, start fresh timer
            if self.silence_activation_enabled.get():
                message_content = self.get_message_text().strip()
                if message_content:
                    self.add_chat_message("System", "📝 Text detected - silence timer will start after next speech")
                    
        except Exception as e:
            self.add_chat_message("Error", f"Silence toggle error: {e}")
    
    def on_silence_duration_changed(self, event=None):
        """Handle silence duration change - RESET TIMER"""
        try:
            duration = self.silence_duration.get()
            self.add_chat_message("System", f"🕐 Silence duration changed to {duration} - timer reset")
            
            # Reset timer when duration changes
            self.reset_silence_timer()
            
        except Exception as e:
            self.add_chat_message("Error", f"Duration change error: {e}")
    
    def reset_silence_timer(self):
        """Reset all silence-related timers and counters"""
        try:
            # Cancel existing timers
            if self.silence_timer:
                self.root.after_cancel(self.silence_timer)
                self.silence_timer = None
                
            if self.countdown_timer:
                self.root.after_cancel(self.countdown_timer)
                self.countdown_timer = None
                
            if self.silence_buffer_timer:
                self.root.after_cancel(self.silence_buffer_timer)
                self.silence_buffer_timer = None
            
            # Reset countdown state
            self.countdown_active = False
            self.countdown_remaining = 0
            
            # Clear countdown display
            self.countdown_label.config(text="")
            
        except Exception as e:
            self.add_chat_message("Error", f"Timer reset error: {e}")

    # ===== YOUR AWESOME NEW FEATURES! =====
    
    def toggle_english_only(self):
        """Toggle English-only transcription mode"""
        try:
            self.english_only_mode.set(not self.english_only_mode.get())
            
            # Apply to speech recognition if active
            if self.speech_whisper:
                self.speech_whisper.set_english_only(self.english_only_mode.get())
            
            if self.english_only_mode.get():
                self.english_only_button.config(text="🇺🇸 ENGLISH ONLY", style="ToggleActive.TButton")
                self.add_chat_message("System", "🇺🇸 ENGLISH-ONLY MODE ENABLED!")
                self.add_chat_message("System", "💬 Speech will be transcribed in English only")
                self.add_chat_message("System", "🚫 Russian/Arabic/other languages filtered out")
            else:
                self.english_only_button.config(text="🌍 Multi-Language", style="Enhanced.Accent.TButton")
                self.add_chat_message("System", "🌍 Multi-language mode enabled")
                self.add_chat_message("System", "🗣️ All languages will be transcribed")
                
        except Exception as e:
            self.add_chat_message("Error", f"English-only toggle error: {e}")
    
    def toggle_auto_silence(self):
        """Toggle auto-silence detection (10 second pause = separator)"""
        try:
            self.auto_silence_enabled.set(not self.auto_silence_enabled.get())
            
            if self.auto_silence_enabled.get():
                self.auto_silence_button.config(text="🤫 Auto-Silence: ON", style="ToggleActive.TButton")
                self.add_chat_message("System", "🤫 AUTO-SILENCE DETECTION ENABLED!")
                self.add_chat_message("System", "⏱️ 15 seconds of silence = automatic ✂️ CUT separator")
                self.add_chat_message("System", "� Visual countdown will show when active!")
            else:
                self.auto_silence_button.config(text="🤫 Auto-Silence: OFF", style="Enhanced.Accent.TButton")
                self.add_chat_message("System", "🤫 Auto-silence detection disabled")
                # Clear any active countdown
                if hasattr(self, 'auto_silence_countdown_label'):
                    self.auto_silence_countdown_label.config(text="")
                
        except Exception as e:
            self.add_chat_message("Error", f"Auto-silence toggle error: {e}")
    
    def toggle_auto_cleanup(self):
        """Toggle auto-cleanup to prevent text accumulation sluggishness"""
        try:
            self.auto_cleanup_enabled.set(not self.auto_cleanup_enabled.get())
            
            if self.auto_cleanup_enabled.get():
                self.auto_cleanup_button.config(text="🧹 Auto-Clean: ON", style="ToggleActive.TButton")
                self.add_chat_message("System", "🧹 AUTO-CLEANUP ENABLED!")
                self.add_chat_message("System", f"📏 Text will auto-clean at {self.max_text_length} characters")
                self.add_chat_message("System", "⚡ Prevents sluggishness from long text accumulation")
            else:
                self.auto_cleanup_button.config(text="🧹 Auto-Clean: OFF", style="Enhanced.Accent.TButton")
                self.add_chat_message("System", "🧹 Auto-cleanup disabled - text will accumulate")
                
        except Exception as e:
            self.add_chat_message("Error", f"Auto-cleanup toggle error: {e}")
    
    def start_auto_silence_timer(self):
        """Start the 10-second auto-silence detection timer with VISUAL COUNTDOWN - ONLY for accumulation mode"""
        try:
            # CRITICAL LOGIC FIX: Auto-silence ONLY works when Direct Output is OFF (accumulation mode)
            if self.direct_output_enabled.get():
                # Direct Output is ON - no auto-silence, separators come from sending
                return
            
            # Cancel any existing timer - CRITICAL for preventing wrong cuts!
            if self.auto_silence_timer:
                self.root.after_cancel(self.auto_silence_timer)
                self.auto_silence_timer = None
            
            # Start new 10-second timer with visual feedback - ONLY for accumulation mode
            self.auto_silence_timer = self.root.after(
                int(self.auto_silence_duration * 1000),
                self.auto_silence_detected
            )
            
            # Start visual countdown display
            if self.auto_silence_enabled.get():
                self.start_auto_silence_countdown_display()
            
        except Exception as e:
            self.add_chat_message("Error", f"Auto-silence timer error: {e}")
    
    def start_auto_silence_countdown_display(self):
        """Visual countdown display for auto-silence detection"""
        try:
            self.auto_silence_countdown_remaining = int(self.auto_silence_duration)
            self.update_auto_silence_countdown()
            
        except Exception as e:
            self.add_chat_message("Error", f"Auto-silence countdown error: {e}")
    
    def update_auto_silence_countdown(self):
        """Update the visual countdown display - ONLY for accumulation mode"""
        try:
            # FIXED LOGIC: Only show countdown when Direct Output is OFF (accumulation mode)
            if (hasattr(self, 'auto_silence_countdown_remaining') and 
                self.auto_silence_countdown_remaining > 0 and 
                not self.direct_output_enabled.get()):
                
                # Show countdown with visual indicators - SILENCE instead of CUT for accumulation mode
                countdown_text = f"🤫 Auto-silence: {self.auto_silence_countdown_remaining}s until SILENCE"
                self.auto_silence_countdown_label.config(text=countdown_text)
                
                # Decrease counter and schedule next update
                self.auto_silence_countdown_remaining -= 1
                self.root.after(1000, self.update_auto_silence_countdown)
            else:
                # Clear countdown display
                self.auto_silence_countdown_label.config(text="")
                
        except Exception as e:
            self.add_chat_message("Error", f"Countdown update error: {e}")
    
    def auto_silence_detected(self):
        """Handle 10-second silence detection - ONLY for accumulation mode, shows SILENCE separator"""
        try:
            if self.auto_silence_enabled.get() and not self.direct_output_enabled.get():
                # FIXED LOGIC: Only add SILENCE separator when Direct Output is OFF (accumulation mode)
                current_text = self.get_message_text()
                if current_text.strip():  # Only add separator if there's existing text
                    separator = "\n" + "─" * 30 + " SILENCE " + "─" * 30 + "\n"
                    self.message_entry.insert(tk.END, separator)
                    self.message_entry.see(tk.END)
                    
                    self.add_chat_message("System", "🤫 15-second silence detected - text separated with SILENCE")
                    
                    # Auto-cleanup check
                    self.check_auto_cleanup()
            
            # Clear countdown display
            self.auto_silence_countdown_label.config(text="")
            self.auto_silence_timer = None
            
        except Exception as e:
            self.add_chat_message("Error", f"Auto-silence detection error: {e}")
    
    def check_auto_cleanup(self):
        """Check if text needs auto-cleanup to prevent sluggishness"""
        try:
            if self.auto_cleanup_enabled.get():
                current_text = self.get_message_text()
                if len(current_text) > self.max_text_length:
                    # Keep only the last portion of text
                    keep_length = int(self.max_text_length * 0.7)  # Keep 70% of max
                    new_text = "...[auto-cleaned]...\n" + current_text[-keep_length:]
                    
                    self.message_entry.delete("1.0", tk.END)
                    self.message_entry.insert("1.0", new_text)
                    self.message_entry.see(tk.END)
                    
                    self.add_chat_message("System", f"🧹 Auto-cleaned text to prevent sluggishness ({len(new_text)} chars)")
                    
        except Exception as e:
            self.add_chat_message("Error", f"Auto-cleanup error: {e}")

    # ===== INSTANT TESTING BUTTONS - NO WAITING FOR AI! =====
    
    def quick_test_speech(self):
        """Quick test of speech system - instant feedback!"""
        try:
            self.add_chat_message("System", "⚡ QUICK TEST: Speech system check...")
            
            # Test 1: Check if speech is available
            if SPEECH_AVAILABLE:
                self.add_chat_message("System", "✅ Speech system: AVAILABLE")
            else:
                self.add_chat_message("System", "❌ Speech system: NOT AVAILABLE")
            
            # Test 2: Check current listening state
            if self.speech_listening:
                self.add_chat_message("System", "🎤 Status: LISTENING")
            else:
                self.add_chat_message("System", "🔇 Status: NOT LISTENING")
                
            # Test 3: Check silence activation
            if self.silence_activation_enabled.get():
                duration = self.silence_duration.get()
                self.add_chat_message("System", f"🤫 Silence: ENABLED ({duration})")
            else:
                self.add_chat_message("System", "🤫 Silence: DISABLED")
                
            # Test 4: Check direct output
            if self.direct_output_enabled.get():
                window = self.selected_window.get()
                self.add_chat_message("System", f"🎯 Output: ENABLED → {window}")
            else:
                self.add_chat_message("System", "🎯 Output: DISABLED")
                
            self.add_chat_message("System", "⚡ Quick test complete - NO WAITING!")
            
        except Exception as e:
            self.add_chat_message("Error", f"Quick test error: {e}")
    
    def instant_back_test(self):
        """Simulate going back in message history - adds test text to show it works"""
        try:
            self.add_chat_message("System", "⬅️ HISTORY BACK: Simulating previous message...")
            
            # Add some test text to show it's working
            test_text = "📝 Previous message content - this simulates history navigation"
            self.message_entry.insert(tk.END, f"\n⬅️ {test_text}")
            self.message_entry.see(tk.END)
            
            self.add_chat_message("System", "⬅️ History Back test complete - this is just a demo!")
            self.add_chat_message("System", "💡 Future: Will navigate to previous messages")
            
        except Exception as e:
            self.add_chat_message("Error", f"History back test error: {e}")
    
    def instant_forward_test(self):
        """Simulate going forward in message history - adds test text to show it works"""
        try:
            self.add_chat_message("System", "➡️ HISTORY FORWARD: Simulating next message...")
            
            # Add some test text to show it's working
            test_text = "📝 Next message content - this simulates history navigation"
            self.message_entry.insert(tk.END, f"\n➡️ {test_text}")
            self.message_entry.see(tk.END)
            
            self.add_chat_message("System", "➡️ History Forward test complete - this is just a demo!")
            self.add_chat_message("System", "💡 Future: Will navigate to next messages")
            
        except Exception as e:
            self.add_chat_message("Error", f"History forward test error: {e}")

    def test_window_connection(self):
        """Test connection to selected window - PERFECT for verifying setup!"""
        try:
            if not self.direct_output_enabled.get():
                self.add_chat_message("Error", "❌ Direct Output is OFF - turn it ON first!")
                self.add_chat_message("System", "💡 Click 'Direct Output: OFF' to turn it ON")
                return
            
            if not self.selected_window_handle:
                self.add_chat_message("Error", "❌ No target window selected!")
                self.add_chat_message("System", "💡 Steps: 1) Click 🔄 to refresh windows")
                self.add_chat_message("System", "💡       2) Choose your target window from dropdown")
                self.add_chat_message("System", "💡       3) Then click 🔗 Test Connection")
                return
            
            window_title = self.selected_window.get()
            self.add_chat_message("System", f"🔗 TESTING CONNECTION to: {window_title}")
            
            # Test message to verify connection
            test_message = f"🔗 CONNECTION TEST - {datetime.now().strftime('%H:%M:%S')}"
            
            # Attempt to send test message
            success = self.send_direct_to_window(test_message)
            
            if success:
                self.add_chat_message("System", "✅ CONNECTION TEST SUCCESSFUL!")
                self.add_chat_message("System", "🎯 Target window is ready to receive messages")
                self.add_chat_message("System", "⚡ Auto-press Enter: " + ("ON" if self.auto_press_enter.get() else "OFF"))
                if self.auto_press_enter.get():
                    self.add_chat_message("System", "💡 Messages will auto-submit with Enter key")
                else:
                    self.add_chat_message("System", "💡 Enable 'Auto-Press Enter' for automatic submission")
            else:
                self.add_chat_message("Error", "❌ CONNECTION TEST FAILED!")
                self.add_chat_message("System", "💡 Try: 1) Select different window")
                self.add_chat_message("System", "💡      2) Make sure target window is visible")
                self.add_chat_message("System", "💡      3) Try again")
                
        except Exception as e:
            self.add_chat_message("Error", f"Connection test error: {e}")

    # ===== BROWSER AUTOMATION - NO MOUSE NEEDED! =====
    
    def toggle_browser_automation(self):
        """Toggle browser automation mode - WORKS ALONGSIDE EXISTING SYSTEMS!"""
        try:
            if not self.browser_automation:
                # CHECK: Do you have a target window selected?
                if not self.selected_window_handle:
                    self.add_chat_message("Error", "❌ Please select a target window FIRST!")
                    self.add_chat_message("System", "💡 WHAT THIS DOES: Connects to web browsers!")
                    self.add_chat_message("System", "💡 Steps: 1) Click 🔄 to refresh windows")
                    self.add_chat_message("System", "💡       2) Choose your browser (Chrome, Edge, Firefox)")
                    self.add_chat_message("System", "💡       3) Then click 🌐 Web Connect")
                    self.add_chat_message("System", "")
                    self.add_chat_message("System", "🎯 This sends your speech directly to ChatGPT/Claude/Discord!")
                    return
                
                # PERFECT! Connect to YOUR chosen window
                window_title = self.selected_window.get()
                self.add_chat_message("System", f"🌐 Preparing Browser Automation for: {window_title}")
                self.add_chat_message("System", "✅ EXISTING SYSTEMS PRESERVED - No breaking changes!")
                
                # Start browser automation for YOUR target
                try:
                    try:
                        from browser_automation import BrowserBridge
                    except ImportError:
                        self.add_chat_message("Error", "❌ Browser automation module not found")
                        self.add_chat_message("System", "💡 Install with: pip install selenium webdriver_manager")
                        BrowserBridge = None
                    self.browser_automation = BrowserBridge()
                    
                    # Check if this is a web-based target
                    if self.is_web_target(window_title):
                        if self.browser_automation.prepare_for_web_window(window_title):
                            self.browser_automation_button.config(text="🌐 WEB: ON", style="ToggleActive.TButton")
                            self.add_chat_message("System", f"✅ Browser automation ACTIVE for: {window_title}")
                            self.add_chat_message("System", "🌐 Speech → Browser (no cursor conflicts!)")
                            self.add_chat_message("System", "🔄 Direct Output still available for desktop apps!")
                        else:
                            self.browser_automation = None
                            self.add_chat_message("Error", "❌ Failed to connect browser automation")
                    else:
                        # Not a web target - suggest using existing direct output
                        self.browser_automation = None
                        self.add_chat_message("System", "💡 This looks like a desktop app!")
                        self.add_chat_message("System", "💡 Use 'Direct Output' instead for desktop apps")
                        self.add_chat_message("System", "🌐 Browser automation is for web pages only")
                        
                except ImportError:
                    self.add_chat_message("Error", "❌ Browser automation module not found")
                    self.add_chat_message("System", "💡 Run: pip install selenium")
                    
            else:
                # Disconnect browser automation - existing systems unaffected
                self.browser_automation.stop()
                self.browser_automation = None
                self.browser_automation_button.config(text="🌐 Web Connect", style="Enhanced.Accent.TButton")
                self.add_chat_message("System", "🌐 Browser automation stopped")
                self.add_chat_message("System", "✅ All existing systems still working normally!")
                
        except Exception as e:
            self.add_chat_message("Error", f"Browser automation error: {e}")

    def is_web_target(self, window_title):
        """Check if the target window is a web browser"""
        web_indicators = [
            "chrome", "firefox", "edge", "safari", "opera", "brave",
            "chatgpt", "claude", "discord", "browser"
        ]
        title_lower = window_title.lower()
        return any(indicator in title_lower for indicator in web_indicators)

    def send_to_browser_if_active(self, message):
        """Send message to browser if automation is active - DOESN'T AFFECT OTHER SYSTEMS"""
        try:
            if self.browser_automation:
                success = self.browser_automation.send_message(message)
                if success:
                    self.add_chat_message("System", "🌐 Message sent via browser automation!")
                    return True
                else:
                    self.add_chat_message("Error", "❌ Browser send failed - falling back to normal systems")
                    return False
            return False
        except Exception as e:
            self.add_chat_message("Error", f"Browser send error: {e}")
            return False

    def show_whisper_selector(self):
        """Show Whisper model selector window - YOUR CONTROL PANEL!"""
        try:
            # If speech system not loaded, load it first
            if not self.speech_whisper:
                self.add_chat_message("System", "🚀 Loading speech system first...")
                self.force_load_speech_system()
                return
                
            # Create popup window
            selector_window = tk.Toplevel(self.root)
            selector_window.title("🤖 Whisper Model Selector")
            selector_window.geometry("400x350")
            selector_window.resizable(False, False)
            
            # Make it modal and center it
            selector_window.transient(self.root)
            selector_window.grab_set()
            
            # Center the window
            selector_window.geometry("+%d+%d" % 
                                   (self.root.winfo_rootx() + 100, 
                                    self.root.winfo_rooty() + 100))
            
            # Main frame
            main_frame = ttk.Frame(selector_window, padding="15")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="🎙️ Speech Recognition Models", 
                                  font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Current model status
            status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding="10")
            status_frame.pack(fill="x", pady=(0, 10))
            
            current_model = "Not Loaded"
            if self.speech_whisper:
                current_model = self.speech_whisper.selected_model_name
            
            current_label = ttk.Label(status_frame, text=f"Active Model: {current_model}",
                                    font=("Arial", 10, "bold"), foreground="blue")
            current_label.pack()
            
            # Available models list
            models_frame = ttk.LabelFrame(main_frame, text="Available Models", padding="10")
            models_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            # Get available models
            available_models = self.get_available_whisper_models()
            
            if not available_models:
                no_models_label = ttk.Label(models_frame, text="❌ No models found in your folder",
                                          foreground="red")
                no_models_label.pack(pady=10)
                
                help_label = ttk.Label(models_frame, 
                                     text="💡 Use the Model Manager to download models first",
                                     foreground="gray")
                help_label.pack()
            else:
                # Create listbox for model selection
                listbox_frame = ttk.Frame(models_frame)
                listbox_frame.pack(fill="both", expand=True)
                
                self.model_listbox = tk.Listbox(listbox_frame, height=6, font=("Arial", 10))
                self.model_listbox.pack(side="left", fill="both", expand=True)
                
                # Scrollbar for listbox
                scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.model_listbox.yview)
                scrollbar.pack(side="right", fill="y")
                self.model_listbox.configure(yscrollcommand=scrollbar.set)
                
                # Populate with models
                for model in available_models:
                    display_name = f"🤖 {model}"
                    if self.speech_whisper and model in current_model:
                        display_name += " ✅ (Active)"
                    self.model_listbox.insert(tk.END, display_name)
                
                # Add double-click functionality for instant switching
                self.model_listbox.bind("<Double-Button-1>", lambda e: self.quick_switch_model(selector_window, available_models))
                
                # Select current model if any
                if self.speech_whisper:
                    for i, model in enumerate(available_models):
                        if model in current_model:
                            self.model_listbox.selection_set(i)
                            break
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=(10, 0))
            
            # Switch button
            if available_models:
                switch_button = ttk.Button(buttons_frame, text="🔄 Switch Model", 
                                         command=lambda: self.switch_whisper_model(selector_window, available_models))
                switch_button.pack(side="left", padx=(0, 5))
                
                # Load/Initialize button - if speech system not loaded
                if not self.speech_whisper:
                    load_button = ttk.Button(buttons_frame, text="🚀 Load Speech System", 
                                           command=lambda: self.force_load_speech_system(selector_window))
                    load_button.pack(side="left", padx=(0, 5))
                else:
                    # UNLOAD button - if speech system is loaded
                    unload_button = ttk.Button(buttons_frame, text="🗑️ Unload Model", 
                                             command=lambda: self.unload_speech_system(selector_window))
                    unload_button.pack(side="left", padx=(0, 5))
            
            # Model Manager button
            manager_button = ttk.Button(buttons_frame, text="📦 Model Manager", 
                                       command=lambda: self.open_model_manager())
            manager_button.pack(side="left", padx=(0, 5))
            
            # Debug button - Show what's happening
            debug_button = ttk.Button(buttons_frame, text="🔍 Debug Info", 
                                     command=lambda: self.show_debug_info())
            debug_button.pack(side="left", padx=(0, 5))
            
            # Close button
            close_button = ttk.Button(buttons_frame, text="❌ Close", 
                                    command=selector_window.destroy)
            close_button.pack(side="right")
            
        except Exception as e:
            self.add_chat_message("Error", f"Model selector error: {e}")
    
    def get_available_whisper_models(self):
        """Get list of available Whisper models from your local folder"""
        try:
            models_dir = os.path.join(os.path.dirname(__file__), "models")
            available = []
            
            # Check for each model type
            model_names = ["tiny", "base", "small", "medium", "large-v3"]
            
            for model_name in model_names:
                model_path = os.path.join(models_dir, f"models--Systran--faster-whisper-{model_name}")
                if os.path.exists(model_path):
                    available.append(f"faster-whisper-{model_name}")
            
            return available
            
        except Exception as e:
            self.add_chat_message("Error", f"Error checking models: {e}")
            return []
    
    def switch_whisper_model(self, window, available_models):
        """Switch to selected Whisper model - FORCE COMPLETE RELOAD"""
        try:
            if not hasattr(self, 'model_listbox'):
                return
                
            selection = self.model_listbox.curselection()
            if not selection:
                self.add_chat_message("Error", "Please select a model first")
                return
            
            selected_model = available_models[selection[0]]
            model_name = selected_model.replace("faster-whisper-", "")
            
            self.add_chat_message("System", f"🔄 FORCE RELOAD: Switching to {selected_model}")
            
            # Stop current speech if active
            if self.speech_listening:
                self.stop_speech()
                self.add_chat_message("System", "🔇 Stopped current speech recognition")
            
            # CRITICAL: Force complete reload instead of just switching
            self.add_chat_message("System", "🗑️ Unloading current model...")
            self.speech_whisper = None  # Clear current instance
            
            # Load fresh instance with specific model
            self.add_chat_message("System", f"🚀 Loading fresh instance: {selected_model}")
            
            if SPEECH_AVAILABLE:
                from flexible_whisper import FlexibleWhisper
                self.speech_whisper = FlexibleWhisper()
                
                # Force switch to the specific model
                success = self.speech_whisper.switch_model(model_name)
                if success:
                    # Apply current language setting
                    self.speech_whisper.set_english_only(self.english_only_mode.get())
                    
                    self.add_chat_message("System", f"✅ SUCCESSFULLY LOADED: {self.speech_whisper.selected_model_name}")
                    self.update_whisper_status()
                    window.destroy()  # Close the selector window
                else:
                    self.add_chat_message("Error", f"❌ Failed to load: {selected_model}")
            else:
                self.add_chat_message("Error", "❌ Speech system not available")
                
        except Exception as e:
            self.add_chat_message("Error", f"Model switch error: {e}")
    
    def update_whisper_status(self):
        """Update the visual status indicator for current Whisper model"""
        try:
            if self.speech_whisper and hasattr(self, 'whisper_status_label'):
                model_name = self.speech_whisper.selected_model_name
                
                # Color coding for different models
                if "medium" in model_name.lower():
                    color = "green"
                    icon = "🟢"
                elif "small" in model_name.lower():
                    color = "blue" 
                    icon = "🔵"
                elif "large" in model_name.lower():
                    color = "purple"
                    icon = "🟣"
                else:
                    color = "orange"
                    icon = "🟠"
                
                display_text = f"{icon} {model_name}"
                self.whisper_status_label.config(text=display_text, foreground=color)
                
                # Update the button text to show model type
                if hasattr(self, 'whisper_model_button'):
                    if "medium" in model_name.lower():
                        self.whisper_model_button.config(text="🤖 Medium")
                    elif "small" in model_name.lower():
                        self.whisper_model_button.config(text="🤖 Small")
                    elif "large" in model_name.lower():
                        self.whisper_model_button.config(text="🤖 Large")
                    else:
                        self.whisper_model_button.config(text="🤖 Whisper")
            else:
                if hasattr(self, 'whisper_status_label'):
                    self.whisper_status_label.config(text="🤖 Not Loaded", foreground="gray")
                if hasattr(self, 'whisper_model_button'):
                    self.whisper_model_button.config(text="🤖 Whisper")
                    
        except Exception as e:
            self.add_chat_message("Error", f"Status update error: {e}")
    
    def force_load_speech_system(self, window=None):
        """Force load the speech system if not already loaded"""
        try:
            if self.speech_whisper:
                self.add_chat_message("System", "✅ Speech system already loaded!")
                if window:
                    window.destroy()
                return
            
            self.add_chat_message("System", "🚀 Loading speech system...")
            
            # Initialize speech system
            if SPEECH_AVAILABLE:
                from flexible_whisper import FlexibleWhisper
                self.speech_whisper = FlexibleWhisper()
                
                # Auto-select best model
                if self.speech_whisper.auto_select_model():
                    # Apply current language setting
                    self.speech_whisper.set_english_only(self.english_only_mode.get())
                    
                    # Update visual status
                    self.update_whisper_status()
                    
                    self.add_chat_message("System", f"✅ Speech system loaded: {self.speech_whisper.selected_model_name}")
                    self.add_chat_message("System", "🎯 You can now switch models!")
                    
                    if window:
                        window.destroy()
                        # Reopen selector to show loaded system
                        self.root.after(100, self.show_whisper_selector)
                else:
                    self.add_chat_message("Error", "❌ Failed to auto-select model")
            else:
                self.add_chat_message("Error", "❌ Speech system not available")
                
        except Exception as e:
            self.add_chat_message("Error", f"Failed to load speech system: {e}")
    
    def show_debug_info(self):
        """Show debug information about the current state"""
        try:
            self.add_chat_message("Debug", "🔍 DEBUG INFO:")
            self.add_chat_message("Debug", f"  Speech Available: {SPEECH_AVAILABLE}")
            self.add_chat_message("Debug", f"  Speech Whisper: {self.speech_whisper is not None}")
            
            if self.speech_whisper:
                self.add_chat_message("Debug", f"  Current Model: {self.speech_whisper.selected_model_name}")
                self.add_chat_message("Debug", f"  CUDA Enabled: {self.speech_whisper.use_cuda}")
                self.add_chat_message("Debug", f"  Available Models: {self.speech_whisper.available_models}")
            
            # Check available models in folder
            available = self.get_available_whisper_models()
            self.add_chat_message("Debug", f"  Models in Folder: {available}")
            
            # Check status label
            if hasattr(self, 'whisper_status_label'):
                current_text = self.whisper_status_label.cget("text")
                self.add_chat_message("Debug", f"  Status Label: '{current_text}'")
            
        except Exception as e:
            self.add_chat_message("Error", f"Debug info error: {e}")
    
    def initialize_speech_status(self):
        """Initialize speech system status display on startup"""
        try:
            # Check if we have models available
            available_models = self.get_available_whisper_models()
            
            if available_models:
                # We have models but no speech system loaded yet
                if hasattr(self, 'whisper_status_label'):
                    self.whisper_status_label.config(text="🤖 Ready to Load", foreground="blue")
                if hasattr(self, 'whisper_model_button'):
                    self.whisper_model_button.config(text="🤖 Load Models")
                    
                self.add_chat_message("System", f"🎯 {len(available_models)} Whisper models available")
                self.add_chat_message("System", "💡 Click '🤖 Load Models' to activate speech recognition")
            else:
                # No models found
                if hasattr(self, 'whisper_status_label'):
                    self.whisper_status_label.config(text="❌ No Models", foreground="red")
                if hasattr(self, 'whisper_model_button'):
                    self.whisper_model_button.config(text="🤖 Get Models")
                    
                self.add_chat_message("System", "❌ No Whisper models found")
                self.add_chat_message("System", "💡 Use Model Manager to download models first")
            
        except Exception as e:
            self.add_chat_message("Error", f"Speech status init error: {e}")
    
    def quick_switch_model(self, window, available_models):
        """Quick switch model with double-click - UNLOAD then LOAD"""
        try:
            if not hasattr(self, 'model_listbox'):
                return
                
            selection = self.model_listbox.curselection()
            if not selection:
                self.add_chat_message("Error", "Please select a model first")
                return
            
            selected_model = available_models[selection[0]]
            model_name = selected_model.replace("faster-whisper-", "")
            
            self.add_chat_message("System", f"⚡ QUICK SWITCH: Unloading current model...")
            
            # Step 1: Unload current model completely
            if self.speech_whisper:
                self.unload_speech_system()
            
            # Step 2: Load new model
            self.add_chat_message("System", f"🚀 Loading new model: {selected_model}")
            
            if SPEECH_AVAILABLE:
                from flexible_whisper import FlexibleWhisper
                self.speech_whisper = FlexibleWhisper()
                
                # Force load the specific model
                success = self.speech_whisper.switch_model(model_name)
                if success:
                    # Apply current language setting
                    self.speech_whisper.set_english_only(self.english_only_mode.get())
                    
                    # Update visual status
                    self.update_whisper_status()
                    
                    self.add_chat_message("System", f"✅ QUICK SWITCH SUCCESS: {self.speech_whisper.selected_model_name}")
                    window.destroy()  # Close the selector window
                else:
                    self.add_chat_message("Error", f"❌ Failed to load: {selected_model}")
            else:
                self.add_chat_message("Error", "❌ Speech system not available")
                
        except Exception as e:
            self.add_chat_message("Error", f"Quick switch error: {e}")
    
    def simple_model_switch(self):
        """Cycle through all available models and switch. Always update UI. Safer logic."""
        try:
            # Get available models
            available_models = self.get_available_whisper_models()
            if not available_models:
                self.add_chat_message("Error", "❌ No speech models available to switch.")
                return
            if len(available_models) == 1:
                self.add_chat_message("System", f"Only one model available: {available_models[0]}")
                return

            # If not loaded, load the first model
            if not self.speech_whisper:
                self.add_chat_message("System", f"🚀 Loading speech system with {available_models[0]}...")
                if SPEECH_AVAILABLE:
                    from flexible_whisper import FlexibleWhisper
                    self.speech_whisper = FlexibleWhisper()
                    # Force switch to the first model
                    self.speech_whisper.switch_model(available_models[0].replace("faster-whisper-", ""))
                    self.update_whisper_status()
                return

            # Get current model
            current_model = self.speech_whisper.selected_model_name
            self.add_chat_message("System", f"🔄 Current model: {current_model}")

            # Find the next model in the list
            try:
                idx = [m for m in available_models if m in current_model or m.replace("faster-whisper-", "") in current_model]
                if idx:
                    current_index = available_models.index(idx[0])
                else:
                    current_index = 0
            except Exception:
                current_index = 0
            next_index = (current_index + 1) % len(available_models)
            next_model = available_models[next_index]
            next_model_name = next_model.replace("faster-whisper-", "")
            self.add_chat_message("System", f"🔄 Switching to: {next_model}")

            # Stop current speech if active
            if self.speech_listening:
                self.stop_speech_listening()
                self.add_chat_message("System", "🔇 Stopped speech for model switch")

            # Switch the model
            success = self.speech_whisper.switch_model(next_model_name)
            if success:
                self.speech_whisper.set_english_only(self.english_only_mode.get())
                self.update_whisper_status()
                self.add_chat_message("System", f"✅ SWITCHED TO: {self.speech_whisper.selected_model_name}")
            else:
                self.add_chat_message("Error", f"❌ Failed to switch to: {next_model}")
        except Exception as e:
            self.add_chat_message("Error", f"Model switch error: {e}")

    def start_periodic_status_check(self):
        """Start periodic checking for external model changes - DETECTS TERMINAL SWITCHES!"""
        try:
            self.check_for_model_changes()
            # Check every 2 seconds for external model changes
            self.root.after(2000, self.start_periodic_status_check)
        except Exception as e:
            # If something goes wrong, try again in 5 seconds
            self.root.after(5000, self.start_periodic_status_check)
    
    def check_for_model_changes(self):
        """Check if model was changed externally and update the interface - YOUR SYNC SYSTEM!"""
        try:
            if self.speech_whisper and hasattr(self, 'whisper_status_label'):
                # Get what the interface currently shows
                current_displayed = self.whisper_status_label.cget("text")
                
                # Get what the actual loaded model is
                actual_model = self.speech_whisper.selected_model_name
                
                # Check if they don't match (external change detected!)
                if actual_model and actual_model not in current_displayed:
                    self.add_chat_message("System", f"🔄 EXTERNAL MODEL CHANGE DETECTED!")
                    self.add_chat_message("System", f"📢 Terminal switched to: {actual_model}")
                    self.add_chat_message("System", f"📱 Updating main interface...")
                    self.update_whisper_status()
                    
        except Exception as e:
            # Silent error handling for background checking
            pass

    def manual_sync_models(self):
        """Manual button to sync model display - INSTANT FIX!"""
        try:
            if self.speech_whisper:
                actual_model = self.speech_whisper.selected_model_name
                self.add_chat_message("System", f"🔄 MANUAL SYNC: Current model is {actual_model}")
                self.update_whisper_status()
                self.add_chat_message("System", f"✅ Interface updated to match actual model!")
            else:
                self.add_chat_message("System", f"❌ No speech system loaded to sync")
        except Exception as e:
            self.add_chat_message("Error", f"Manual sync error: {e}")

    def unload_speech_system(self, window=None):
        """Completely unload the speech system - CLEAN SLATE"""
        try:
            self.add_chat_message("System", "🗑️ Unloading speech system...")
            
            # Stop any active speech recognition
            if self.speech_listening:
                self.stop_speech()
                self.add_chat_message("System", "🔇 Stopped active speech recognition")
            
            # Clear the speech system
            self.speech_whisper = None
            
            # Update visual indicators
            if hasattr(self, 'whisper_status_label'):
                self.whisper_status_label.config(text="🤖 Not Loaded", foreground="gray")
            if hasattr(self, 'whisper_model_button'):
                self.whisper_model_button.config(text="🤖 Load Models")
            
            self.add_chat_message("System", "✅ Speech system unloaded - ready for fresh model")
            
            if window:
                window.destroy()
                # Reopen selector to show unloaded state
                self.root.after(100, self.show_whisper_selector)
                
        except Exception as e:
            self.add_chat_message("Error", f"Unload error: {e}")

    def open_model_manager(self):
        """Open the model manager in a new window - YOUR CONTROL PANEL!"""
        try:
            import subprocess
            import sys
            
            # Run the model manager script
            self.add_chat_message("System", "🤖 Opening Model Manager...")
            self.add_chat_message("System", "💡 Download, upgrade, and manage your Whisper models!")
            
            # Launch model_manager.py in a new process
            subprocess.Popen([sys.executable, "model_manager.py"], 
                           cwd=os.path.dirname(__file__),
                           creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0)
            
            self.add_chat_message("System", "✅ Model Manager launched in new window!")
            self.add_chat_message("System", "🎯 You can now:")
            self.add_chat_message("System", "  • Download fresh models")
            self.add_chat_message("System", "  • Update existing models")
            self.add_chat_message("System", "  • Clean up cached files")
            self.add_chat_message("System", "  • See exactly what you have")
            
        except Exception as e:
            self.add_chat_message("Error", f"Failed to open Model Manager: {e}")
            self.add_chat_message("System", "💡 Try running 'python model_manager.py' manually in terminal")

    def create_input_context_menu(self):
        """Create right-click context menu for input area"""
        self.input_context_menu = tk.Menu(self.root, tearoff=0)
        self.input_context_menu.add_command(label="Copy", command=self.copy_input_text)
        self.input_context_menu.add_command(label="Paste", command=self.paste_input_text)
        self.input_context_menu.add_separator()
        self.input_context_menu.add_command(label="Select All", command=self.select_all_input)
        self.input_context_menu.add_command(label="Copy All Input", command=self.copy_all_input)
        self.input_context_menu.add_command(label="Clear Input", command=self.clear_message_input)
        self.input_context_menu.add_separator()
        self.input_context_menu.add_command(label="🛡️ Copy Last Safety Segment", command=self.copy_last_safety_segment)
        
        # Bind right-click to show menu
        self.message_entry.bind("<Button-3>", self.show_input_context_menu)

    def show_input_context_menu(self, event):
        """Show the input context menu"""
        try:
            self.input_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.input_context_menu.grab_release()

    def copy_input_text(self):
        """Copy selected text from input to clipboard"""
        try:
            selected_text = self.message_entry.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.add_chat_message("System", "📋 Selected text copied to clipboard")
        except tk.TclError:
            # No text selected, copy current line/paragraph
            try:
                current_pos = self.message_entry.index(tk.INSERT)
                line_start = current_pos.split('.')[0] + '.0'
                line_end = current_pos.split('.')[0] + '.end'
                line_text = self.message_entry.get(line_start, line_end)
                if line_text.strip():
                    self.root.clipboard_clear()
                    self.root.clipboard_append(line_text)
                    self.add_chat_message("System", "📋 Current line copied to clipboard")
            except:
                pass

    def paste_input_text(self):
        """Paste text from clipboard to input"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.message_entry.insert(tk.INSERT, clipboard_text)
            self.add_chat_message("System", "📋 Text pasted from clipboard")
        except tk.TclError:
            self.add_chat_message("System", "📋 No text in clipboard to paste")

    def select_all_input(self):
        """Select all text in input area"""
        self.message_entry.tag_add(tk.SEL, "1.0", tk.END)
        self.message_entry.mark_set(tk.INSERT, "1.0")
        self.message_entry.see(tk.INSERT)

    def copy_all_input(self):
        """Copy all text from input area to clipboard"""
        try:
            all_text = self.get_message_text()
            if all_text.strip():
                self.root.clipboard_clear()
                self.root.clipboard_append(all_text)
                self.add_chat_message("System", f"📋 Copied {len(all_text)} characters to clipboard")
            else:
                self.add_chat_message("System", "📋 Input is empty - nothing to copy")
        except Exception as e:
            self.add_chat_message("Error", f"Failed to copy input: {e}")

    # ===== SAFETY NET SYSTEM - ULTIMATE BACKUP FOR CHATGPT FAILURES =====
    
    def toggle_safety_net(self):
        """Toggle the Safety Net mode - pure text accumulation with segment rotation"""
        try:
            self.safety_net_active.set(not self.safety_net_active.get())
            
            if self.safety_net_active.get():
                # ACTIVATE SAFETY NET MODE - No button to update, just enable feature
                self.add_chat_message("System", "🛡️ SAFETY NET ACTIVATED!")
                self.add_chat_message("System", "💡 Mode: Pure text accumulation only")
                self.add_chat_message("System", "⏸️ 5-second pauses create new segments")
                self.add_chat_message("System", "🔄 Keeps last 10 segments, auto-deletes oldest")
                self.add_chat_message("System", "📋 Click 'Copy Last' to get latest segment")
                self.add_chat_message("System", "🚫 NO auto-sending - just pure capture!")
                
                # Load existing segments if available
                self.load_safety_net_data()
                
                # Show current status
                self.add_chat_message("System", f"📊 Current segments: {len(self.safety_net_segments)}")
                
            else:
                # DEACTIVATE SAFETY NET MODE - No button to update
                self.add_chat_message("System", "🛡️ Safety Net deactivated")
                
                # Cancel any active pause timer
                if self.safety_net_pause_timer:
                    self.root.after_cancel(self.safety_net_pause_timer)
                    self.safety_net_pause_timer = None
                
                # Save current data
                self.save_safety_net_data()
                
        except Exception as e:
            self.add_chat_message("Error", f"Safety Net toggle error: {e}")
            # Force safe state on error
            self.safety_net_active.set(False)
    
    def safety_net_add_text(self, text):
        """Add text to safety net accumulation (called from speech system)"""
        if not self.safety_net_active.get():
            return
            
        try:
            # Add to current accumulation
            self.safety_net_current += " " + text.strip()
            
            # Reset pause timer - new speech detected
            if self.safety_net_pause_timer:
                self.root.after_cancel(self.safety_net_pause_timer)
            
            # Start new pause timer (5 seconds)
            self.safety_net_pause_timer = self.root.after(
                self.safety_net_pause_duration * 1000,
                self.safety_net_create_segment
            )
            
            self.add_chat_message("Debug", f"🛡️ Safety Net: Added text, timer reset")
            
        except Exception as e:
            self.add_chat_message("Error", f"Safety Net add text error: {e}")
    
    def safety_net_create_segment(self):
        """Create new segment from current accumulation (pause detected)"""
        try:
            if not self.safety_net_current.strip():
                return
                
            # Create new segment with timestamp
            segment = {
                "text": self.safety_net_current.strip(),
                "timestamp": datetime.now().isoformat(),
                "length": len(self.safety_net_current.strip())
            }
            
            # Add to segments list
            self.safety_net_segments.append(segment)
            
            # Keep only last 10 segments
            if len(self.safety_net_segments) > self.safety_net_max_segments:
                removed = self.safety_net_segments.pop(0)
                self.add_chat_message("System", f"🗑️ Auto-deleted oldest segment ({removed['length']} chars)")
            
            # Clear current accumulation
            self.safety_net_current = ""
            
            # Save to file
            self.save_safety_net_data()
            
            self.add_chat_message("System", f"🛡️ NEW SEGMENT CREATED! ({segment['length']} chars)")
            self.add_chat_message("System", f"📊 Total segments: {len(self.safety_net_segments)}")
            
        except Exception as e:
            self.add_chat_message("Error", f"Safety Net segment creation error: {e}")
    
    def copy_last_safety_segment(self):
        """Copy the last completed segment to clipboard"""
        try:
            if not self.safety_net_segments:
                self.add_chat_message("System", "📋 No safety net segments available")
                return
                
            last_segment = self.safety_net_segments[-1]
            text = last_segment["text"]
            
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            
            self.add_chat_message("System", f"📋 Copied last segment ({len(text)} chars)")
            self.add_chat_message("System", f"🕐 From: {last_segment['timestamp']}")
            
        except Exception as e:
            self.add_chat_message("Error", f"Copy last segment error: {e}")
    
    def load_safety_net_data(self):
        """Load safety net data from JSON file"""
        try:
            if os.path.exists(self.safety_net_file):
                with open(self.safety_net_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.safety_net_segments = data.get('segments', [])
                    self.safety_net_current = data.get('current', "")
                    
                self.add_chat_message("System", f"📂 Loaded {len(self.safety_net_segments)} segments from file")
            else:
                self.safety_net_segments = []
                self.safety_net_current = ""
                
        except Exception as e:
            self.add_chat_message("Error", f"Safety Net load error: {e}")
            self.safety_net_segments = []
            self.safety_net_current = ""  # Fixed: was incorrectly set to []
    
    def save_safety_net_data(self):
        """Save safety net data to JSON file"""
        try:
            data = {
                "segments": self.safety_net_segments,
                "current": self.safety_net_current,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.safety_net_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            self.add_chat_message("Debug", f"💾 Safety net data saved ({len(self.safety_net_segments)} segments)")
            
        except Exception as e:
            self.add_chat_message("Error", f"Safety Net save error: {e}")

    def create_context_menu(self):
        """Create right-click context menu for chat area"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Select All", command=self.select_all_text)
        self.context_menu.add_command(label="Clear Chat", command=self.clear_chat)
        
        # Bind right-click to show menu
        self.chat_text.bind("<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        """Show the context menu"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            selected_text = self.chat_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # No text selected
            
    def paste_text(self):
        """Paste text from clipboard to message entry"""
        try:
            clipboard_text = self.root.clipboard_get()
            self.message_entry.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass  # No text in clipboard
            
    def select_all_text(self):
        """Select all text in chat area"""
        self.chat_text.tag_add(tk.SEL, "1.0", tk.END)
        
    def clear_chat(self):
        """Clear the screen display and optionally memory"""
        self.chat_text.delete(1.0, tk.END)
        self.add_chat_message("System", "🧹 Screen display cleared")
        self.add_chat_message("System", "💾 Memory files preserved (chat_memory.json, input_memory.json)")
        self.add_chat_message("System", "⚠️ To clear ALL memory permanently, use a dedicated 'Clean Memory' button")
        
    def launch_test_window(self):
        """Launch the test target window for debugging"""
        try:
            import subprocess
            import sys
            subprocess.Popen([sys.executable, "test_target_window.py"])
            self.add_chat_message("Debug", "🪟 Test target window launched!")
            # Auto-refresh windows after a short delay
            self.root.after(1000, self.refresh_windows)
        except Exception as e:
            self.add_chat_message("Error", f"Failed to launch test window: {e}")
    
    def show_visual_log(self):
        """Show the visual log window"""
        try:
            if self.visual_log_window is None:
                self.visual_log_window = VisualLogWindow(self, self.vision_log_file)
            
            self.visual_log_window.show_window()
            self.add_chat_message("System", "📋 Visual log window opened")
            
        except Exception as e:
            self.add_chat_message("Error", f"Failed to open visual log window: {e}")
    
    def clean_visual_log(self):
        """Clean the visual log JSON file for fresh start"""
        try:
            # Create empty log structure
            empty_log = {"entries": []}
            
            # Write to file
            with open(self.vision_log_file, 'w', encoding='utf-8') as f:
                json.dump(empty_log, f, indent=2, ensure_ascii=False)
            
            self.add_chat_message("System", "🧹 Visual log cleaned! Fresh start ready.")
            
            # Note: Visual log window will automatically detect the file change and update
            
            # Also clean up old screenshot files for complete cleanup
            try:
                if os.path.exists(self.screenshots_dir):
                    screenshot_files = [f for f in os.listdir(self.screenshots_dir) 
                                      if f.startswith("screen_") and f.endswith(".png")]
                    for file in screenshot_files:
                        os.remove(os.path.join(self.screenshots_dir, file))
                    
                    if screenshot_files:
                        self.add_chat_message("System", f"🗑️ Removed {len(screenshot_files)} old screenshots")
                        
            except Exception as e:
                self.add_chat_message("Debug", f"Screenshot cleanup warning: {e}")
                
        except Exception as e:
            self.add_chat_message("Error", f"Failed to clean visual log: {e}")
    
    def test_delivery(self):
        """Test the delivery system with enhanced debugging"""
        if not self.selected_window_handle:
            self.add_chat_message("Error", "❌ No target window selected!")
            return
            
        if not self.direct_output_enabled.get():
            self.add_chat_message("Error", "❌ Direct output is disabled! Click 'Direct Output: OFF' to enable.")
            return
        
        test_message = f"🧪 Test delivery at {datetime.now().strftime('%H:%M:%S')}"
        
        # Show detailed window analysis
        try:
            window_title = self.selected_window.get()
            rect = win32gui.GetWindowRect(self.selected_window_handle)
            is_visible = win32gui.IsWindowVisible(self.selected_window_handle)
            is_minimized = win32gui.IsIconic(self.selected_window_handle)
            
            self.add_chat_message("Debug", f"🔍 DETAILED WINDOW ANALYSIS:")
            self.add_chat_message("Debug", f"  Title: {window_title}")
            self.add_chat_message("Debug", f"  Handle: {self.selected_window_handle}")
            self.add_chat_message("Debug", f"  Position: {rect}")
            self.add_chat_message("Debug", f"  Size: {rect[2]-rect[0]}x{rect[3]-rect[1]}")
            self.add_chat_message("Debug", f"  Visible: {is_visible}")
            self.add_chat_message("Debug", f"  Minimized: {is_minimized}")
            
            # Test window interaction step by step
            self.add_chat_message("Debug", "📋 STEP-BY-STEP TEST:")
            
        except Exception as e:
            self.add_chat_message("Debug", f"Window analysis failed: {e}")
        
        # Attempt delivery with detailed feedback
        self.add_chat_message("System", "🧪 Starting enhanced test delivery...")
        success = self.send_direct_to_window(test_message)
        
        if success:
            self.add_chat_message("System", "✅ Test delivery completed!")
            self.add_chat_message("System", "👀 CHECK TARGET WINDOW - Did the text appear?")
            self.add_chat_message("System", "If no text appeared, try clicking in the input field manually first")
        else:
            self.add_chat_message("Error", "❌ Test delivery failed!")
            self.add_chat_message("System", "💡 TROUBLESHOOTING TIPS:")
            self.add_chat_message("System", "1. Make sure target window has a text input field")
            self.add_chat_message("System", "2. Click in the input field manually, then test again")
            self.add_chat_message("System", "3. Try a different window (like Notepad) for testing")
            self.add_chat_message("System", "4. Check if the window is actually receiving focus")
    
    def show_debug_payload(self):
        """Show current system status for debugging"""
        try:
            # Show current system status
            self.add_chat_message("Debug", "📦 SYSTEM STATUS:")
            self.add_chat_message("Debug", f"Direct Output: {'ON' if self.direct_output_enabled.get() else 'OFF'}")
            self.add_chat_message("Debug", f"Visual Context: {'Enabled' if self.include_visual_context.get() else 'Disabled'}")
            self.add_chat_message("Debug", f"Auto-Press Enter: {'Enabled' if self.auto_press_enter.get() else 'Disabled'}")
            
            # Show target window info
            if self.selected_window_handle:
                window_title = self.selected_window.get()
                self.add_chat_message("Debug", f"Target Window: {window_title}")
                self.add_chat_message("Debug", f"Window Handle: {self.selected_window_handle}")
            else:
                self.add_chat_message("Debug", "Target Window: None selected")
            
            # Show visual context status
            visual_context = self.get_simple_visual_context()
            if visual_context:
                preview = visual_context[:100] + "..." if len(visual_context) > 100 else visual_context
                self.add_chat_message("Debug", f"Latest Visual Context: {preview}")
            else:
                self.add_chat_message("Debug", "Latest Visual Context: None available")
            
        except Exception as e:
            self.add_chat_message("Error", f"Failed to show debug info: {e}")
        
    # ===== WINDOW TARGETING METHODS =====
    
    def refresh_windows(self):
        """Refresh the list of available windows"""
        try:
            windows = []
            
            def enum_windows_callback(hwnd, windows_list):
                if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    # Filter out empty titles and system windows
                    if title and len(title.strip()) > 0 and title != "Program Manager":
                        windows_list.append((hwnd, title))
                return True
            
            # Get all visible windows
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Also try pygetwindow for additional windows
            try:
                gw_windows = gw.getAllWindows()
                for window in gw_windows:
                    if window.title and window.visible and window.title.strip():
                        # Avoid duplicates
                        if not any(w[1] == window.title for w in windows):
                            try:
                                hwnd = window._hWnd if hasattr(window, '_hWnd') else None
                                if hwnd:
                                    windows.append((hwnd, window.title))
                            except:
                                pass
            except Exception as e:
                print(f"PyGetWindow error: {e}")
            
            # Update the dropdown
            self.target_windows = windows
            window_titles = [title for hwnd, title in windows]
            self.window_combo['values'] = window_titles
            
            if window_titles:
                self.add_chat_message("System", f"Found {len(window_titles)} target windows")
            else:
                self.add_chat_message("System", "No target windows found")
                
        except Exception as e:
            self.add_chat_message("Error", f"Failed to refresh windows: {e}")
    
    def on_window_selected(self, event=None):
        """Handle window selection"""
        selected_title = self.selected_window.get()
        if selected_title:
            # Find the window handle
            for hwnd, title in self.target_windows:
                if title == selected_title:
                    self.selected_window_handle = hwnd
                    self.add_chat_message("System", f"Selected target window: {title}")
                    break
    
    def toggle_direct_output(self):
        """Toggle direct output to selected window. Always stop speech listening if active."""
        if not self.selected_window_handle:
            self.add_chat_message("Error", "No target window selected. Please select a window first.")
            return

        # Always stop speech listening if active before switching mode
        if self.speech_listening:
            self.stop_speech_listening()
            self.add_chat_message("System", "🔇 Speech listening stopped due to mode switch.")

        self.direct_output_enabled.set(not self.direct_output_enabled.get())

        if self.direct_output_enabled.get():
            self.direct_output_button.config(text="Direct Output: ON")
            window_title = self.selected_window.get()
            self.add_chat_message("System", f"🎯 Direct output ENABLED to: {window_title}")
            self.add_chat_message("System", "💡 Now separators come from SENDING, not silence")
            # Clear any auto-silence countdown when switching to sending mode
            if hasattr(self, 'auto_silence_countdown_label'):
                self.auto_silence_countdown_label.config(text="")
        else:
            self.direct_output_button.config(text="Direct Output: OFF")
            self.add_chat_message("System", "🎯 Direct output DISABLED")
            self.add_chat_message("System", "💡 Now in accumulation mode - silence separators available")
    
    def get_latest_visual_context(self):
        """Get the latest visual context from vision log"""
        try:
            if os.path.exists(self.vision_log_file):
                with open(self.vision_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    entries = data.get('entries', [])
                    if entries:
                        latest = entries[-1]
                        # Return a shortened version of the interpretation
                        interpretation = latest.get('interpreted_text', '')
                        if len(interpretation) > 300:
                            interpretation = interpretation[:300] + "..."
                        return f"[{latest.get('timestamp', '')}] {interpretation}"
        except Exception as e:
            print(f"Error getting visual context: {e}")
        return None
        
    # ===== SIMPLE MESSAGE SYSTEM =====
    
    def get_simple_visual_context(self):
        """Simply get the latest visual interpretation from JSON log"""
        try:
            if not os.path.exists(self.vision_log_file):
                return None
                
            with open(self.vision_log_file, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
                
            entries = log_data.get('entries', [])
            if entries:
                latest = entries[-1]  # Get the most recent entry
                return latest.get('interpreted_text', '')
                
        except Exception as e:
            print(f"Error getting visual context: {e}")
        return None
    
    def get_latest_screenshot_data(self):
        """Get latest screenshot data for unified delivery"""
        try:
            # Check if screenshots directory exists
            if not os.path.exists(self.screenshots_dir):
                return None
                
            # Get all screenshot files
            screenshot_files = [f for f in os.listdir(self.screenshots_dir) 
                              if f.startswith("screen_") and f.endswith(".png")]
            
            if not screenshot_files:
                return None
            
            # Get the most recent screenshot by modification time
            latest_file = max(screenshot_files, 
                            key=lambda f: os.path.getmtime(os.path.join(self.screenshots_dir, f)))
            latest_path = os.path.join(self.screenshots_dir, latest_file)
            
            # Get file modification timestamp
            modification_time = os.path.getmtime(latest_path)
            screenshot_timestamp = datetime.fromtimestamp(modification_time).isoformat()
            
            # Try to get interpretation from vision log
            interpretation = None
            try:
                if os.path.exists(self.vision_log_file):
                    with open(self.vision_log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    
                    # Find interpretation for this screenshot
                    entries = log_data.get('entries', [])
                    for entry in reversed(entries):  # Start from most recent
                        if entry.get('screenshot_filename') == latest_file:
                            interpretation = entry.get('interpreted_text', '')
                            break
                    
                    # If no exact match, use the most recent interpretation
                    if not interpretation and entries:
                        interpretation = entries[-1].get('interpreted_text', '')
                        
            except Exception as e:
                print(f"Error getting interpretation: {e}")
            
            if not interpretation:
                interpretation = "No interpretation available"
            
            return {
                "filename": latest_file,
                "filepath": latest_path,
                "timestamp": screenshot_timestamp,
                "interpretation": interpretation,
                "file_size": os.path.getsize(latest_path)
            }
            
        except Exception as e:
            print(f"Error getting latest screenshot data: {e}")
        return None
    
    def interpret_screenshot_full(self, filepath):
        """Get full visual interpretation (not truncated) from screenshot"""
        try:
            # Read and encode image
            with open(filepath, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send to Ollama for full interpretation
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.selected_model.get(),
                    "prompt": "Provide a comprehensive, detailed analysis of this screenshot. Include ALL visible text content, UI elements, applications, windows, buttons, menus, and any important visual information. Be thorough and complete.",
                    "images": [image_data],
                    "stream": False
                },
                timeout=60,  # Longer timeout for comprehensive analysis
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('response', 'No interpretation received')
            else:
                self.add_chat_message("Debug", f"Screenshot interpretation failed: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            self.add_chat_message("Debug", f"Screenshot interpretation error: {e}")
            return None
    
    def send_direct_to_window(self, message):
        """BULLETPROOF delivery system - multiple methods for rock-solid reliability"""
        try:
            if not self.direct_output_enabled.get() or not self.selected_window_handle:
                self.add_chat_message("Error", "❌ Direct output disabled or no window selected!")
                return False
            
            window_title = self.selected_window.get()
            self.add_chat_message("System", f"🎯 BULLETPROOF DELIVERY to: {window_title}")
            
            # STEP 1: Ensure window is ready and focused properly
            if not self.ensure_window_focus_bulletproof(self.selected_window_handle):
                self.add_chat_message("Error", "❌ Failed to focus target window")
                return False
            
            # STEP 2: Bulletproof clipboard preparation
            try:
                # Store original clipboard safely
                original_clipboard = ""
                try:
                    original_clipboard = pyperclip.paste()
                except:
                    pass
                
                # Set our message to clipboard with verification
                pyperclip.copy(message)
                time.sleep(0.3)  # Give clipboard time to update properly
                
                # Verify clipboard was set correctly
                clipboard_check = pyperclip.paste()
                if clipboard_check != message:
                    self.add_chat_message("Error", "❌ Clipboard verification failed")
                    return False
                    
                self.add_chat_message("Debug", f"✅ Clipboard verified: {len(message)} chars")
                
            except Exception as e:
                self.add_chat_message("Error", f"❌ Clipboard setup failed: {e}")
                return False
            
            # STEP 3: TRIPLE-LAYER DELIVERY - Try multiple methods for reliability
            delivery_success = False
            
            # Method 1: Controlled PyAutoGUI with proper timing
            try:
                self.add_chat_message("Debug", "🔄 Method 1: Controlled delivery...")
                
                # Re-ensure window focus
                win32gui.SetForegroundWindow(self.selected_window_handle)
                time.sleep(0.4)  # Longer wait for stability
                
                # Clear any existing selection safely
                pyautogui.hotkey('ctrl', 'a')
                time.sleep(0.2)
                
                # Paste with controlled timing
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(0.4)  # Wait for paste to complete
                
                # Auto-press Enter if enabled (with verification)
                if self.auto_press_enter.get():
                    # Add extra delay for Vision Image mode to ensure screenshot upload
                    delay = 1.2 if self.vision_mode.get() == "Vision Image" else 0.2
                    time.sleep(delay)  # Increased delay for image mode
                    pyautogui.press('enter')
                    time.sleep(0.2)
                    self.add_chat_message("Debug", f"✅ Auto-Enter pressed with timing (delay: {delay}s)")
                
                delivery_success = True
                self.add_chat_message("Debug", "✅ Method 1 succeeded!")
                
            except Exception as e:
                self.add_chat_message("Debug", f"⚠️ Method 1 failed: {e}")
            
            # Method 2: Direct Win32 API (if Method 1 failed)
            if not delivery_success:
                try:
                    self.add_chat_message("Debug", "🔄 Method 2: Win32 API delivery...")
                    
                    # Use Win32 to send keystrokes directly
                    # win32api and win32con already imported at top
                    
                    # Send Ctrl+A (select all)
                    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    win32api.keybd_event(ord('A'), 0, 0, 0)
                    win32api.keybd_event(ord('A'), 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.2)
                    
                    # Send Ctrl+V (paste)
                    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                    win32api.keybd_event(ord('V'), 0, 0, 0)
                    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.3)
                    
                    # Send Enter if enabled
                    if self.auto_press_enter.get():
                        time.sleep(0.2)
                        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                    
                    delivery_success = True
                    self.add_chat_message("Debug", "✅ Method 2 succeeded!")
                    
                except Exception as e:
                    self.add_chat_message("Debug", f"⚠️ Method 2 failed: {e}")
            
            # Method 3: Tkinter clipboard with extended retry (final fallback)
            if not delivery_success:
                try:
                    self.add_chat_message("Debug", "🔄 Method 3: Tkinter fallback...")
                    
                    # Use Tkinter's clipboard system
                    self.root.clipboard_clear()
                    self.root.clipboard_append(message)
                    self.root.update_idletasks()  # Force clipboard update
                    time.sleep(0.3)
                    
                    # Focus window again
                    win32gui.SetForegroundWindow(self.selected_window_handle)
                    time.sleep(0.4)
                    
                    # Simple paste
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.3)
                    
                    if self.auto_press_enter.get():
                        time.sleep(0.2)
                        pyautogui.press('enter')
                    
                    delivery_success = True
                    self.add_chat_message("Debug", "✅ Method 3 succeeded!")
                    
                except Exception as e:
                    self.add_chat_message("Debug", f"⚠️ Method 3 failed: {e}")
            
            # STEP 4: Restore original clipboard safely
            try:
                if original_clipboard:
                    # Delay clipboard restoration to avoid interference
                    self.root.after(1000, lambda: pyperclip.copy(original_clipboard))
                    self.add_chat_message("Debug", "🔄 Original clipboard will be restored")
            except:
                pass
            
            # STEP 5: Report final result
            if delivery_success:
                self.add_chat_message("System", f"✅ BULLETPROOF DELIVERY SUCCESS!")
                self.add_chat_message("System", f"📦 Delivered {len(message)} characters reliably")
                if self.auto_press_enter.get():
                    self.add_chat_message("System", "⚡ Message automatically sent!")
                return True
            else:
                self.add_chat_message("Error", "❌ ALL DELIVERY METHODS FAILED!")
                self.add_chat_message("System", "💡 Try: 1) Click in target input field manually")
                self.add_chat_message("System", "💡 Try: 2) Test with Notepad first") 
                return False
                
        except Exception as e:
            self.add_chat_message("Error", f"❌ Bulletproof delivery error: {e}")
            return False

    def ensure_window_focus_bulletproof(self, hwnd):
        """BULLETPROOF window focusing with multiple attempts and verification"""
        try:
            # Check if window exists first
            if not win32gui.IsWindow(hwnd):
                self.add_chat_message("Error", "❌ Target window no longer exists")
                return False
            
            # Get window info for debugging
            window_title = win32gui.GetWindowText(hwnd)
            is_visible = win32gui.IsWindowVisible(hwnd)
            is_minimized = win32gui.IsIconic(hwnd)
            
            self.add_chat_message("Debug", f"🔍 Window: '{window_title}' - Visible: {is_visible}, Minimized: {is_minimized}")
            
            # STEP 1: Restore window if minimized
            if is_minimized:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.3)
                self.add_chat_message("Debug", "📖 Window restored from minimized state")
            
            # STEP 2: Bring window to front with multiple attempts
            attempts = 3
            for attempt in range(attempts):
                try:
                    # Try different methods to bring window to front
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    time.sleep(0.1)
                    win32gui.BringWindowToTop(hwnd)
                    time.sleep(0.1)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)
                    
                    # Verify focus
                    current_focus = win32gui.GetForegroundWindow()
                    if current_focus == hwnd:
                        self.add_chat_message("Debug", f"✅ Window focused successfully (attempt {attempt + 1})")
                        return True
                    else:
                        self.add_chat_message("Debug", f"⚠️ Focus attempt {attempt + 1} failed")
                        
                except Exception as e:
                    self.add_chat_message("Debug", f"⚠️ Focus attempt {attempt + 1} error: {e}")
                
                # Brief pause before retry
                if attempt < attempts - 1:
                    time.sleep(0.2)
            
            # STEP 3: Alternative focus method using SetActiveWindow
            try:
                self.add_chat_message("Debug", "🔄 Trying alternative focus method...")
                win32gui.SetActiveWindow(hwnd)
                time.sleep(0.3)
                
                current_focus = win32gui.GetForegroundWindow()
                if current_focus == hwnd:
                    self.add_chat_message("Debug", "✅ Alternative focus method succeeded")
                    return True
                    
            except Exception as e:
                self.add_chat_message("Debug", f"⚠️ Alternative focus failed: {e}")
            
            # STEP 4: Final verification
            final_focus = win32gui.GetForegroundWindow()
            if final_focus == hwnd:
                self.add_chat_message("Debug", "✅ Window focus verified")
                return True
            else:
                self.add_chat_message("Debug", f"❌ Focus failed - Current: {final_focus}, Target: {hwnd}")
                return False
                
        except Exception as e:
            self.add_chat_message("Error", f"❌ Window focus error: {e}")
            return False
            
            # Verify focus
            current_focus = win32gui.GetForegroundWindow()
            return current_focus == hwnd
            
        except Exception:
            return False

    def add_chat_message(self, sender: str, message: str):
        """Add message to chat area and save to memory"""
        self.chat_text.insert(tk.END, f"{sender}: {message}\n")
        self.chat_text.see(tk.END)
        
        # AUTOMATICALLY SAVE TO MEMORY SYSTEM
        try:
            message_type = sender.lower()
            self.save_chat_memory(message_type, sender, message)
        except Exception as e:
            print(f"Memory save error in add_chat_message: {e}")
        
    def add_initial_instructions(self):
        """Add initial instructions to the chat"""
        self.add_chat_message("System", "🎯 Visual Interpretation System v2.0 - SPEECH KEYWORD ACTIVATION!")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "✨ New Features:")
        self.add_chat_message("System", "📥 Window Selection: Choose any open window as output target")
        self.add_chat_message("System", "📤 Unified Message Delivery: Complete payload with visual data")
        self.add_chat_message("System", "🖼️ Full Visual Interpretation: Comprehensive screenshot analysis")
        self.add_chat_message("System", "⚡ Burst Delivery: Instant paste with no typing delays")
        self.add_chat_message("System", "🚀 Auto-Press Enter: Automatically sends messages after delivery!")
        self.add_chat_message("System", "🎯 KEYWORD ACTIVATION: Say trigger words to auto-send!")
        self.add_chat_message("System", "⬆️⬇️ Message History: Use Up/Down arrows to navigate previous messages")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "🎤 SPEECH-TO-TEXT WITH DUAL ACTIVATION MODES:")
        self.add_chat_message("System", "1. Click 🎤 TTS to start listening")
        self.add_chat_message("System", "2. Talk naturally - watch text accumulate in real-time")
        self.add_chat_message("System", "3A. KEYWORD MODE - Say trigger words to auto-send:")
        self.add_chat_message("System", "    • 'send it' • 'send' • 'I'm done' • 'done'")
        self.add_chat_message("System", "    • 'go' • 'submit' • 'fire' • 'execute' • 'deliver'")
        self.add_chat_message("System", "3B. SILENCE MODE - Just pause for 2-5 seconds:")
        self.add_chat_message("System", "    • Choose duration: 2s/3s/4s/5s")
        self.add_chat_message("System", "    • Stop talking → auto-send after pause")
        self.add_chat_message("System", "    • Perfect for natural conversation flow")
        self.add_chat_message("System", "4. Message automatically sends - continue talking for next message!")
        self.add_chat_message("System", "5. Mix and match: Use keywords for precision, silence for flow")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "🔧 How to Use Unified Delivery:")
        self.add_chat_message("System", "1. Click 🔄 to refresh available windows")
        self.add_chat_message("System", "2. Select target window from dropdown")
        self.add_chat_message("System", "3. Enable 'Include Visual Context' for complete payloads")
        self.add_chat_message("System", "4. Click 'Direct Output: OFF' to enable targeting")
        self.add_chat_message("System", "5. Enable '⚡ Auto-Press Enter' for automatic message sending")
        self.add_chat_message("System", "6. Enable '🎯 Keyword Activation' for hands-free operation")
        self.add_chat_message("System", "7. Messages now include full visual context + metadata!")
        self.add_chat_message("System", "   📌 Delivered via instant clipboard paste (Ctrl+V)")
        self.add_chat_message("System", "   🚀 Plus automatic Enter press when enabled!")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "⌨️ Message Entry:")
        self.add_chat_message("System", "• Type your message and press Enter to send")
        self.add_chat_message("System", "• Use ⬆️⬇️ arrow keys to navigate message history")
        self.add_chat_message("System", "• Compatible with speech-to-text software")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "📸 Screenshot System:")
        self.add_chat_message("System", "• Select interval (3s/5s/10s) and click 'Start Rotation'")
        self.add_chat_message("System", "• AI will continuously interpret your screen")
        self.add_chat_message("System", "• Everything logged to vision_log.json")
        self.add_chat_message("System", "")
        self.add_chat_message("System", "🎬 ULTIMATE HANDS-FREE EXPERIENCE:")
        self.add_chat_message("System", "• Start speech listening + screenshot rotation")
        self.add_chat_message("System", "• Talk naturally while AI watches your screen")
        self.add_chat_message("System", "• Say 'send it' to deliver messages instantly")
        self.add_chat_message("System", "• Perfect for gaming, movies, or multitasking!")
        self.add_chat_message("System", "")
        
    def send_message(self, event=None):
        """Send message to selected model or redirect to target window - SEGMENTED SENDS ONLY!"""
        try:
            vision_mode = self.vision_mode.get()
            if vision_mode == "Vision Image":
                def send_picture_and_text():
                    import io
                    import win32clipboard
                    from PIL import ImageGrab
                    message = self.get_new_message_segment().strip()
                    if not message:
                        self.add_chat_message("System", "⚠️ No new content to send since last message")
                        return
                    if self.include_visual_context.get():
                        # Take screenshot and copy to clipboard as image
                        screenshot = ImageGrab.grab()
                        output = io.BytesIO()
                        screenshot.save(output, 'BMP')
                        data = output.getvalue()[14:]
                        output.close()
                        try:
                            win32clipboard.OpenClipboard()
                            win32clipboard.EmptyClipboard()
                            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                            win32clipboard.CloseClipboard()
                            self.add_chat_message("System", "🖼️ Screenshot taken and copied to clipboard.")
                        except Exception as e:
                            self.add_chat_message("Error", f"❌ Failed to copy screenshot to clipboard: {e}")
                            return
                        # Paste image into target window, then paste text, then press Enter
                        if self.direct_output_enabled.get() and self.selected_window_handle:
                            try:
                                # Focus window and paste screenshot
                                app = None
                                try:
                                    import pywinauto
                                    app = pywinauto.Application().connect(handle=self.selected_window_handle)
                                    win = app.window(handle=self.selected_window_handle)
                                    win.set_focus()
                                except Exception:
                                    import win32gui
                                    win32gui.SetForegroundWindow(self.selected_window_handle)
                                import time as _time
                                _time.sleep(0.5)
                                import pyautogui
                                pyautogui.hotkey('ctrl', 'v')
                                self.add_chat_message("System", "🖼️ Screenshot pasted to selected window.")
                                # Wait for screenshot to appear
                                _time.sleep(2.5)
                                # Now copy text to clipboard and paste it
                                import pyperclip
                                original_message = self.get_new_message_segment().strip()
                                pyperclip.copy(original_message)
                                pyautogui.hotkey('ctrl', 'v')
                                self.add_chat_message("System", "💬 Text pasted after screenshot.")
                                # Wait a fixed 5 seconds in Vision Image mode before pressing Enter
                                if self.auto_press_enter.get():
                                    if self.vision_mode.get() == "Vision Image":
                                        _time.sleep(5.0)
                                        pyautogui.press('enter')
                                        self.add_chat_message("Debug", f"✅ Auto-Enter pressed after 5s buffer (Vision Image)")
                                    else:
                                        _time.sleep(0.7)
                                        pyautogui.press('enter')
                            except Exception as e:
                                self.add_chat_message("Error", f"Failed to send screenshot/text: {e}")
                                return
                        # Wait before continuing logic
                        time.sleep(0.5)
                    # Now log/send the text message (for chat/memory only, not to window again)
                    original_message = message
                    self.add_chat_message("System", f"📤 Sending NEW segment: {len(message)} characters")
                    try:
                        self.save_input_memory(original_message, "send")
                    except Exception as e:
                        self.add_chat_message("Debug", f"Memory save failed: {e}")
                    try:
                        if original_message not in self.message_history:
                            self.message_history.append(original_message)
                        if len(self.message_history) > 50:
                            self.message_history.pop(0)
                        self.history_index = -1
                    except Exception as e:
                        self.add_chat_message("Debug", f"History update failed: {e}")
                    try:
                        self.mark_message_as_sent(original_message)
                    except Exception as e:
                        self.add_chat_message("Debug", f"Send marking failed: {e}")
                    self.add_chat_message("You", original_message)
                    self.clear_message_input()
                threading.Thread(target=send_picture_and_text, daemon=True).start()
                return
            # Otherwise, Vision Text mode (original logic)
            # ...existing code...
            # GET ONLY NEW MESSAGE SEGMENT - not the whole text block!
            message = self.get_new_message_segment().strip()
            if not message:
                self.add_chat_message("System", "⚠️ No new content to send since last message")
                return
            # Store the NEW segment being sent
            original_message = message
            self.add_chat_message("System", f"📤 Sending NEW segment: {len(message)} characters")
            # SAVE TO INPUT MEMORY SYSTEM (with error handling)
            try:
                self.save_input_memory(original_message, "send")
            except Exception as e:
                self.add_chat_message("Debug", f"Memory save failed: {e}")
            # Add to message history for up/down arrow navigation
            try:
                if original_message not in self.message_history:
                    self.message_history.append(original_message)
                if len(self.message_history) > 50:
                    self.message_history.pop(0)
                self.history_index = -1
            except Exception as e:
                self.add_chat_message("Debug", f"History update failed: {e}")
            # MARK THIS SEGMENT AS SENT - adds separator for next message
            try:
                self.mark_message_as_sent(original_message)
            except Exception as e:
                self.add_chat_message("Debug", f"Send marking failed: {e}")
            # Add user message to chat (show what user typed)
            self.add_chat_message("You", original_message)
            # SIMPLE VISUAL ATTACHMENT - ONLY for the NEW message segment
            if self.include_visual_context.get():
                try:
                    if os.path.exists(self.vision_log_file):
                        with open(self.vision_log_file, 'r', encoding='utf-8') as f:
                            log_data = json.load(f)
                        entries = log_data.get('entries', [])
                        if entries:
                            latest = entries[-1]
                            visual_text = latest.get('interpreted_text', '')
                            if visual_text:
                                message = f"""Based on this visual context from my screen: I can see {visual_text}\n\nPlease respond to my NEW message: {original_message}\n\nUse the visual context to provide a more informed and relevant response."""
                                self.add_chat_message("Info", "✅ Visual context attached to NEW message segment")
                            else:
                                self.add_chat_message("Info", "⚠️ No visual interpretation found")
                        else:
                            self.add_chat_message("Info", "⚠️ No visual entries - start screenshot rotation")
                    else:
                        self.add_chat_message("Info", "⚠️ No vision log found - start screenshot rotation")
                except Exception as e:
                    self.add_chat_message("Error", f"Visual context error: {e}")
            self.root.title("Visual Interpretation System v1.0")
            if self.direct_output_enabled.get():
                if self.selected_window_handle:
                    final_message = original_message
                    if self.include_visual_context.get():
                        visual_context = self.get_simple_visual_context()
                        if visual_context:
                            final_message += f"\n\n[Visual Context: {visual_context}]"
                    success = self.send_direct_to_window(final_message)
                    if success:
                        self.add_chat_message("System", "✅ NEW message segment sent to target window")
                    else:
                        self.add_chat_message("Error", "Failed to deliver message segment")
                    return
                else:
                    self.add_chat_message("Error", "No target window selected for direct output")
                    return
            if not self.connected:
                self.add_chat_message("Error", "Not connected to Ollama. Please check connection.")
                return
            if not self.selected_model.get():
                self.add_chat_message("Error", "No model selected. Please select a model first.")
                return
            self.send_button.config(state='disabled', text="Sending...")
            self.root.update()
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.selected_model.get(),
                    "prompt": message,
                    "stream": False
                },
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                data = response.json()
                model_response = data.get('response', 'No response received')
                self.add_chat_message(self.selected_model.get(), model_response)
            else:
                self.add_chat_message("Error", f"HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            self.add_chat_message("Error", "Request timed out. Try again.")
        except requests.exceptions.RequestException as e:
            self.add_chat_message("Error", f"Connection failed: {str(e)}")
        except Exception as e:
            self.add_chat_message("Error", f"CRITICAL: Send message crashed: {str(e)}")
            try:
                if hasattr(self, 'speech_listening') and self.speech_listening:
                    self.speech_listening = False
                    self.speech_button.config(text="🎤 TTS", style="Shiny.TButton")
            except:
                pass
        finally:
            try:
                self.send_button.config(state='normal', text="📤 Send")
            except:
                pass
    def take_and_save_screenshot(self):
        """Take a screenshot and save it to the screenshots folder. Returns the file path or None."""
        try:
            import datetime
            from PIL import ImageGrab
            screenshots_dir = self.screenshots_dir
            os.makedirs(screenshots_dir, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screen_{timestamp}.png"
            filepath = os.path.join(screenshots_dir, filename)
            img = ImageGrab.grab()
            img.save(filepath)
            return filepath
        except Exception as e:
            self.add_chat_message("Error", f"Screenshot error: {e}")
            return None
        
    def check_connection(self):
        """Check if Ollama is running and update status"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.connected = True
                self.status_label.config(text="Connected ✓", foreground="green")
                self.refresh_models()
            else:
                self.connected = False
                self.status_label.config(text="Connection Error", foreground="red")
        except requests.exceptions.RequestException as e:
            self.connected = False
            self.status_label.config(text="Disconnected", foreground="red")
        
    def refresh_models(self):
        """Get list of available models from Ollama"""
        if not self.connected:
            return
            
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.available_models = [model['name'] for model in data.get('models', [])]
                self.model_combo['values'] = self.available_models
                
                if self.available_models:
                    self.selected_model.set(self.available_models[0])
        except requests.exceptions.RequestException as e:
            pass  # Silent fail to keep screen clean
            
    def send_file(self):
        """Send a file (image) to the selected model"""
        if not self.connected:
            self.add_chat_message("Error", "Not connected to Ollama. Please check connection.")
            return
            
        if not self.selected_model.get():
            self.add_chat_message("Error", "No model selected. Please select a model first.")
            return
        
        # Open file dialog for image selection
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        # Get description from user
        description = self.message_entry.get().strip()
        if not description:
            description = "What do you see in this image?"
        
        # Clear the input
        self.message_entry.delete(0, tk.END)
        
        # Show user message
        self.add_chat_message("You", f"[Image: {file_path.split('/')[-1]}] {description}")
        
        # Disable buttons
        self.send_file_button.config(state='disabled', text="Sending...")
        self.send_button.config(state='disabled')
        self.root.update()
        
        try:
            # Read and encode image
            with open(file_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send to Ollama with image
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.selected_model.get(),
                    "prompt": description,
                    "images": [image_data],
                    "stream": False
                },
                timeout=60,  # Longer timeout for image processing
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                model_response = data.get('response', 'No response received')
                self.add_chat_message(self.selected_model.get(), model_response)
            else:
                self.add_chat_message("Error", f"HTTP {response.status_code}")
                
        except FileNotFoundError:
            self.add_chat_message("Error", "File not found or cannot be read.")
        except Exception as e:
            self.add_chat_message("Error", f"Error processing image: {str(e)}")
        finally:
            # Re-enable buttons
            self.send_file_button.config(state='normal', text="Send File")
            self.send_button.config(state='normal')

    def update_interval(self, event=None):
        """Update rotation interval when user changes selection"""
        interval_str = self.interval_var.get()
        self.rotation_interval = int(interval_str.replace('s', ''))
        
    def toggle_rotation(self):
        """Start or stop the screenshot rotation system"""
        if self.rotation_active:
            self.stop_rotation()
        else:
            self.start_rotation()
            
    def start_rotation(self):
        """Start the screenshot rotation system"""
        if not self.connected:
            self.add_chat_message("Error", "Connect to Ollama first before starting rotation")
            return
            
        self.rotation_active = True
        self.rotation_button.config(text="Stop Rotation", style="Accent.TButton")
        self.add_chat_message("System", f"🔄 Screenshot rotation started (every {self.rotation_interval}s)")
        
        # Start the rotation thread
        self.rotation_thread = threading.Thread(target=self.rotation_loop, daemon=True)
        self.rotation_thread.start()
        
    def stop_rotation(self):
        """Stop the screenshot rotation system"""
        self.rotation_active = False
        self.rotation_button.config(text="Start Rotation", style="")
        self.add_chat_message("System", "⏹️ Screenshot rotation stopped")
        
    def rotation_loop(self):
        """Main rotation loop that runs in background thread"""
        while self.rotation_active:
            try:
                # Take screenshot
                self.take_screenshot()
                
                # Wait for next interval
                for _ in range(self.rotation_interval * 10):  # Check every 0.1s for responsive stopping
                    if not self.rotation_active:
                        return
                    time.sleep(0.1)
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_chat_message("Error", f"Rotation error: {str(e)}"))
                break
                
    def take_screenshot(self):
        """Capture a screenshot using MSS - EXACTLY like Athena suggested!"""
        try:
            self.add_chat_message("Debug", f"📸 MSS CAPTURE: selected_screen_index = {self.selected_screen_index}")
            
            with mss.mss() as sct:
                if self.selected_screen_index == 1:
                    # SCREEN 1 - Primary monitor (MSS monitor 1)
                    monitor = sct.monitors[1] 
                    self.add_chat_message("Debug", f"   → SCREEN 1: monitor={monitor}")
                    screenshot_mss = sct.grab(monitor)

                    screen_info = "Screen 1"
                    
                elif self.selected_screen_index == 2:
                    # SCREEN 2 - Secondary monitor with 1080p override for performance
                    if len(sct.monitors) > 2:
                        monitor = sct.monitors[2]
                        self.add_chat_message("Debug", f"   → SCREEN 2: Original monitor={monitor}")
                        
                        # PERFECT! Use the EXACT coordinates MSS reports (they're correct!)
                        # No need to force 1080p - MSS already reports it correctly as 1920x1080
                        self.add_chat_message("Debug", f"   → SCREEN 2: Using EXACT MSS coordinates (no override needed!)")
                        self.add_chat_message("Debug", f"   → Monitor coords: {monitor}")
                        self.add_chat_message("Debug", f"   → This captures from LEFT={monitor['left']} to RIGHT={monitor['left']+monitor['width']}")
                        
                        # Use the monitor exactly as MSS reports it - it's already correct!
                        screenshot_mss = sct.grab(monitor)
                        self.add_chat_message("Debug", f"   → MSS captured: {screenshot_mss.size} pixels (native resolution)")
                        
                        screen_info = "Screen 2 (Native MSS)"
                    else:
                        # Fallback to primary if no secondary
                        monitor = sct.monitors[1]
                        self.add_chat_message("Debug", f"   → SCREEN 2 FALLBACK: only {len(sct.monitors)} monitors found, using monitor 1")
                        screenshot_mss = sct.grab(monitor)
                        screen_info = "Screen 2 (Fallback to Screen 1)"
                        
                else:
                    # Fallback to primary screen
                    monitor = sct.monitors[1]
                    self.add_chat_message("Debug", f"   → FALLBACK: Unexpected index {self.selected_screen_index}, using monitor 1")
                    screenshot_mss = sct.grab(monitor)
                    screen_info = "Screen 1 (Fallback)"
                
                # Convert MSS screenshot to PIL Image (IDENTICAL to debug script method)
                screenshot = Image.frombytes("RGB", screenshot_mss.size, screenshot_mss.bgra, "raw", "BGRX")
                
                # Apply resolution reduction if selected and in Vision Image mode
                if self.vision_mode.get() == "Vision Image" and self.screenshot_resolution.get() == "Reduced (1080p)":
                    # Only resize if original is larger than 1080p
                    original_width, original_height = screenshot.size
                    if original_width > 1920 or original_height > 1080:
                        # Calculate target size while maintaining aspect ratio
                        target_height = 1080
                        target_width = int(original_width * (target_height / original_height))
                        
                        # Make sure width doesn't exceed 1920
                        if target_width > 1920:
                            target_width = 1920
                            target_height = int(original_height * (target_width / original_width))
                        
                        # Resize with Lanczos for best quality/speed balance
                        screenshot = screenshot.resize((target_width, target_height), Image.LANCZOS)
                        self.add_chat_message("Debug", f"   → Reduced to 1080p: {screenshot.size} pixels")
                
                self.add_chat_message("Debug", f"   → PIL conversion: {screenshot.size} pixels")
                self.add_chat_message("Debug", f"   → Ready to save as: {screen_info}")
            
            # Generate filename with proper rotation (1, 2, 3, then back to 1)
            self.screenshot_counter = (self.screenshot_counter % self.max_screenshots) + 1
            filename = f"screen_{self.screenshot_counter:03d}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Save screenshot (this will overwrite the oldest one automatically)
            screenshot.save(filepath)
            
            # Add screen info to log
            self.add_chat_message("Debug", f"📸 Screenshot captured from: {screen_info} ({screenshot.width}x{screenshot.height})")
            
            # Clean up old screenshots beyond our rotation limit
            self.cleanup_old_screenshots()
            
            # Process with AI (in background to not block rotation)
            threading.Thread(target=self.process_screenshot, args=(filepath, filename), daemon=True).start()
            
        except Exception as e:
            self.root.after(0, lambda: self.add_chat_message("Error", f"Screenshot failed: {str(e)}"))
            
            # Fallback to basic MSS screenshot
            try:
                with mss.mss() as sct:
                    # Grab from first monitor as fallback
                    screenshot_mss = sct.grab(sct.monitors[1])
                    screenshot = Image.frombytes("RGB", screenshot_mss.size, screenshot_mss.bgra, "raw", "BGRX")
                    
                self.screenshot_counter = (self.screenshot_counter % self.max_screenshots) + 1
                filename = f"screen_{self.screenshot_counter:03d}.png"
                filepath = os.path.join(self.screenshots_dir, filename)
                screenshot.save(filepath)
                self.add_chat_message("Debug", "📸 MSS Fallback screenshot captured")
                threading.Thread(target=self.process_screenshot, args=(filepath, filename), daemon=True).start()
            except Exception as fallback_error:
                self.root.after(0, lambda: self.add_chat_message("Error", f"Fallback screenshot failed: {fallback_error}"))
    
    def cleanup_old_screenshots(self):
        """Remove screenshots beyond our rotation limit"""
        try:
            screenshot_files = [f for f in os.listdir(self.screenshots_dir) 
                              if f.startswith("screen_") and f.endswith(".png")]
            
            # Keep only the newest max_screenshots files
            if len(screenshot_files) > self.max_screenshots:
                # Sort by modification time, oldest first
                screenshot_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.screenshots_dir, f)))
                
                # Delete excess files
                files_to_delete = screenshot_files[:-self.max_screenshots]
                for file_to_delete in files_to_delete:
                    file_path = os.path.join(self.screenshots_dir, file_to_delete)
                    os.remove(file_path)
                    
        except Exception as e:
            print(f"Cleanup error: {e}")
    def process_screenshot(self, filepath, filename):
        """Process screenshot with AI and log results"""
        try:
            # Read and encode image
            with open(filepath, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Send to Ollama
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.selected_model.get(),
                    "prompt": "Describe what you see in this screenshot. Focus on text content, UI elements, and any important visual information.",
                    "images": [image_data],
                    "stream": False
                },
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                interpretation = data.get('response', 'No response received')
                
                # Log to JSON
                self.log_vision_result(filename, interpretation)
                
                # Update UI
                self.root.after(0, lambda: self.add_chat_message("Vision", f"📸 {filename}: {interpretation[:100]}..."))
                
            else:
                self.root.after(0, lambda: self.add_chat_message("Error", f"AI processing failed: HTTP {response.status_code}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.add_chat_message("Error", f"Processing failed: {str(e)}"))
            
    def log_vision_result(self, filename, interpretation):
        """Log vision result to JSON file"""
        try:
            # Load existing log or create new
            if os.path.exists(self.vision_log_file):
                with open(self.vision_log_file, 'r', encoding='utf-8') as f:
                    log_data = json.load(f)
            else:
                log_data = {"entries": []}
            
            # Add new entry
            entry = {
                "timestamp": datetime.now().isoformat(),
                "screenshot_filename": filename,
                "interpreted_text": interpretation
            }
            log_data["entries"].append(entry)
            
            # Save back to file
            with open(self.vision_log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.root.after(0, lambda: self.add_chat_message("Error", f"Logging failed: {str(e)}"))

    def test_clipboard(self):
        """Test clipboard functionality independently"""
        try:
            self.add_chat_message("Debug", "🧪 TESTING CLIPBOARD FUNCTIONALITY")
            
            # Test 1: Basic clipboard operations
            test_text = f"Clipboard test at {datetime.now().strftime('%H:%M:%S')}"
            
            # Save current clipboard
            try:
                original_clipboard = pyperclip.paste()
                self.add_chat_message("Debug", f"📋 Original clipboard: '{original_clipboard[:50]}...'")
            except Exception as e:
                self.add_chat_message("Debug", f"⚠️ Could not read original clipboard: {e}")
                original_clipboard = ""
            
            # Test copy
            try:
                pyperclip.copy(test_text)
                self.add_chat_message("Debug", "✅ Test text copied to clipboard")
            except Exception as e:
                self.add_chat_message("Error", f"❌ Copy failed: {e}")
                return
            
            # Test paste
            try:
                pasted_text = pyperclip.paste()
                if pasted_text == test_text:
                    self.add_chat_message("Debug", "✅ Clipboard read/write working correctly")
                else:
                    self.add_chat_message("Error", f"❌ Clipboard mismatch: expected '{test_text}', got '{pasted_text}'")
                    return
            except Exception as e:
                self.add_chat_message("Error", f"❌ Paste failed: {e}")
                return
            
            # Test 2: Keyboard shortcut simulation
            if self.selected_window_handle and self.direct_output_enabled.get():
                self.add_chat_message("Debug", "🔄 Testing Ctrl+V in target window...")
                
                # Activate window
                try:
                    win32gui.SetForegroundWindow(self.selected_window_handle)
                    time.sleep(0.5)
                    
                    # Try to paste
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(0.3)
                    
                    self.add_chat_message("Debug", "✅ Ctrl+V sent to target window")
                    self.add_chat_message("System", "👀 CHECK TARGET WINDOW - Did the test text appear?")
                    
                except Exception as e:
                    self.add_chat_message("Error", f"❌ Failed to test Ctrl+V: {e}")
            else:
                self.add_chat_message("Debug", "⚠️ No target window selected - skipping Ctrl+V test")
            
            # Restore original clipboard
            try:
                pyperclip.copy(original_clipboard)
                self.add_chat_message("Debug", "🔄 Original clipboard restored")
            except Exception as e:
                self.add_chat_message("Debug", f"⚠️ Could not restore clipboard: {e}")
            
            self.add_chat_message("System", "🧪 Clipboard test completed!")
            
        except Exception as e:
            self.add_chat_message("Error", f"💥 Clipboard test failed: {e}")

    def on_message_typing(self, event):
        """Handle typing in message entry - reset history navigation"""
        # Reset history navigation when user starts typing
        if event.keysym not in ['Up', 'Down']:
            self.history_index = -1
    
    def preview_message_with_context(self):
        """Show preview of what will be sent including visual context"""
        try:
            message = self.message_entry.get().strip()
            if not message:
                self.add_chat_message("Preview", "Type a message to see preview...")
                return
            
            # Show what will be sent
            self.add_chat_message("Preview", f"📝 Your message: {message}")
            
            if self.include_visual_context.get():
                visual_context = self.get_simple_visual_context()
                if visual_context:
                    # Show truncated visual context
                    preview_visual = visual_context[:200] + "..." if len(visual_context) > 200 else visual_context
                    self.add_chat_message("Preview", f"📸 Visual context: {preview_visual}")
                    self.add_chat_message("Preview", "✅ Combined message will include both your text + visual context")
                else:
                    self.add_chat_message("Preview", "⚠️ No visual context available - start screenshot rotation")
            else:
                self.add_chat_message("Preview", "📸 Visual context disabled - only your message will be sent")
                
        except Exception as e:
            self.add_chat_message("Error", f"Preview error: {e}")

    def activate_speech(self):
        """Toggle speech-to-text listening mode"""
        if not self.speech_listening:
            # START LISTENING
            self.start_speech_listening()
        else:
            # STOP LISTENING
            self.stop_speech_listening()
    
    def start_speech_listening(self):
        """Start continuous speech listening"""
        try:
            self.speech_listening = True
            self.speech_button.config(text="🔴 STOP", style="SpeechActive.TButton")
            
            self.add_chat_message("System", "🎤 Speech listening STARTED - ULTRA FLUFFY MODE!")
            self.add_chat_message("System", "💬 System is now EXTREMELY patient with natural speech patterns")
            self.add_chat_message("System", "🕐 Allows up to 4.5 second thinking pauses without cutting")
            self.add_chat_message("System", "🗣️ Speak naturally - no need to rush your thoughts!")
            
            # Add activation mode status
            if self.keyword_activation_enabled.get() and self.silence_activation_enabled.get():
                self.add_chat_message("System", "🎯🤫 DUAL MODE: Keywords OR silence activation enabled")
            elif self.keyword_activation_enabled.get():
                self.add_chat_message("System", "🎯 KEYWORD MODE: Say trigger words to auto-send")
            elif self.silence_activation_enabled.get():
                duration = self.silence_duration.get()
                self.add_chat_message("System", f"🤫 SILENCE MODE: {duration} pause auto-sends")
            else:
                self.add_chat_message("System", "⚠️ Manual mode: Click STOP when finished speaking")
            
            self.add_chat_message("System", "🔴 Click STOP button to end speech session")
            
            # Check if speech system is available
            if not SPEECH_AVAILABLE:
                self.add_chat_message("Error", "❌ Speech system not available - check flexible_whisper.py")
                self.speech_listening = False
                self.speech_button.config(text="🎤 TTS", style="Shiny.TButton")
                return
            
            def continuous_speech_thread():
                try:
                    # Initialize Whisper (FlexibleWhisper already imported at top)
                    self.speech_whisper = FlexibleWhisper()
                    if not self.speech_whisper.available_models:
                        self.root.after(0, lambda: self.add_chat_message("Error", "❌ No speech recognition available!"))
                        self.root.after(0, self.stop_speech_listening)
                        return
                    
                    # Auto-select best model
                    if self.speech_whisper.auto_select_model():
                        # Apply current language setting
                        self.speech_whisper.set_english_only(self.english_only_mode.get())
                        
                        # Update visual status indicator
                        self.update_whisper_status()
                        
                        self.root.after(0, lambda: self.add_chat_message("System", f"🤖 Speech ready: {self.speech_whisper.selected_model_name}"))
                        self.root.after(0, lambda: self.add_chat_message("System", "🔧 Switch models anytime with the Whisper button"))
                        
                        # Use the improved continuous listening with VAD
                        import threading
                        stop_event = threading.Event()
                        
                        def speech_callback(text):
                            """Callback for when speech is detected"""
                            if text and text.strip():
                                # Insert text into the input field (thread-safe)
                                self.root.after(0, lambda t=text: self.insert_speech_text(t))
                        
                        # Start the improved continuous listening with BETTER STOP DETECTION
                        try:
                            self.speech_whisper.continuous_listen(speech_callback, stop_event)
                        except Exception as e:
                            self.root.after(0, lambda: self.add_chat_message("Debug", f"Continuous listen error: {e}"))
                        
                        # SYNCHRONIZED: Check stop flag more frequently but not aggressively
                        while self.speech_listening:
                            time.sleep(0.1)  # Check every 100ms - balanced responsiveness (was 50ms)
                            
                            # Double-check that we should still be listening
                            if not self.speech_listening:
                                break
                                
                        # IMMEDIATE STOP when flag changes - SYNCHRONIZED with VAD
                        stop_event.set()
                        
                        # Give VAD system time to finish current processing
                        time.sleep(0.2)  # 200ms grace period for VAD cleanup
                        
                        self.root.after(0, lambda: self.add_chat_message("Debug", "🔴 Speech thread synchronized stop - VAD cleanup complete"))
                        
                    else:
                        self.root.after(0, lambda: self.add_chat_message("Error", "❌ Failed to initialize speech recognition"))
                        
                except Exception as e:
                    self.root.after(0, lambda: self.add_chat_message("Error", f"Speech error: {e}"))
                finally:
                    # Clean up
                    self.speech_whisper = None
                    if self.speech_listening:  # Auto-stop if there was an error
                        self.root.after(0, self.stop_speech_listening)
            
            # Run in background thread
            self.speech_thread = threading.Thread(target=continuous_speech_thread, daemon=True)
            self.speech_thread.start()
            
        except Exception as e:
            self.add_chat_message("Error", f"Speech start failed: {e}")
            self.stop_speech_listening()
    
    def stop_speech_listening(self):
        """Stop speech listening - IMMEDIATE & RELIABLE SHUTDOWN"""
        try:
            # IMMEDIATE STOP - Set flag first
            self.speech_listening = False
            
            # Update button immediately to show we're stopping
            self.speech_button.config(text="⏸️ STOPPING...", style="Shiny.TButton")
            self.add_chat_message("System", "⏹️ Speech listening STOPPING...")
            
            # Cancel any pending silence timer
            if self.silence_timer:
                self.root.after_cancel(self.silence_timer)
                self.silence_timer = None
            if self.countdown_timer:
                self.root.after_cancel(self.countdown_timer)
                self.countdown_timer = None
            
            # Reset countdown display
            self.countdown_active = False
            self.countdown_label.config(text="")
            
            # FORCE STOP the whisper instance if it exists
            if self.speech_whisper:
                try:
                    # Try to stop gracefully first
                    if hasattr(self.speech_whisper, 'stop_listening'):
                        self.speech_whisper.stop_listening()
                except:
                    pass
                self.speech_whisper = None
                
            # Give thread a moment to see the stop flag, then clean up
            def finalize_stop():
                try:
                    self.speech_thread = None
                    self.speech_button.config(text="🎤 TTS", style="Shiny.TButton")
                    
                    self.add_chat_message("System", "✅ Speech listening STOPPED completely")
                except:
                    pass
                    
            # Delay final cleanup to ensure thread sees the stop flag
            self.root.after(500, finalize_stop)
            
        except Exception as e:
            self.add_chat_message("Error", f"Speech stop error: {e}")
            # FORCE cleanup on any error
            self.speech_listening = False
            self.speech_button.config(text="🎤 TTS", style="Shiny.TButton")
            self.speech_thread = None
    
    def insert_speech_text(self, text):
        """SIMPLE INSTANT TEXT - like Microsoft Speech Recognition - WITH WHISPER ARTIFACT FILTER"""
        try:
            if not text or not text.strip():
                return
            
            # 🛡️ WHISPER ARTIFACT FILTER - Block garbage noise from triggering silence timer!
            text_clean = text.strip().lower()
            
            # Common Whisper artifacts that should be IGNORED completely
            whisper_artifacts = [
                "you", "uu", "uuu", "uh", "uhh", "um", "umm",
                "thank you", "subscribe", "like", "and subscribe",
                "youtube", "please subscribe", "hit the bell",
                "mm", "mmm", "hmm", "hm", "eh", "ah", "oh"
            ]
            
            # Check if this is ONLY an artifact (ignore completely)
            if text_clean in whisper_artifacts:
                self.add_chat_message("Debug", f"🚫 BLOCKED Whisper artifact: '{text_clean}'")
                return  # DON'T process this text AT ALL - no timer resets!
            
            # Check if text is too short (likely noise)
            if len(text_clean) < 3:
                self.add_chat_message("Debug", f"🚫 BLOCKED short artifact: '{text_clean}'")
                return  # DON'T process short noise
                
            # KEYWORD ACTIVATION CHECK - CRITICAL FIX!
            if self.keyword_activation_enabled.get():
                text_lower = text.lower().strip()
                
                # Check if text contains any trigger keywords
                for keyword in self.trigger_keywords:
                    if keyword in text_lower:
                        self.add_chat_message("System", f"🎯 KEYWORD DETECTED: '{keyword}' - AUTO-SENDING!")
                        
                        # Add the text (without the trigger keyword for cleaner messages)
                        clean_text = text.replace(keyword, "").strip()
                        if clean_text and len(clean_text) > 2:
                            current_pos = self.message_entry.index(tk.INSERT)
                            self.message_entry.insert(current_pos, " " + clean_text)
                            self.message_entry.see(tk.END)
                        
                        # AUTO-SEND the message immediately
                        self.root.after(200, self.send_message)  # Quick response
                        return
                
            # INSTANT TEXT INSERTION - NO DELAYS, NO BUFFERS!
            current_pos = self.message_entry.index(tk.INSERT)
            self.message_entry.insert(current_pos, " " + text.strip())
            self.message_entry.see(tk.END)
            
            # Update speech time for silence detection
            import time
            self.last_speech_time = time.time()
            
            # Reset auto-silence timer if active and restart it
            if self.auto_silence_timer:
                self.root.after_cancel(self.auto_silence_timer)
                self.auto_silence_timer = None
            
            # Start auto-silence timer if enabled (FIXED: was missing restart!)
            if self.auto_silence_enabled.get():
                self.start_auto_silence_timer()
            
            # Start silence detection timer if enabled - MANUAL SILENCE ACTIVATION
            if self.silence_activation_enabled.get():
                # Cancel existing timers
                self.reset_silence_timer()
                
                # Start new timer - no buffer, direct approach
                duration_str = self.silence_duration.get()
                duration_seconds = int(duration_str.replace('s', ''))
                duration_ms = duration_seconds * 1000
                
                self.silence_timer = self.root.after(duration_ms, self.on_silence_detected)
                
                # Show countdown
                self.countdown_remaining = duration_seconds
                self.countdown_active = True
                self.update_countdown_display()
            
        except Exception as e:
            self.add_chat_message("Error", f"Speech insertion failed: {e}")
    
    def process_speech_buffer(self):
        """Process accumulated speech buffer with FLOWING approach - faster, smoother text delivery"""
        try:
            if not self.speech_buffer.strip():
                return
            
            # Get the accumulated text
            accumulated_text = self.speech_buffer.strip()
            self.speech_buffer = ""  # Clear buffer
            self.speech_buffer_timer = None
            
            import time
            # Update last speech time for silence detection
            self.last_speech_time = time.time()
            
            # CRITICAL: Reset silence activation timer (but NOT auto-silence yet)
            self.reset_silence_timer()
            
            # Check for trigger keywords FIRST before inserting text
            if self.keyword_activation_enabled.get():
                text_lower = accumulated_text.lower().strip()
                
                # Check if text contains any trigger keywords
                for keyword in self.trigger_keywords:
                    if keyword in text_lower:
                        self.add_chat_message("System", f"🎯 KEYWORD DETECTED: '{keyword}' - AUTO-SENDING!")
                        
                        # Add the text (without the trigger keyword for cleaner messages)
                        clean_text = accumulated_text.replace(keyword, "").strip()
                        if clean_text and len(clean_text) > 2:
                            current_pos = self.message_entry.index(tk.INSERT)
                            self.message_entry.insert(current_pos, " " + clean_text)
                        
                        # AUTO-SEND the message with flowing delay
                        self.root.after(300, self.send_message)  # Quick response
                        return
            
            # Normal FLOWING text insertion (no keywords detected)
            current_pos = self.message_entry.index(tk.INSERT)
            self.message_entry.insert(current_pos, " " + accumulated_text)
            
            # AUTO-SCROLL to show latest text
            self.message_entry.see(tk.END)
            self.message_entry.focus()
            
            # Show confirmation with flowing feedback
            self.add_chat_message("Speech", f"✅ FLOWING TEXT: {len(accumulated_text)} chars delivered")
            
            # NOW start auto-silence detection timer (AFTER text is processed)
            if self.auto_silence_enabled.get():
                self.start_auto_silence_timer()
            
            # Start silence detection timer if enabled - for manual silence activation
            if self.silence_activation_enabled.get():
                self.start_silence_buffer()
            
            # AUTO-CLEANUP CHECK - Prevent sluggishness (you said keep this fast)
            self.check_auto_cleanup()
            
        except Exception as e:
            self.add_chat_message("Error", f"Speech buffer processing failed: {e}")
    
    def process_speech_buffer_background(self):
        """Background processing for speech buffer - keywords, cleanup, etc."""
        try:
            if not self.speech_buffer.strip():
                return
                
            # Check for keyword detection in background
            buffer_text = self.speech_buffer.strip()
            
            # Keyword detection for actions (only if not already processed immediately)
            if self.keyword_activation_enabled.get():
                text_lower = buffer_text.lower().strip()
                for keyword in self.trigger_keywords:
                    if keyword in text_lower:
                        self.add_chat_message("Action", f"🔥 Background keyword '{keyword}' - Auto-sending message...")
                        self.send_message()
                        break
            
            # Clear processed buffer
            self.speech_buffer = ""
            self.speech_buffer_timer = None
            
        except Exception as e:
            self.add_chat_message("Error", f"Background processing failed: {e}")
    
    def check_keywords_immediately(self):
        """Check for keywords immediately without delays"""
        try:
            if not self.keyword_activation_enabled.get():
                return
                
            buffer_text = self.speech_buffer.strip().lower()
            
            for keyword in self.trigger_keywords:
                if keyword in buffer_text:
                    self.add_chat_message("Action", f"🔥 KEYWORD '{keyword}' DETECTED - AUTO-SENDING!")
                    
                    # Clear buffer and send immediately
                    self.speech_buffer = ""
                    self.root.after(100, self.send_message)  # Very quick send
                    return
                    
        except Exception as e:
            self.add_chat_message("Error", f"Keyword check failed: {e}")
    
    def start_silence_buffer(self):
        """Start the 1-second buffer before actual silence timer - SOFT ACTIVATION"""
        try:
            # IMMEDIATE RESET - Cancel all existing timers when new speech detected
            self.reset_silence_timer()
            
            # Start 1-second buffer timer for soft activation
            self.silence_buffer_timer = self.root.after(
                int(self.silence_buffer_duration * 1000), 
                self.start_silence_timer
            )
            
            # Show buffer indication
            self.countdown_label.config(text="⏳ Buffering...", foreground="gray")
            
        except Exception as e:
            self.add_chat_message("Error", f"Silence buffer error: {e}")
    
    def start_silence_timer(self):
        """Start the silence detection timer with visual countdown - AFTER BUFFER"""
        try:
            # Only start if buffer timer completed and not cancelled
            if not self.silence_buffer_timer:
                return
                
            # Clear buffer timer reference
            self.silence_buffer_timer = None
            
            # Get silence duration in seconds
            duration_str = self.silence_duration.get()
            duration_seconds = int(duration_str.replace('s', ''))
            
            # Start visual countdown
            self.countdown_remaining = duration_seconds
            self.countdown_active = True
            self.update_countdown_display()
            
            # Set main timer to trigger after silence duration
            duration_ms = duration_seconds * 1000
            self.silence_timer = self.root.after(duration_ms, self.on_silence_detected)
            
            self.add_chat_message("System", f"🤫 Silence timer started: {duration_seconds}s (after 1s buffer)")
            
        except Exception as e:
            self.add_chat_message("Error", f"Silence timer error: {e}")
    
    def update_countdown_display(self):
        """Update the visual countdown display"""
        try:
            if not self.countdown_active or self.countdown_remaining <= 0:
                self.countdown_label.config(text="")
                return
            
            # Show countdown with visual flair
            if self.countdown_remaining > 1:
                self.countdown_label.config(text=f"🕐 {self.countdown_remaining}s", foreground="orange")
            else:
                self.countdown_label.config(text="🚀 SENDING!", foreground="red")
            
            # Schedule next countdown update
            self.countdown_remaining -= 1
            if self.countdown_remaining >= 0:
                self.countdown_timer = self.root.after(1000, self.update_countdown_display)
            
        except Exception as e:
            self.add_chat_message("Error", f"Countdown display error: {e}")
    
    def on_silence_detected(self):
        """Called when silence duration is reached - AUTO-SEND MESSAGE"""
        try:
            import time
            
            # Double-check that enough time has actually passed
            time_since_speech = time.time() - self.last_speech_time
            silence_duration = int(self.silence_duration.get().replace('s', ''))
            
            if time_since_speech >= (silence_duration - 0.1):  # Small tolerance
                # Check if there's actually a message to send
                message_content = self.get_message_text().strip()
                if message_content:
                    self.add_chat_message("System", f"🤫 SILENCE DETECTED ({silence_duration}s) - AUTO-SENDING MESSAGE!")
                    
                    # Clear countdown display
                    self.countdown_active = False
                    self.countdown_label.config(text="✅ SENT!", foreground="green")
                    
                    # AUTO-SEND the message
                    self.root.after(100, self.send_message)
                    
                    # Clear the sent indicator after a moment
                    self.root.after(2000, lambda: self.countdown_label.config(text=""))
                else:
                    self.add_chat_message("Debug", "🤫 Silence detected, but no message to send")
                    self.countdown_label.config(text="")
            
            # Clear the timer
            self.silence_timer = None
            self.countdown_active = False
            
        except Exception as e:
            self.add_chat_message("Error", f"Silence detection error: {e}")
            self.countdown_label.config(text="")
    
    def get_message_text(self):
        """Get text from the message input (works with Text widget)"""
        try:
            return self.message_entry.get("1.0", tk.END).strip()
        except:
            return ""
    
    def get_new_message_segment(self):
        """Get only the NEW message content since last send - SEGMENTATION LOGIC!"""
        try:
            # Get all text from the message input
            all_text = self.message_entry.get("1.0", tk.END).strip()
            
            if not all_text:
                return ""
            
            lines = all_text.split('\n')
            
            # Find the last SENT or QUEUED marker (both formats)
            last_sent_index = -1
            for i, line in enumerate(lines):
                # Look for BOTH old format and new format markers
                if ("═══ SENT:" in line or 
                    "SENT" in line and "─" in line or 
                    "QUEUED" in line and "─" in line):
                    last_sent_index = i
            
            # If no SENT/QUEUED marker found, return all text as new
            if last_sent_index == -1:
                return all_text
            
            # Get everything after the last SENT/QUEUED marker
            new_lines = []
            for i in range(last_sent_index + 1, len(lines)):
                line = lines[i]
                # Skip empty lines immediately after SENT/QUEUED marker
                if not line.strip() and not new_lines:
                    continue
                new_lines.append(line)
            
            return '\n'.join(new_lines).strip()
            
        except Exception as e:
            self.add_chat_message("Error", f"Message segment error: {e}")
            # Fallback to all text
            return self.get_message_text()
    
    def mark_message_as_sent(self, sent_message):
        """Mark the current message as sent by adding appropriate separator based on Direct Output mode"""
        try:
            if not sent_message.strip():
                return
                
            # FIXED LOGIC: Different separators based on Direct Output mode
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if self.direct_output_enabled.get():
                # Direct Output ON (sending mode) - Show SENT separator
                separator = f"\n" + "─" * 30 + f" SENT {timestamp} " + "─" * 30 + "\n"
                self.add_chat_message("System", f"📤 Message SENT to target ({len(sent_message)} chars)")
            else:
                # Direct Output OFF (accumulation mode) - Show QUEUED separator  
                separator = f"\n" + "─" * 25 + f" QUEUED {timestamp} " + "─" * 25 + "\n"
                self.add_chat_message("System", f"📤 Message QUEUED for later ({len(sent_message)} chars)")
            
            # Add separator at the end of current content
            self.message_entry.insert(tk.END, separator)
            self.message_entry.see(tk.END)
            
        except Exception as e:
            self.add_chat_message("Error", f"Send marking error: {e}")
    
    def clear_message_input(self):
        """Clear the message input (works with Text widget)"""
        try:
            current_text = self.get_message_text()
            text_length = len(current_text)
            
            # SAVE TO INPUT MEMORY before clearing
            if text_length > 0:
                self.save_input_memory(current_text, "clear")
            
            self.message_entry.delete("1.0", tk.END)
            if text_length > 0:
                self.add_chat_message("System", f"🗑️ Cleared {text_length} characters from input (saved to memory)")
            else:
                self.add_chat_message("System", "🗑️ Input was already empty")
        except Exception as e:
            self.add_chat_message("Error", f"Failed to clear input: {e}")
    
    def add_text_flow_separator(self):
        """Add a visual separator to create flowing text chunks without clearing"""
        try:
            # Add a visual separator line in the input to show where previous chunk ended
            current_text = self.get_message_text()
            if current_text.strip():  # Only add separator if there's existing text
                separator = "\n" + "─" * 50 + " SENT ─" + "─" * 50 + "\n"
                self.message_entry.insert(tk.END, separator)
                
                # Auto-scroll to end to show the separator and prepare for new input
                self.message_entry.see(tk.END)
                
                self.add_chat_message("System", "📝 Text chunk sent - continuing flow...")
            
        except Exception as e:
            self.add_chat_message("Error", f"Failed to add flow separator: {e}")
    
    def focus_message_entry(self):
        """Focus the message entry field"""
        try:
            self.message_entry.focus()
            # Position cursor at end
            self.message_entry.mark_set(tk.INSERT, tk.END)
        except Exception as e:
            print(f"Focus error: {e}")
    
    def navigate_history_up(self, event=None):
        """Navigate up through message history"""
        if not self.message_history:
            return "break"  # Prevent default behavior
        
        # If at end of history or first time, start from last message
        if self.history_index == -1:
            self.history_index = len(self.message_history) - 1
        else:
            # Move up in history (older messages)
            self.history_index = max(0, self.history_index - 1)
        
        # Set the message
        if 0 <= self.history_index < len(self.message_history):
            self.clear_message_input()
            self.message_entry.insert("1.0", self.message_history[self.history_index])
        
        return "break"  # Prevent default up arrow behavior
    
    def navigate_history_down(self, event=None):
        """Navigate down through message history"""
        if not self.message_history or self.history_index == -1:
            return "break"  # Prevent default behavior
        
        # Move down in history (newer messages)
        self.history_index += 1
        
        if self.history_index >= len(self.message_history):
            # Beyond last message, clear input and reset
            self.history_index = -1
            self.clear_message_input()
        else:
            # Set the message
            self.clear_message_input()
            self.message_entry.insert("1.0", self.message_history[self.history_index])
        
        return "break"  # Prevent default down arrow behavior
    
    def show_keyword_settings(self):
        """Show keyword activation settings in a dialog"""
        try:
            from tkinter import simpledialog, messagebox
            
            current_keywords = ", ".join(self.trigger_keywords)
            
            new_keywords = simpledialog.askstring(
                "Keyword Activation Settings",
                f"Enter trigger keywords (comma-separated):\n\nCurrent keywords:\n{current_keywords}",
                initialvalue=current_keywords
            )
            
            if new_keywords:
                # Parse and clean the keywords
                keywords = [kw.strip().lower() for kw in new_keywords.split(",") if kw.strip()]
                
                if keywords:
                    self.trigger_keywords = keywords
                    self.add_chat_message("System", f"🎯 Updated trigger keywords: {', '.join(keywords)}")
                else:
                    messagebox.showwarning("Invalid Input", "Please enter at least one keyword.")
                    
        except Exception as e:
            self.add_chat_message("Error", f"Keyword settings error: {e}")
    
    def open_model_chat(self):
        """Open the dedicated model chat window - Future Swiss Army Knife feature!"""
        try:
            self.add_chat_message("System", "💬 Model chat feature coming soon!")
            self.add_chat_message("System", "🎯 For now, you can chat with models in the System Screen")
            self.add_chat_message("System", "🔧 This will be a separate dedicated chat interface")
            
        except Exception as e:
            self.add_chat_message("Error", f"Model chat placeholder error: {e}")

    # ===== CHAT MEMORY SYSTEM - PRESERVE ALL CONVERSATIONS =====
    
    def save_chat_memory(self, message_type, sender, content):
        """Save all chat interactions to permanent memory"""
        try:
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": message_type,  # "system", "user", "ai", "debug", "error"
                "sender": sender,
                "content": content,
                "length": len(content)
            }
            
            self.chat_memory.append(memory_entry)
            
            # Save to file immediately
            self.write_chat_memory_to_file()
            
        except Exception as e:
            print(f"Chat memory save error: {e}")
    
    def save_input_memory(self, input_text, action="input"):
        """Save all input text to permanent memory"""
        try:
            if not input_text.strip():
                return
                
            input_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,  # "input", "send", "clear", "copy"
                "text": input_text.strip(),
                "length": len(input_text.strip())
            }
            
            self.input_memory.append(input_entry)
            
            # Save to file immediately
            self.write_input_memory_to_file()
            
        except Exception as e:
            print(f"Input memory save error: {e}")
    
    def write_chat_memory_to_file(self):
        """Write chat memory to JSON file"""
        try:
            memory_data = {
                "total_entries": len(self.chat_memory),
                "last_updated": datetime.now().isoformat(),
                "entries": self.chat_memory[-1000:]  # Keep last 1000 entries
            }
            
            with open(self.chat_memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Chat memory file write error: {e}")
    
    def write_input_memory_to_file(self):
        """Write input memory to JSON file"""
        try:
            input_data = {
                "total_entries": len(self.input_memory),
                "last_updated": datetime.now().isoformat(),
                "entries": self.input_memory[-500:]  # Keep last 500 input entries
            }
            
            with open(self.input_memory_file, 'w', encoding='utf-8') as f:
                json.dump(input_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Input memory file write error: {e}")
    
    def load_chat_memory(self):
        """Load existing chat memory from file"""
        try:
            if os.path.exists(self.chat_memory_file):
                with open(self.chat_memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chat_memory = data.get('entries', [])
                    self.add_chat_message("System", f"📂 Loaded {len(self.chat_memory)} chat memory entries")
            else:
                self.chat_memory = []
                
        except Exception as e:
            self.add_chat_message("Error", f"Chat memory load error: {e}")
            self.chat_memory = []
    
    def load_input_memory(self):
        """Load existing input memory from file"""
        try:
            if os.path.exists(self.input_memory_file):
                with open(self.input_memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.input_memory = data.get('entries', [])
                    self.add_chat_message("System", f"📂 Loaded {len(self.input_memory)} input memory entries")
            else:
                self.input_memory = []
                
        except Exception as e:
            self.add_chat_message("Error", f"Input memory load error: {e}")
            self.input_memory = []
    
    def clean_all_memory(self):
        """Clean all memory files - DANGER ZONE!"""
        try:
            # Clean chat memory
            self.chat_memory = []
            empty_chat = {"total_entries": 0, "last_updated": datetime.now().isoformat(), "entries": []}
            with open(self.chat_memory_file, 'w', encoding='utf-8') as f:
                json.dump(empty_chat, f, indent=2, ensure_ascii=False)
            
            # Clean input memory
            self.input_memory = []
            empty_input = {"total_entries": 0, "last_updated": datetime.now().isoformat(), "entries": []}
            with open(self.input_memory_file, 'w', encoding='utf-8') as f:
                json.dump(empty_input, f, indent=2, ensure_ascii=False)
            
            self.add_chat_message("System", "🧹 ALL MEMORY CLEANED! Fresh start ready.")
            
        except Exception as e:
            self.add_chat_message("Error", f"Memory cleaning error: {e}")


# ===== MAIN EXECUTION - START THE APPLICATION =====

if __name__ == "__main__":
    try:
        print("🚀 Starting Visual Interpretation System...")
        
        # Create the main window
        root = tk.Tk()
        print("✅ Tkinter root window created")
        
        # Create the application
        app = OllamaInterface(root)
        print("✅ OllamaInterface initialized")
        
        print("🎯 System ready! Starting GUI...")
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
