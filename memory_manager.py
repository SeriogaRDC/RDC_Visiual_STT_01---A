"""
Memory Manager - Unified Memory System
=====================================

Handles all three types of memory:
- System Memory: Debug/technical logs  
- Chat Memory: User conversations & voice input
- Vision Memory: Screenshot analysis results

This replaces the scattered memory code from the monolith.
"""

import json
import os
from datetime import datetime
from config import (
    SYSTEM_MEMORY_FILE, CHAT_MEMORY_FILE, VISION_MEMORY_FILE,
    MAX_SYSTEM_MEMORY_ENTRIES, MAX_CHAT_MEMORY_ENTRIES
)


class MemoryManager:
    """Centralized memory management for all system components"""
    
    def __init__(self):
        """Initialize memory systems"""
        self.system_memory = []
        self.chat_memory = []
        
        # Load existing memory
        self.load_all_memory()
        
    def load_all_memory(self):
        """Load all memory types from files"""
        self.load_system_memory()
        self.load_chat_memory()
        
    def load_system_memory(self):
        """Load system memory (debug/technical logs)"""
        try:
            if os.path.exists(SYSTEM_MEMORY_FILE):
                with open(SYSTEM_MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.system_memory = data.get('entries', [])
                    print(f"📂 Loaded {len(self.system_memory)} system memory entries")
            else:
                self.system_memory = []
                
        except Exception as e:
            print(f"System memory load error: {e}")
            self.system_memory = []
            
    def load_chat_memory(self):
        """Load chat memory (conversations & voice)"""
        try:
            if os.path.exists(CHAT_MEMORY_FILE):
                with open(CHAT_MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.chat_memory = data.get('entries', [])
                    print(f"📂 Loaded {len(self.chat_memory)} chat memory entries")
            else:
                self.chat_memory = []
                
        except Exception as e:
            print(f"Chat memory load error: {e}")
            self.chat_memory = []
            
    def save_system_message(self, message_type, sender, content):
        """Save system/debug messages to system memory"""
        try:
            memory_entry = {
                "timestamp": datetime.now().isoformat(),
                "type": message_type,  # "system", "debug", "error", "info"
                "sender": sender,
                "content": content,
                "length": len(content)
            }
            
            self.system_memory.append(memory_entry)
            self.write_system_memory_to_file()
            
        except Exception as e:
            print(f"System memory save error: {e}")
            
    def save_chat_message(self, input_text, action="input"):
        """Save user conversations and input to chat memory"""
        try:
            if not input_text.strip():
                return
                
            chat_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,  # "input", "send", "clear", "copy"
                "text": input_text.strip(),
                "length": len(input_text.strip())
            }
            
            self.chat_memory.append(chat_entry)
            self.write_chat_memory_to_file()
            
        except Exception as e:
            print(f"Chat memory save error: {e}")
            
    def save_vision_result(self, filename, interpretation):
        """Save vision analysis result to vision memory"""
        try:
            # Load existing vision log
            if os.path.exists(VISION_MEMORY_FILE):
                with open(VISION_MEMORY_FILE, 'r', encoding='utf-8') as f:
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
            with open(VISION_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Vision memory save error: {e}")
            
    def write_system_memory_to_file(self):
        """Write system memory to JSON file"""
        try:
            memory_data = {
                "total_entries": len(self.system_memory),
                "last_updated": datetime.now().isoformat(),
                "entries": self.system_memory[-MAX_SYSTEM_MEMORY_ENTRIES:]  # Keep recent entries
            }
            
            with open(SYSTEM_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"System memory file write error: {e}")
            
    def write_chat_memory_to_file(self):
        """Write chat memory to JSON file"""
        try:
            chat_data = {
                "total_entries": len(self.chat_memory),
                "last_updated": datetime.now().isoformat(),
                "entries": self.chat_memory[-MAX_CHAT_MEMORY_ENTRIES:]  # Keep recent entries
            }
            
            with open(CHAT_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(chat_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Chat memory file write error: {e}")
            
    def clear_chat_memory(self):
        """Clear chat memory completely"""
        try:
            self.chat_memory = []
            empty_chat = {
                "total_entries": 0, 
                "last_updated": datetime.now().isoformat(), 
                "entries": []
            }
            with open(CHAT_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(empty_chat, f, indent=2, ensure_ascii=False)
                
            return True
            
        except Exception as e:
            print(f"Chat memory clear error: {e}")
            return False
            
    def clear_all_memory(self):
        """Clear all memory files - DANGER ZONE!"""
        try:
            # Clear chat memory
            self.chat_memory = []
            empty_chat = {"total_entries": 0, "last_updated": datetime.now().isoformat(), "entries": []}
            with open(CHAT_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(empty_chat, f, indent=2, ensure_ascii=False)
            
            # Clear system memory
            self.system_memory = []
            empty_system = {"total_entries": 0, "last_updated": datetime.now().isoformat(), "entries": []}
            with open(SYSTEM_MEMORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(empty_system, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            print(f"Memory cleaning error: {e}")
            return False
            
    def get_vision_memory(self):
        """Get recent vision memory entries"""
        try:
            if os.path.exists(VISION_MEMORY_FILE):
                with open(VISION_MEMORY_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('entries', [])
            return []
            
        except Exception as e:
            print(f"Vision memory read error: {e}")
            return []
            
    def save_all(self):
        """Save all memory systems to files"""
        self.write_system_memory_to_file()
        self.write_chat_memory_to_file()
        print("💾 All memory systems saved")
