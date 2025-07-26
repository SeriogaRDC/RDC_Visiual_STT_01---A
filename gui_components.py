"""
GUI Components - Modern UI Components & Windows
===============================================

Handles all GUI creation and management:
- Main application window
- All UI controls and layout
- Event handling and styling
- Visual log window integration

This replaces the scattered GUI code from the monolith.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
from datetime import datetime
from visual_log_window import VisualLogWindow
from config import (
    WINDOW_TITLE, WINDOW_GEOMETRY, APP_COLORS, UI_FONTS,
    BUTTON_PADDING, TEXT_AREAS, STARTUP_MESSAGES
)


class GUIComponents:
    """Modern GUI components and window management"""
    
    def __init__(self, app_controller):
        """Initialize GUI components"""
        self.app_controller = app_controller
        self.root = None
        self.visual_log_window = None
        
        # UI Elements
        self.target_window_var = None
        self.status_var = None
        self.input_text = None
        self.output_text = None
        self.recording_button = None
        self.is_recording = False
        
    def create_main_window(self):
        """Create and configure main application window"""
        try:
            self.root = tk.Tk()
            self.root.title(WINDOW_TITLE)
            self.root.geometry(WINDOW_GEOMETRY)
            self.root.configure(bg=APP_COLORS["background"])
            
            # Configure style
            self.setup_styles()
            
            # Create UI components
            self.create_ui_components()
            
            # Show startup message
            self.show_startup_message()
            
            print(f"✅ Main window created: {WINDOW_TITLE}")
            
        except Exception as e:
            error_msg = f"Main window creation failed: {e}"
            print(f"❌ {error_msg}")
            self.app_controller.memory_manager.save_system_message("error", "GUIComponents", error_msg)
            
    def setup_styles(self):
        """Configure ttk styles for modern appearance"""
        try:
            style = ttk.Style()
            
            # Configure button styles
            style.configure(
                "Modern.TButton",
                font=UI_FONTS["button"],
                padding=BUTTON_PADDING
            )
            
            style.configure(
                "Record.TButton",
                font=UI_FONTS["button"],
                padding=BUTTON_PADDING,
                foreground="white"
            )
            
            # Configure label styles
            style.configure(
                "Modern.TLabel",
                font=UI_FONTS["label"],
                background=APP_COLORS["background"],
                foreground=APP_COLORS["text"]
            )
            
        except Exception as e:
            print(f"Style setup error: {e}")
            
    def create_ui_components(self):
        """Create all UI components"""
        try:
            # Main container
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Target window section
            self.create_target_window_section(main_frame)
            
            # Control buttons section
            self.create_control_buttons_section(main_frame)
            
            # Input/Output section
            self.create_text_areas_section(main_frame)
            
            # Status section
            self.create_status_section(main_frame)
            
        except Exception as e:
            error_msg = f"UI components creation failed: {e}"
            print(f"❌ {error_msg}")
            self.app_controller.memory_manager.save_system_message("error", "GUIComponents", error_msg)
            
    def create_target_window_section(self, parent):
        """Create target window configuration section"""
        # Target window frame
        target_frame = ttk.LabelFrame(parent, text="Target Window", padding="5")
        target_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Target window entry
        self.target_window_var = tk.StringVar()
        target_entry = ttk.Entry(
            target_frame, 
            textvariable=self.target_window_var,
            font=UI_FONTS["input"],
            width=50
        )
        target_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Set target button
        set_target_btn = ttk.Button(
            target_frame,
            text="Set Target",
            style="Modern.TButton",
            command=self.on_set_target_window
        )
        set_target_btn.pack(side=tk.RIGHT)
        
        # Auto-detect button
        auto_detect_btn = ttk.Button(
            target_frame,
            text="Auto-Detect",
            style="Modern.TButton",
            command=self.on_auto_detect_window
        )
        auto_detect_btn.pack(side=tk.RIGHT, padx=(0, 5))
        
    def create_control_buttons_section(self, parent):
        """Create main control buttons section"""
        # Control buttons frame
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Recording button
        self.recording_button = ttk.Button(
            control_frame,
            text="🎤 Start Recording",
            style="Record.TButton",
            command=self.on_toggle_recording
        )
        self.recording_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Screenshot button
        screenshot_btn = ttk.Button(
            control_frame,
            text="📸 Screenshot + AI",
            style="Modern.TButton",
            command=self.on_screenshot_analyze
        )
        screenshot_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Visual log button
        visual_log_btn = ttk.Button(
            control_frame,
            text="👁️ Visual Log",
            style="Modern.TButton",
            command=self.on_show_visual_log
        )
        visual_log_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Send button
        send_btn = ttk.Button(
            control_frame,
            text="📤 Send",
            style="Modern.TButton",
            command=self.on_send_text
        )
        send_btn.pack(side=tk.RIGHT)
        
        # Copy button
        copy_btn = ttk.Button(
            control_frame,
            text="📋 Copy",
            style="Modern.TButton",
            command=self.on_copy_text
        )
        copy_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
    def create_text_areas_section(self, parent):
        """Create input and output text areas"""
        # Text areas frame
        text_frame = ttk.Frame(parent)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Input section
        input_label = ttk.Label(text_frame, text="Input Text:", style="Modern.TLabel")
        input_label.pack(anchor=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(
            text_frame,
            height=TEXT_AREAS["input_height"],
            font=UI_FONTS["input"],
            wrap=tk.WORD
        )
        self.input_text.pack(fill=tk.X, pady=(0, 10))
        
        # Output section
        output_label = ttk.Label(text_frame, text="AI Output:", style="Modern.TLabel")
        output_label.pack(anchor=tk.W)
        
        self.output_text = scrolledtext.ScrolledText(
            text_frame,
            height=TEXT_AREAS["output_height"],
            font=UI_FONTS["output"],
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
    def create_status_section(self, parent):
        """Create status bar section"""
        # Status frame
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style="Modern.TLabel",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_label.pack(fill=tk.X, pady=(5, 0))
        
    def show_startup_message(self):
        """Display startup message in output area"""
        try:
            startup_text = "\n".join(STARTUP_MESSAGES)
            self.update_output_text(startup_text)
            
        except Exception as e:
            print(f"Startup message error: {e}")
            
    def update_output_text(self, text, append=False):
        """Update output text area"""
        try:
            self.output_text.config(state=tk.NORMAL)
            
            if append:
                self.output_text.insert(tk.END, f"\n{text}")
            else:
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(1.0, text)
                
            self.output_text.config(state=tk.DISABLED)
            self.output_text.see(tk.END)
            
        except Exception as e:
            print(f"Output text update error: {e}")
            
    def update_status(self, message):
        """Update status bar"""
        try:
            self.status_var.set(f"{datetime.now().strftime('%H:%M:%S')} - {message}")
            
        except Exception as e:
            print(f"Status update error: {e}")
            
    def get_input_text(self):
        """Get text from input area"""
        try:
            return self.input_text.get(1.0, tk.END).strip()
        except:
            return ""
            
    def set_input_text(self, text):
        """Set text in input area"""
        try:
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, text)
        except Exception as e:
            print(f"Input text set error: {e}")
            
    def clear_input_text(self):
        """Clear input text area"""
        try:
            self.input_text.delete(1.0, tk.END)
        except Exception as e:
            print(f"Input text clear error: {e}")
            
    # Event Handlers
    def on_set_target_window(self):
        """Handle set target window button"""
        try:
            window_title = self.target_window_var.get().strip()
            if window_title:
                self.app_controller.window_manager.set_target_window(window_title)
                self.update_status(f"Target window set: {window_title}")
            else:
                messagebox.showwarning("Warning", "Please enter a window title")
                
        except Exception as e:
            print(f"Set target window error: {e}")
            
    def on_auto_detect_window(self):
        """Handle auto-detect window button"""
        try:
            if self.app_controller.window_manager.auto_set_target_window():
                self.target_window_var.set(self.app_controller.window_manager.target_window_title)
                self.update_status("Target window auto-detected")
            else:
                messagebox.showinfo("Info", "No suitable target window found")
                
        except Exception as e:
            print(f"Auto-detect window error: {e}")
            
    def on_toggle_recording(self):
        """Handle recording toggle button"""
        try:
            if not self.is_recording:
                # Start recording
                if self.app_controller.speech_system.start_recording():
                    self.is_recording = True
                    self.recording_button.config(text="🛑 Stop Recording")
                    self.update_status("Recording...")
                    
                    # Start recording thread
                    threading.Thread(target=self.recording_loop, daemon=True).start()
                else:
                    messagebox.showerror("Error", "Failed to start recording")
            else:
                # Stop recording
                self.stop_recording()
                
        except Exception as e:
            print(f"Toggle recording error: {e}")
            
    def recording_loop(self):
        """Recording loop (runs in separate thread)"""
        try:
            while self.is_recording:
                if not self.app_controller.speech_system.record_audio_frame():
                    break
                    
        except Exception as e:
            print(f"Recording loop error: {e}")
            
    def stop_recording(self):
        """Stop recording and process audio"""
        try:
            self.is_recording = False
            self.recording_button.config(text="🎤 Start Recording")
            self.update_status("Processing audio...")
            
            # Process audio in separate thread
            threading.Thread(target=self.process_recording, daemon=True).start()
            
        except Exception as e:
            print(f"Stop recording error: {e}")
            
    def process_recording(self):
        """Process recorded audio (runs in separate thread)"""
        try:
            result = self.app_controller.speech_system.stop_recording()
            
            if result:
                # Update UI on main thread
                self.root.after(0, lambda: self.set_input_text(result))
                self.root.after(0, lambda: self.update_status("Speech recognized"))
            else:
                self.root.after(0, lambda: self.update_status("No speech recognized"))
                
        except Exception as e:
            print(f"Process recording error: {e}")
            
    def on_screenshot_analyze(self):
        """Handle screenshot + analyze button"""
        try:
            self.update_status("Taking screenshot...")
            
            # Run in separate thread
            threading.Thread(target=self.screenshot_analyze_thread, daemon=True).start()
            
        except Exception as e:
            print(f"Screenshot analyze error: {e}")
            
    def screenshot_analyze_thread(self):
        """Screenshot and analyze in separate thread"""
        try:
            screenshot_path, interpretation = self.app_controller.vision_system.capture_and_analyze()
            
            if interpretation:
                # Update UI on main thread
                self.root.after(0, lambda: self.update_output_text(interpretation))
                self.root.after(0, lambda: self.update_status("Screenshot analyzed"))
            else:
                self.root.after(0, lambda: self.update_status("Screenshot analysis failed"))
                
        except Exception as e:
            print(f"Screenshot analyze thread error: {e}")
            
    def on_show_visual_log(self):
        """Handle visual log button"""
        try:
            if not self.visual_log_window or not self.visual_log_window.window.winfo_exists():
                self.visual_log_window = VisualLogWindow()
                
            self.visual_log_window.show()
            self.update_status("Visual log window opened")
            
        except Exception as e:
            print(f"Show visual log error: {e}")
            
    def on_send_text(self):
        """Handle send text button"""
        try:
            text = self.get_input_text()
            if text:
                if self.app_controller.window_manager.send_text_with_enter(text):
                    self.update_status("Text sent successfully")
                    self.app_controller.memory_manager.save_chat_message(text, "send")
                else:
                    messagebox.showerror("Error", "Failed to send text")
            else:
                messagebox.showwarning("Warning", "No text to send")
                
        except Exception as e:
            print(f"Send text error: {e}")
            
    def on_copy_text(self):
        """Handle copy text button"""
        try:
            text = self.get_input_text()
            if text:
                if self.app_controller.window_manager.copy_to_clipboard(text):
                    self.update_status("Text copied to clipboard")
                else:
                    messagebox.showerror("Error", "Failed to copy text")
            else:
                messagebox.showwarning("Warning", "No text to copy")
                
        except Exception as e:
            print(f"Copy text error: {e}")
            
    def run(self):
        """Start the GUI main loop"""
        try:
            if self.root:
                self.root.mainloop()
                
        except Exception as e:
            print(f"GUI main loop error: {e}")
            
    def cleanup(self):
        """Clean up GUI resources"""
        try:
            if self.visual_log_window:
                self.visual_log_window.close()
                
            if self.root:
                self.root.quit()
                
            print("🧹 GUI components cleaned up")
            
        except Exception as e:
            print(f"GUI cleanup error: {e}")
