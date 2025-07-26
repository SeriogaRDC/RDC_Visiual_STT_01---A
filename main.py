"""
Main Application Entry Point - Modular Architecture
==================================================

Clean entry point coordinating all system components:
- Memory Manager: Unified memory system
- Speech System: Advanced STT with filtering  
- Vision System: AI-powered screenshot analysis
- Window Manager: Target window control
- GUI Components: Modern interface

This replaces the 4,300-line monolith with focused modules.
"""

import sys
import os
import signal
import atexit
from datetime import datetime

# Import all our modular components
from config import WINDOW_TITLE, STARTUP_MESSAGES
from memory_manager import MemoryManager
from speech_system import SpeechSystem  
from vision_system import VisionSystem
from window_manager import WindowManager
from gui_components import GUIComponents


class VisualInterpretationSystem:
    """Main application controller - coordinates all components"""
    
    def __init__(self):
        """Initialize all system components"""
        print("🚀 Starting Visual Interpretation System...")
        
        # Initialize core components in proper order
        print("📂 Initializing memory manager...")
        self.memory_manager = MemoryManager()
        
        print("🎤 Initializing speech system...")
        self.speech_system = SpeechSystem(self.memory_manager)
        
        print("👁️ Initializing vision system...")
        self.vision_system = VisionSystem(self.memory_manager)
        
        print("🪟 Initializing window manager...")
        self.window_manager = WindowManager(self.memory_manager)
        
        print("🖥️ Initializing GUI components...")
        self.gui_components = GUIComponents(self)
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        
        # Handle Windows signals properly
        try:
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)
        except AttributeError:
            # Some signals may not be available on Windows
            pass
        
        print("✅ All components initialized successfully")
        
    def start(self):
        """Start the application"""
        try:
            # Log startup
            self.memory_manager.save_system_message(
                "system", "Main", "Visual Interpretation System started"
            )
            
            # Create and show GUI
            print("🖼️ Creating main window...")
            self.gui_components.create_main_window()
            
            # Display startup messages
            startup_text = "\n".join(STARTUP_MESSAGES)
            print(startup_text)
            
            # Start GUI main loop
            print("▶️ Starting GUI main loop...")
            self.gui_components.run()
            
        except Exception as e:
            error_msg = f"Application startup failed: {e}"
            print(f"❌ {error_msg}")
            if hasattr(self, 'memory_manager'):
                self.memory_manager.save_system_message("error", "Main", error_msg)
            sys.exit(1)
            
    def cleanup(self):
        """Clean up all system resources"""
        try:
            print("🧹 Cleaning up system resources...")
            
            # Save final memory state
            if hasattr(self, 'memory_manager'):
                self.memory_manager.save_all()
            
            # Clean up components
            if hasattr(self, 'speech_system'):
                self.speech_system.cleanup()
                
            if hasattr(self, 'gui_components'):
                self.gui_components.cleanup()
            
            # Log shutdown
            if hasattr(self, 'memory_manager'):
                self.memory_manager.save_system_message(
                    "system", "Main", "Visual Interpretation System shutdown"
                )
            
            print("✅ Cleanup completed successfully")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
            
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)


def main():
    """Application entry point"""
    try:
        print(f"🎯 {WINDOW_TITLE}")
        print("=" * 50)
        
        # Create and start the application
        app = VisualInterpretationSystem()
        app.start()
        
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
