"""
Window Manager - Target Window Control & Message Delivery
=========================================================

Handles all window management functionality:
- Target window detection and focus
- Message delivery to target applications
- Window state monitoring
- Cross-application communication

This replaces the scattered window code from the monolith.
"""

import win32gui
import win32con
import win32clipboard
import time
import pyautogui
from datetime import datetime
from memory_manager import MemoryManager
from config import DEFAULT_TRIGGER_KEYWORDS


class WindowManager:
    """Advanced window management and message delivery"""
    
    def __init__(self, memory_manager):
        """Initialize window manager"""
        self.memory_manager = memory_manager
        self.target_window_title = ""
        self.target_window_handle = None
        self.last_focused_window = None
        
        # Configure pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def set_target_window(self, window_title):
        """Set the target window for message delivery"""
        try:
            self.target_window_title = window_title.strip()
            self.target_window_handle = None
            
            if self.target_window_title:
                # Try to find the window immediately
                self.target_window_handle = self.find_window_by_title(self.target_window_title)
                
                if self.target_window_handle:
                    print(f"🎯 Target window set: '{self.target_window_title}' (Found)")
                    self.memory_manager.save_system_message(
                        "info", "WindowManager", 
                        f"Target window set: '{self.target_window_title}'"
                    )
                else:
                    print(f"🎯 Target window set: '{self.target_window_title}' (Not found yet)")
                    
            else:
                print("🎯 Target window cleared")
                
        except Exception as e:
            error_msg = f"Set target window failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            
    def find_window_by_title(self, title):
        """Find window handle by title (partial match)"""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if title.lower() in window_title.lower():
                        windows.append((hwnd, window_title))
                return True
                
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # Return the first match
                hwnd, full_title = windows[0]
                print(f"🔍 Found window: '{full_title}'")
                return hwnd
                
            return None
            
        except Exception as e:
            print(f"Window search error: {e}")
            return None
            
    def focus_target_window(self):
        """Focus the target window"""
        try:
            if not self.target_window_handle:
                # Try to find it again
                if self.target_window_title:
                    self.target_window_handle = self.find_window_by_title(self.target_window_title)
                    
            if self.target_window_handle:
                # Check if window still exists
                try:
                    win32gui.GetWindowText(self.target_window_handle)
                except:
                    # Window no longer exists, clear handle
                    self.target_window_handle = None
                    return False
                    
                # Focus the window
                win32gui.SetForegroundWindow(self.target_window_handle)
                time.sleep(0.2)  # Give time for focus to change
                
                print(f"✅ Focused target window: '{self.target_window_title}'")
                return True
            else:
                print(f"❌ Target window not found: '{self.target_window_title}'")
                return False
                
        except Exception as e:
            error_msg = f"Focus window failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            return False
            
    def send_text_to_target(self, text):
        """Send text to target window"""
        try:
            if not text.strip():
                return False
                
            # Focus target window first
            if not self.focus_target_window():
                return False
                
            # Small delay to ensure focus
            time.sleep(0.3)
            
            # Type the text
            pyautogui.typewrite(text, interval=0.02)
            
            print(f"📤 Text sent to '{self.target_window_title}': '{text[:50]}...'")
            
            self.memory_manager.save_system_message(
                "info", "WindowManager", 
                f"Text sent to '{self.target_window_title}': {len(text)} chars"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Send text failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            return False
            
    def send_text_with_enter(self, text):
        """Send text to target window and press Enter"""
        try:
            if self.send_text_to_target(text):
                time.sleep(0.1)
                pyautogui.press('enter')
                print(f"⏎ Enter pressed after text delivery")
                return True
            return False
            
        except Exception as e:
            error_msg = f"Send text with enter failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            return False
            
    def copy_to_clipboard(self, text):
        """Copy text to Windows clipboard"""
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text)
            win32clipboard.CloseClipboard()
            
            print(f"📋 Text copied to clipboard: {len(text)} chars")
            
            self.memory_manager.save_system_message(
                "info", "WindowManager", 
                f"Text copied to clipboard: {len(text)} chars"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Clipboard copy failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            return False
            
    def get_clipboard_text(self):
        """Get text from Windows clipboard"""
        try:
            win32clipboard.OpenClipboard()
            clipboard_text = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            
            return clipboard_text
            
        except Exception as e:
            print(f"Clipboard read error: {e}")
            return ""
            
    def get_active_window_title(self):
        """Get title of currently active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title
            
        except Exception as e:
            print(f"Active window error: {e}")
            return ""
            
    def list_visible_windows(self):
        """Get list of all visible windows"""
        try:
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title.strip():  # Only include windows with titles
                        windows.append((hwnd, title))
                return True
                
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            # Sort by title for easier reading
            windows.sort(key=lambda x: x[1].lower())
            
            return windows
            
        except Exception as e:
            print(f"Window list error: {e}")
            return []
            
    def find_best_window_match(self, keywords=None):
        """Find best window match based on keywords"""
        try:
            if not keywords:
                keywords = DEFAULT_TRIGGER_KEYWORDS
                
            visible_windows = self.list_visible_windows()
            
            # Score windows based on keyword matches
            scored_windows = []
            
            for hwnd, title in visible_windows:
                score = 0
                title_lower = title.lower()
                
                for keyword in keywords:
                    if keyword.lower() in title_lower:
                        score += 1
                        
                if score > 0:
                    scored_windows.append((hwnd, title, score))
                    
            # Sort by score (highest first)
            scored_windows.sort(key=lambda x: x[2], reverse=True)
            
            if scored_windows:
                hwnd, title, score = scored_windows[0]
                print(f"🎯 Best window match: '{title}' (score: {score})")
                return hwnd, title
            else:
                print("🔍 No matching windows found")
                return None, None
                
        except Exception as e:
            print(f"Window match error: {e}")
            return None, None
            
    def auto_set_target_window(self):
        """Automatically set target window based on keywords"""
        try:
            hwnd, title = self.find_best_window_match()
            
            if title:
                self.target_window_title = title
                self.target_window_handle = hwnd
                
                print(f"🎯 Auto-set target window: '{title}'")
                self.memory_manager.save_system_message(
                    "info", "WindowManager", 
                    f"Auto-set target window: '{title}'"
                )
                
                return True
            else:
                print("❌ No suitable target window found")
                return False
                
        except Exception as e:
            error_msg = f"Auto-set target window failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "WindowManager", error_msg)
            return False
            
    def get_status(self):
        """Get current window manager status"""
        try:
            active_window = self.get_active_window_title()
            window_count = len(self.list_visible_windows())
            
            return {
                "target_window": self.target_window_title,
                "target_found": self.target_window_handle is not None,
                "active_window": active_window,
                "visible_windows": window_count
            }
            
        except Exception as e:
            print(f"Window status error: {e}")
            return {"error": str(e)}
