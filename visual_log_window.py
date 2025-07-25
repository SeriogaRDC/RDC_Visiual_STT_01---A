"""
Visual Log Window - Simple placeholder implementation
This provides a basic visual log window for the speech-to-text system.
"""

import tkinter as tk
from tkinter import ttk
import json
import os
from datetime import datetime


class VisualLogWindow:
    """Simple visual log window to display vision log entries"""
    
    def __init__(self, parent, log_file_path):
        """Initialize the visual log window"""
        self.parent = parent
        self.log_file_path = log_file_path
        self.window = None
        self.auto_refresh_enabled = tk.BooleanVar(value=False)
        self.auto_refresh_timer = None
        
    def show_window(self):
        """Show the visual log window"""
        try:
            if self.window is None or not self.window.winfo_exists():
                self.create_window()
            else:
                self.window.lift()
                self.window.focus_force()
                
            self.refresh_log_display()
            
        except Exception as e:
            print(f"Visual log window error: {e}")
            if hasattr(self.parent, 'add_chat_message'):
                self.parent.add_chat_message("Error", f"Visual log window error: {e}")
    
    def create_window(self):
        """Create the visual log window interface"""
        self.window = tk.Toplevel(self.parent.root)
        self.window.title("📋 Visual Log Viewer")
        self.window.geometry("800x1200")  # Made twice as tall: 600 -> 1200
        self.window.minsize(600, 800)     # Increased minimum height too
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📋 Visual Log Entries", 
                               font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Log display area
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 10),
                               bg="#f8f9fa", fg="#2c3e50")
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        refresh_btn = ttk.Button(button_frame, text="🔄 Refresh", 
                                command=self.refresh_log_display)
        refresh_btn.pack(side="left", padx=(0, 10))
        
        # Auto-refresh checkbox
        self.auto_refresh_check = ttk.Checkbutton(button_frame, text="⚡ Auto-Refresh (3s)", 
                                                 variable=self.auto_refresh_enabled,
                                                 command=self.toggle_auto_refresh)
        self.auto_refresh_check.pack(side="left", padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Clear Log", 
                              command=self.clear_log)
        clear_btn.pack(side="left", padx=(0, 10))
        
        close_btn = ttk.Button(button_frame, text="✖ Close", 
                              command=self.close_window)
        close_btn.pack(side="right")
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready", foreground="green")
        self.status_label.pack(pady=(5, 0))
        
    def refresh_log_display(self):
        """Refresh the log display with latest entries"""
        try:
            self.log_text.delete(1.0, tk.END)
            
            if not os.path.exists(self.log_file_path):
                self.log_text.insert(tk.END, "No visual log file found.\n")
                self.log_text.insert(tk.END, f"Expected path: {self.log_file_path}\n")
                self.status_label.config(text="No log file", foreground="orange")
                return
            
            # Load and display log entries
            with open(self.log_file_path, 'r', encoding='utf-8') as f:
                log_data = json.load(f)
            
            entries = log_data.get('entries', [])
            
            if not entries:
                self.log_text.insert(tk.END, "No log entries found.\n")
                self.status_label.config(text="Empty log", foreground="orange")
                return
            
            # Display entries (most recent first)
            for i, entry in enumerate(reversed(entries[-50:])):  # Show last 50 entries
                timestamp = entry.get('timestamp', 'Unknown time')
                interpretation = entry.get('interpreted_text', entry.get('interpretation', 'No interpretation'))
                screenshot_file = entry.get('screenshot_filename', entry.get('screenshot_file', 'No file'))
                
                self.log_text.insert(tk.END, f"=== Entry {len(entries) - i} ===\n")
                self.log_text.insert(tk.END, f"📅 Time: {timestamp}\n")
                self.log_text.insert(tk.END, f"📸 File: {screenshot_file}\n")
                self.log_text.insert(tk.END, f"🔍 Interpretation:\n{interpretation}\n\n")
            
            self.status_label.config(text=f"Showing {min(len(entries), 50)} entries", 
                                   foreground="green")
            
            # Auto-scroll to top (most recent)
            self.log_text.see(1.0)
            
        except Exception as e:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, f"Error loading log: {e}\n")
            self.status_label.config(text="Error loading", foreground="red")
    
    def clear_log(self):
        """Clear the visual log file"""
        try:
            # Create empty log structure
            empty_log = {"entries": []}
            
            with open(self.log_file_path, 'w', encoding='utf-8') as f:
                json.dump(empty_log, f, indent=2, ensure_ascii=False)
            
            self.refresh_log_display()
            self.status_label.config(text="Log cleared", foreground="green")
            
            if hasattr(self.parent, 'add_chat_message'):
                self.parent.add_chat_message("System", "📋 Visual log cleared from log window")
            
        except Exception as e:
            self.status_label.config(text="Clear failed", foreground="red")
            if hasattr(self.parent, 'add_chat_message'):
                self.parent.add_chat_message("Error", f"Failed to clear visual log: {e}")
    
    def close_window(self):
        """Close the visual log window"""
        try:
            # Stop auto-refresh timer
            if self.auto_refresh_timer:
                self.window.after_cancel(self.auto_refresh_timer)
                self.auto_refresh_timer = None
                
            if self.window:
                self.window.destroy()
                self.window = None
        except:
            pass
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh functionality"""
        try:
            if self.auto_refresh_enabled.get():
                self.start_auto_refresh()
                self.status_label.config(text="Auto-refresh enabled (3s)", foreground="blue")
            else:
                self.stop_auto_refresh()
                self.status_label.config(text="Auto-refresh disabled", foreground="green")
        except Exception as e:
            print(f"Auto-refresh toggle error: {e}")
    
    def start_auto_refresh(self):
        """Start auto-refresh timer"""
        try:
            if self.auto_refresh_enabled.get() and self.window and self.window.winfo_exists():
                self.refresh_log_display()
                # Schedule next refresh in 3 seconds
                self.auto_refresh_timer = self.window.after(3000, self.start_auto_refresh)
        except Exception as e:
            print(f"Auto-refresh error: {e}")
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        try:
            if self.auto_refresh_timer:
                self.window.after_cancel(self.auto_refresh_timer)
                self.auto_refresh_timer = None
        except:
            pass
