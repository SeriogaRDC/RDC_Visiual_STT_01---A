"""
Vision System - AI-Powered Screenshot Analysis
=============================================

Handles all visual interpretation functionality:
- Screenshot capture
- Ollama AI integration for vision analysis
- Image processing and analysis
- Vision result management

This replaces the scattered vision code from the monolith.
"""

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageGrab
from datetime import datetime
import requests
import json
import base64
from io import BytesIO
from memory_manager import MemoryManager
from config import (
    OLLAMA_BASE_URL, VISION_MODEL_NAME, SCREENSHOTS_DIR,
    VISION_SYSTEM_MESSAGE, REQUEST_TIMEOUT
)


class VisionSystem:
    """AI-powered screenshot analysis system"""
    
    def __init__(self, memory_manager):
        """Initialize vision system"""
        self.memory_manager = memory_manager
        self.last_screenshot_path = None
        
        # Ensure screenshots directory exists
        self.ensure_screenshots_dir()
        
    def ensure_screenshots_dir(self):
        """Ensure screenshots directory exists"""
        try:
            os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
            print(f"📁 Screenshots directory ready: {SCREENSHOTS_DIR}")
            
        except Exception as e:
            error_msg = f"Screenshots directory creation failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            
    def take_screenshot(self, save_file=True):
        """Capture full screen screenshot"""
        try:
            # Capture the screen
            screenshot = ImageGrab.grab()
            
            if save_file:
                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screen_{timestamp}.png"
                self.last_screenshot_path = os.path.join(SCREENSHOTS_DIR, filename)
                
                # Save screenshot
                screenshot.save(self.last_screenshot_path)
                print(f"📸 Screenshot saved: {filename}")
                
                self.memory_manager.save_system_message(
                    "info", "VisionSystem", 
                    f"Screenshot captured: {filename}"
                )
                
                return self.last_screenshot_path, screenshot
            else:
                # Return image without saving
                return None, screenshot
                
        except Exception as e:
            error_msg = f"Screenshot capture failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None, None
            
    def image_to_base64(self, image):
        """Convert PIL image to base64 for Ollama"""
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Save to bytes buffer
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            return image_base64
            
        except Exception as e:
            error_msg = f"Image to base64 conversion failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None
            
    def analyze_screenshot_with_ollama(self, image, custom_prompt=None):
        """Send screenshot to Ollama for AI analysis"""
        try:
            # Convert image to base64
            image_base64 = self.image_to_base64(image)
            if not image_base64:
                return None
                
            # Prepare the prompt
            prompt = custom_prompt if custom_prompt else VISION_SYSTEM_MESSAGE
            
            # Prepare request data
            request_data = {
                "model": VISION_MODEL_NAME,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            print(f"🔍 Analyzing screenshot with {VISION_MODEL_NAME}...")
            
            # Send request to Ollama
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                headers={"Content-Type": "application/json"},
                data=json.dumps(request_data),
                timeout=REQUEST_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                interpretation = result.get('response', 'No response received')
                
                print(f"✅ Vision analysis completed")
                print(f"📝 Analysis: {interpretation[:100]}...")
                
                self.memory_manager.save_system_message(
                    "info", "VisionSystem", 
                    f"Vision analysis completed ({len(interpretation)} chars)"
                )
                
                return interpretation
            else:
                error_msg = f"Ollama request failed: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
                return None
                
        except requests.exceptions.Timeout:
            error_msg = f"Ollama request timed out after {REQUEST_TIMEOUT} seconds"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None
            
        except Exception as e:
            error_msg = f"Ollama analysis failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None
            
    def capture_and_analyze(self, custom_prompt=None):
        """Capture screenshot and analyze it with AI"""
        try:
            # Take screenshot
            screenshot_path, screenshot_image = self.take_screenshot()
            if not screenshot_image:
                return None, None
                
            # Analyze with Ollama
            interpretation = self.analyze_screenshot_with_ollama(screenshot_image, custom_prompt)
            if not interpretation:
                return screenshot_path, None
                
            # Save to vision memory
            if screenshot_path:
                filename = os.path.basename(screenshot_path)
                self.memory_manager.save_vision_result(filename, interpretation)
                
            return screenshot_path, interpretation
            
        except Exception as e:
            error_msg = f"Capture and analyze failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None, None
            
    def analyze_existing_image(self, image_path, custom_prompt=None):
        """Analyze an existing image file"""
        try:
            if not os.path.exists(image_path):
                print(f"❌ Image file not found: {image_path}")
                return None
                
            # Load image
            image = Image.open(image_path)
            
            # Analyze with Ollama
            interpretation = self.analyze_screenshot_with_ollama(image, custom_prompt)
            
            if interpretation:
                # Save to vision memory
                filename = os.path.basename(image_path)
                self.memory_manager.save_vision_result(filename, interpretation)
                
            return interpretation
            
        except Exception as e:
            error_msg = f"Existing image analysis failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            return None
            
    def get_recent_screenshots(self, count=5):
        """Get list of recent screenshot files"""
        try:
            if not os.path.exists(SCREENSHOTS_DIR):
                return []
                
            # Get all PNG files
            screenshots = []
            for filename in os.listdir(SCREENSHOTS_DIR):
                if filename.lower().endswith('.png'):
                    filepath = os.path.join(SCREENSHOTS_DIR, filename)
                    # Get modification time
                    mtime = os.path.getmtime(filepath)
                    screenshots.append((filepath, mtime, filename))
                    
            # Sort by modification time (newest first)
            screenshots.sort(key=lambda x: x[1], reverse=True)
            
            # Return recent screenshots
            return [(path, name) for path, mtime, name in screenshots[:count]]
            
        except Exception as e:
            print(f"Recent screenshots error: {e}")
            return []
            
    def cleanup_old_screenshots(self, keep_count=20):
        """Clean up old screenshot files"""
        try:
            screenshots = self.get_recent_screenshots(count=1000)  # Get all
            
            if len(screenshots) > keep_count:
                # Delete old screenshots
                for path, name in screenshots[keep_count:]:
                    try:
                        os.remove(path)
                        print(f"🗑️ Deleted old screenshot: {name}")
                    except Exception as e:
                        print(f"Delete error for {name}: {e}")
                        
                self.memory_manager.save_system_message(
                    "info", "VisionSystem", 
                    f"Cleaned up {len(screenshots) - keep_count} old screenshots"
                )
                
        except Exception as e:
            error_msg = f"Screenshot cleanup failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "VisionSystem", error_msg)
            
    def get_status(self):
        """Get current vision system status"""
        try:
            screenshot_count = len(self.get_recent_screenshots(count=1000))
            
            return {
                "screenshots_dir": SCREENSHOTS_DIR,
                "screenshot_count": screenshot_count,
                "last_screenshot": self.last_screenshot_path,
                "vision_model": VISION_MODEL_NAME,
                "ollama_url": OLLAMA_BASE_URL
            }
            
        except Exception as e:
            print(f"Vision status error: {e}")
            return {"error": str(e)}
