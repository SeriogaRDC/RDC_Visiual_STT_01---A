"""
Speech System - Advanced Whisper STT with Hallucination Filtering
================================================================

Handles all speech-to-text functionality:
- Whisper model management
- Real-time audio capture
- Hallucination filtering (the magical thank you filter!)
- Speech artifacts removal

This replaces the scattered speech code from the monolith.
"""

import pyaudio
import wave
import whisper
import os
import tempfile
import tkinter as tk
from datetime import datetime
from memory_manager import MemoryManager
from config import (
    WHISPER_ARTIFACTS, WHISPER_MODEL_NAME, AUDIO_CHUNK, 
    AUDIO_CHANNELS, AUDIO_RATE, RECORDING_SILENCE_THRESHOLD,
    RECORDING_SILENCE_DURATION
)

# Set proper audio format
AUDIO_FORMAT = pyaudio.paInt16


class SpeechSystem:
    """Advanced STT system with intelligent filtering"""
    
    def __init__(self, memory_manager):
        """Initialize speech system"""
        self.memory_manager = memory_manager
        self.whisper_model = None
        self.is_recording = False
        self.audio = None
        self.stream = None
        self.frames = []
        
        # Initialize Whisper
        self.load_whisper_model()
        
    def load_whisper_model(self):
        """Load Whisper model for STT"""
        try:
            print(f"🎤 Loading Whisper {WHISPER_MODEL_NAME} model...")
            self.whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
            print(f"✅ Whisper {WHISPER_MODEL_NAME} model loaded successfully")
            
            self.memory_manager.save_system_message(
                "system", "SpeechSystem", 
                f"Whisper {WHISPER_MODEL_NAME} model loaded successfully"
            )
            
        except Exception as e:
            error_msg = f"Whisper model loading failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "SpeechSystem", error_msg)
            self.whisper_model = None
            
    def start_recording(self):
        """Start real-time audio recording"""
        try:
            if self.is_recording:
                return False
                
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=AUDIO_FORMAT,
                channels=AUDIO_CHANNELS,
                rate=AUDIO_RATE,
                input=True,
                frames_per_buffer=AUDIO_CHUNK
            )
            
            self.is_recording = True
            self.frames = []
            print("🎤 Recording started...")
            
            self.memory_manager.save_system_message(
                "info", "SpeechSystem", "Audio recording started"
            )
            
            return True
            
        except Exception as e:
            error_msg = f"Recording start failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "SpeechSystem", error_msg)
            return False
            
    def stop_recording(self):
        """Stop recording and process audio"""
        try:
            if not self.is_recording:
                return None
                
            self.is_recording = False
            
            # Stop and close stream
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                
            if self.audio:
                self.audio.terminate()
                
            print("🛑 Recording stopped")
            
            # Process the recorded audio
            return self.process_recorded_audio()
            
        except Exception as e:
            error_msg = f"Recording stop failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "SpeechSystem", error_msg)
            return None
            
    def record_audio_frame(self):
        """Record single audio frame (call this in loop while recording)"""
        try:
            if self.is_recording and self.stream:
                data = self.stream.read(AUDIO_CHUNK, exception_on_overflow=False)
                self.frames.append(data)
                return True
            return False
            
        except Exception as e:
            print(f"Frame recording error: {e}")
            return False
            
    def process_recorded_audio(self):
        """Process recorded frames with Whisper"""
        try:
            if not self.frames or not self.whisper_model:
                return None
                
            # Save frames to temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                temp_path = temp_audio.name
                
                # Write WAV file
                with wave.open(temp_path, 'wb') as wf:
                    wf.setnchannels(AUDIO_CHANNELS)
                    wf.setsampwidth(self.audio.get_sample_size(AUDIO_FORMAT))
                    wf.setframerate(AUDIO_RATE)
                    wf.writeframes(b''.join(self.frames))
                    
            # Process with Whisper
            result = self.whisper_model.transcribe(temp_path)
            transcribed_text = result["text"].strip()
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Apply hallucination filtering
            filtered_text = self.filter_speech_artifacts(transcribed_text)
            
            if filtered_text:
                print(f"🎯 Speech recognized: '{filtered_text}'")
                self.memory_manager.save_chat_message(filtered_text, "speech_input")
                
                self.memory_manager.save_system_message(
                    "info", "SpeechSystem", 
                    f"Speech processed: '{filtered_text}'"
                )
                
                return filtered_text
            else:
                print("🚫 Speech filtered as artifact")
                return None
                
        except Exception as e:
            error_msg = f"Audio processing failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "SpeechSystem", error_msg)
            return None
            
    def filter_speech_artifacts(self, text):
        """Apply intelligent hallucination filtering"""
        if not text or not text.strip():
            return None
            
        text_clean = text.strip().lower()
        
        # The magical filter! Remove isolated artifacts but preserve contextual speech
        for artifact in WHISPER_ARTIFACTS:
            artifact_lower = artifact.lower()
            
            # If the text is EXACTLY the artifact (isolated), filter it out
            if text_clean == artifact_lower:
                print(f"🔍 Filtered isolated artifact: '{text}'")
                return None
                
            # If it's just the artifact with punctuation, filter it
            if text_clean.replace(".", "").replace(",", "").replace("!", "").replace("?", "") == artifact_lower:
                print(f"🔍 Filtered punctuated artifact: '{text}'")
                return None
                
        # If we get here, it's real speech - return original text with proper case
        return text.strip()
        
    def quick_listen(self, duration_seconds=3):
        """Quick listen for specified duration"""
        try:
            if not self.start_recording():
                return None
                
            print(f"🎤 Quick listening for {duration_seconds} seconds...")
            
            # Simple duration-based recording
            import time
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                if not self.record_audio_frame():
                    break
                time.sleep(0.01)  # Small delay to prevent CPU spinning
                
            return self.stop_recording()
            
        except Exception as e:
            error_msg = f"Quick listen failed: {e}"
            print(f"❌ {error_msg}")
            self.memory_manager.save_system_message("error", "SpeechSystem", error_msg)
            return None
            
    def cleanup(self):
        """Clean up audio resources"""
        try:
            if self.is_recording:
                self.stop_recording()
                
            print("🧹 Speech system cleaned up")
            
        except Exception as e:
            print(f"Speech cleanup error: {e}")
            
    def get_status(self):
        """Get current speech system status"""
        return {
            "model_loaded": self.whisper_model is not None,
            "is_recording": self.is_recording,
            "model_name": WHISPER_MODEL_NAME,
            "artifacts_count": len(WHISPER_ARTIFACTS)
        }
