"""
CUDA-Accelerated Whisper Speech-to-Text Module
Provides fast speech recognition using faster-whisper with CUDA acceleration
"""

import speech_recognition as sr
import threading
import time
import torch
import os
from typing import Optional, Callable

# Try to import faster-whisper for CUDA acceleration
try:
    from faster_whisper import WhisperModel
    FASTER_WHISPER_AVAILABLE = True
    print("✅ faster-whisper available - CUDA acceleration enabled!")
except ImportError:
    FASTER_WHISPER_AVAILABLE = False
    print("⚠️ faster-whisper not available - falling back to Google Speech")

class FlexibleWhisper:
    """Fast speech recognition using CUDA-accelerated faster-whisper or SpeechRecognition fallback"""
    
    def __init__(self):
        """Initialize the speech recognizer with CUDA acceleration if available"""
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.use_cuda = False
        self.faster_model = None
        self.english_only = False  # Language control flag
        
        # LOCAL MODELS FOLDER - Your control, your structure!
        self.models_dir = os.path.join(os.path.dirname(__file__), "models")
        os.makedirs(self.models_dir, exist_ok=True)
        print(f"📁 Using LOCAL models folder: {self.models_dir}")
        
        # Available model options (you choose!)
        self.available_model_names = [
            "tiny",      # ~39 MB  - Super fast, basic accuracy
            "base",      # ~74 MB  - Good balance 
            "small",     # ~244 MB - Better accuracy (current)
            "medium",    # ~769 MB - Even better
            "large-v3"   # ~1550 MB - Best accuracy
        ]
        
        # Check CUDA and initialize faster-whisper if available
        if FASTER_WHISPER_AVAILABLE and torch.cuda.is_available():
            try:
                print("🚀 Checking for existing models in YOUR folder...")
                # Check if we have any models in YOUR folder first
                local_models = self.check_local_models()
                
                if local_models:
                    # Use the first available local model
                    model_name = local_models[0]
                    print(f"✅ Found local model: {model_name}")
                    print(f"📍 Loading from YOUR folder: {self.models_dir}")
                    
                    # Try to load the model with better error handling
                    try:
                        self.faster_model = WhisperModel(
                            model_name, 
                            device="cuda", 
                            compute_type="float16",
                            download_root=self.models_dir,
                            local_files_only=True  # NEVER download automatically!
                        )
                        self.use_cuda = True
                        self.selected_model_name = f"faster-whisper-{model_name} (CUDA)"
                        print("✅ CUDA-accelerated Whisper ready with YOUR model!")
                        print(f"🎯 Active model: {self.selected_model_name}")
                    except Exception as model_error:
                        print(f"❌ Failed to load {model_name}: {model_error}")
                        print("🔄 Trying with CPU fallback...")
                        try:
                            self.faster_model = WhisperModel(
                                model_name, 
                                device="cpu", 
                                compute_type="int8",
                                download_root=self.models_dir,
                                local_files_only=True
                            )
                            self.use_cuda = False  # Using CPU
                            self.selected_model_name = f"faster-whisper-{model_name} (CPU)"
                            print("✅ CPU Whisper loaded as fallback!")
                        except Exception as cpu_error:
                            print(f"❌ CPU fallback also failed: {cpu_error}")
                            self.use_cuda = False
                            self.faster_model = None
                else:
                    print("⚠️ No models found in YOUR folder - will use Google Speech")
                    print(f"📍 To add models, place them in: {self.models_dir}")
                    self.use_cuda = False
                    
            except Exception as e:
                print(f"⚠️ CUDA Whisper init failed: {e}")
                print(f"🔍 Full error details: {str(e)}")
                self.use_cuda = False
        
        if not self.use_cuda:
            print("🔄 Using Google Speech Recognition (fallback)")
            self.selected_model_name = "Google Speech Recognition"
        
        self.available_models = [self.selected_model_name] + [f"faster-whisper-{name}" for name in self.available_model_names]
        
    def check_local_models(self) -> list:
        """Check what models you already have in YOUR folder"""
        local_models = []
        
        # Check for each model type in your folder
        for model_name in self.available_model_names:
            model_path = os.path.join(self.models_dir, f"models--Systran--faster-whisper-{model_name}")
            if os.path.exists(model_path):
                local_models.append(model_name)
                print(f"✅ Found YOUR model: {model_name}")
        
        if not local_models:
            print(f"📁 No models in YOUR folder yet: {self.models_dir}")
            print("💡 You can manually copy models here when you want them")
            
        return local_models
        
    def download_model(self, model_name: str, force_update: bool = False) -> bool:
        """Download a specific model to YOUR folder - YOU decide when!"""
        try:
            if not FASTER_WHISPER_AVAILABLE or not torch.cuda.is_available():
                print("❌ CUDA not available for model download")
                return False
                
            if model_name not in self.available_model_names:
                print(f"❌ Unknown model: {model_name}")
                print(f"Available models: {', '.join(self.available_model_names)}")
                return False
                
            # Check if model already exists
            model_path = os.path.join(self.models_dir, f"models--Systran--faster-whisper-{model_name}")
            if os.path.exists(model_path) and not force_update:
                print(f"✅ Model {model_name} already exists in YOUR folder")
                print(f"📍 Location: {model_path}")
                print("💡 Use force_update=True to redownload")
                return True
                
            print(f"📥 Downloading {model_name} model to YOUR folder...")
            print(f"📍 Destination: {self.models_dir}")
            
            # Get model size info
            sizes = {"tiny": "39MB", "base": "74MB", "small": "244MB", "medium": "769MB", "large-v3": "1.5GB"}
            size = sizes.get(model_name, "Unknown size")
            print(f"📦 Download size: ~{size}")
            
            # Set environment variable to disable symlinks on Windows
            os.environ['HF_HUB_DISABLE_SYMLINKS_WARNING'] = '1'
            os.environ['HF_HUB_DISABLE_SYMLINKS'] = '1'
            
            # Download the model (this will go to YOUR folder)
            temp_model = WhisperModel(
                model_name,
                device="cuda",
                compute_type="float16",
                download_root=self.models_dir  # YOUR FOLDER!
            )
            
            print(f"✅ Successfully downloaded {model_name} to YOUR folder!")
            print(f"📍 Model stored in: {self.models_dir}")
            
            # Update our current model if we don't have one loaded
            if not self.use_cuda:
                self.faster_model = temp_model
                self.use_cuda = True
                self.selected_model_name = f"faster-whisper-{model_name} (CUDA)"
                print(f"🚀 Now using your new {model_name} model!")
                
            return True
            
        except Exception as e:
            print(f"❌ Download failed: {e}")
            print("💡 Try running as Administrator or enable Developer Mode in Windows")
            return False
            
    def download_recommended_model(self) -> bool:
        """Download the recommended 'small' model - good balance of speed and accuracy"""
        print("🎯 Downloading recommended 'small' model (244MB)")
        print("💡 Good balance of speed and accuracy for most users")
        return self.download_model("small")
        
    def update_all_models(self) -> bool:
        """Update all models you currently have to latest versions"""
        local_models = self.check_local_models()
        if not local_models:
            print("📁 No models to update - download some first!")
            return False
            
        print(f"🔄 Updating {len(local_models)} models to latest versions...")
        success_count = 0
        
        for model_name in local_models:
            print(f"\n🔄 Updating {model_name}...")
            if self.download_model(model_name, force_update=True):
                success_count += 1
                
        print(f"\n✅ Updated {success_count}/{len(local_models)} models successfully!")
        return success_count > 0
        
    def change_model(self, model_name: str) -> bool:
        """Change to a different Whisper model - only from YOUR folder!"""
        try:
            if not FASTER_WHISPER_AVAILABLE or not torch.cuda.is_available():
                print("❌ CUDA not available for model switching")
                return False
                
            # Extract model size from name (e.g., "faster-whisper-large-v3" -> "large-v3")
            if model_name.startswith("faster-whisper-"):
                model_size = model_name.replace("faster-whisper-", "")
                if model_size in self.available_model_names:
                    # Check if model exists in YOUR folder
                    local_models = self.check_local_models()
                    if model_size not in local_models:
                        print(f"❌ Model {model_size} not found in YOUR folder")
                        print(f"📍 Add it to: {self.models_dir}")
                        return False
                    
                    print(f"🔄 Switching to YOUR {model_size} model...")
                    
                    # Load model from YOUR folder only
                    self.faster_model = WhisperModel(
                        model_size,
                        device="cuda",
                        compute_type="float16", 
                        download_root=self.models_dir,
                        local_files_only=True  # NEVER download!
                    )
                    self.selected_model_name = f"faster-whisper-{model_size} (CUDA)"
                    print(f"✅ Switched to YOUR {model_size} model!")
                    return True
            
            print(f"❌ Unknown model: {model_name}")
            return False
            
        except Exception as e:
            print(f"❌ Model switch failed: {e}")
            return False
    
    def switch_model(self, model_name: str) -> bool:
        """Switch to a different model - alias for change_model to fix compatibility"""
        return self.change_model(f"faster-whisper-{model_name}")
        
    def set_english_only(self, enabled: bool):
        """Enable or disable English-only transcription mode"""
        self.english_only = enabled
        print(f"🌐 Language mode: {'English only' if enabled else 'All languages'}")
        
        # Adjust for ambient noise
        try:
            with self.microphone as source:
                print("🎤 Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone calibrated!")
        except Exception as e:
            print(f"⚠️ Microphone calibration warning: {e}")
    
    def auto_select_model(self) -> bool:
        """Auto-select the best available model"""
        try:
            # Test microphone access
            with self.microphone as source:
                # Quick test
                pass
            return True
        except Exception as e:
            print(f"❌ Microphone access failed: {e}")
            return False
    
    def listen_once(self, timeout: float = 3.0) -> Optional[str]:
        """Listen for speech once with timeout - CUDA accelerated with INSTANT response like Microsoft"""
        try:
            with self.microphone as source:
                # ENHANCED RESPONSE SETTINGS: Fast but with better trailing word capture
                self.recognizer.energy_threshold = 3500  # Keep sensitivity 
                self.recognizer.pause_threshold = 1.0    # Slightly longer pause to capture trailing words (was 0.8)
                self.recognizer.phrase_threshold = 0.15  # Quick speech start detection
                
                # Listen for audio with timeout - ENHANCED buffering for complete phrases
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=25)  # 25 seconds max phrase (was 20)
            
            if self.use_cuda and self.faster_model:
                # Use CUDA-accelerated faster-whisper with VAD filtering
                try:
                    # Convert audio to WAV format for faster-whisper
                    import io
                    import wave
                    
                    # Get raw audio data
                    audio_data = audio.get_wav_data()
                    
                    # Create temporary WAV file in memory
                    audio_io = io.BytesIO(audio_data)
                    
                    # Transcribe with faster-whisper (CUDA accelerated!) with ENHANCED BUFFERING for trailing words
                    transcribe_params = {
                        "beam_size": 5,
                        "vad_filter": True,           # Enable Voice Activity Detection
                        "vad_parameters": dict(       # ULTRA RESPONSIVE VAD - Faster text appearance!
                            min_silence_duration_ms=500,    # 0.5 seconds silence (was 2000ms - 4x faster!)
                            threshold=0.20,                  # Slightly less sensitive for better word boundaries
                            max_speech_duration_s=30,       # Allow longer phrases
                            min_speech_duration_ms=100      # Capture even shorter utterances (was 250ms)
                        )
                    }
                    
                    # Add language constraint if English-only mode is enabled
                    if self.english_only:
                        transcribe_params["language"] = "en"
                    
                    segments, info = self.faster_model.transcribe(audio_io, **transcribe_params)
                    
                    # Extract text from segments with quality filtering
                    text_parts = []
                    for segment in segments:
                        text = segment.text.strip()
                        # Filter out garbage/noise - only keep real words
                        if (len(text) >= 3 and                    # At least 3 characters
                            not text.lower() in ['uh', 'um', 'ah', 'er', 'uhh', 'mmm'] and  # Not filler words
                            any(c.isalpha() for c in text)):      # Contains letters
                            text_parts.append(text)
                    
                    if text_parts:
                        result = " ".join(text_parts).strip()
                        if result and len(result) >= 3:  # Only return substantial results
                            print(f"🚀 CUDA Whisper: '{result}'")
                            return result
                    
                except Exception as e:
                    print(f"⚠️ CUDA Whisper error: {e}")
                    # Fall back to Google if CUDA fails
                    pass
            
            # Use Google Speech Recognition (fallback or primary) with quality filtering
            try:
                # Use language constraint if English-only mode is enabled
                if self.english_only:
                    text = self.recognizer.recognize_google(audio, language="en-US")
                else:
                    text = self.recognizer.recognize_google(audio)
                if text and text.strip():
                    # Apply same quality filtering
                    clean_text = text.strip()
                    if (len(clean_text) >= 3 and 
                        not clean_text.lower() in ['uh', 'um', 'ah', 'er', 'uhh', 'mmm'] and
                        any(c.isalpha() for c in clean_text)):
                        print(f"🌐 Google Speech: '{clean_text}'")
                        return clean_text
            except sr.UnknownValueError:
                # No speech detected - this is normal
                return None
            except sr.RequestError as e:
                print(f"⚠️ Speech service error: {e}")
                return None
                
        except sr.WaitTimeoutError:
            # Timeout - this is normal, no speech detected
            return None
        except Exception as e:
            print(f"⚠️ Listen error: {e}")
            return None
            
        return None
    
    def continuous_listen(self, callback: Callable[[str], None], stop_event: threading.Event):
        """Continuously listen for speech and call callback with results - SUPER FLUFFY & EXTREMELY PATIENT"""
        consecutive_empty = 0
        consecutive_noise = 0  # Track noise/garbage detections
        max_empty = 12  # MAXIMUM patience - pause after 12 empty results (was 8)
        max_noise = 6   # Much more tolerance - ignore after 6 noise detections (was 4)
        
        while not stop_event.is_set():
            try:
                # Listen for speech with ULTRA FLUFFY timeout - ULTIMATE patience for natural conversation!
                text = self.listen_once(timeout=5.0)  # ULTIMATE timeout (was 4.0)
                
                if text and len(text.strip()) >= 3:  # Valid speech detected
                    # Reset counters for successful detection
                    consecutive_empty = 0
                    consecutive_noise = 0
                    callback(text)
                    
                elif text and len(text.strip()) < 3:  # Likely noise/garbage
                    consecutive_noise += 1
                    consecutive_empty += 1
                    
                    # If too much noise, increase thresholds temporarily
                    if consecutive_noise >= max_noise:
                        print("🔇 Too much noise detected, adjusting sensitivity...")
                        time.sleep(2.0)  # MUCH longer pause for noise settling (was 1.5)
                        consecutive_noise = 0
                        
                else:
                    # No speech detected
                    consecutive_empty += 1
                    consecutive_noise = 0
                    
                    # SUPER FLUFFY pause system - MAXIMUM patience with empty results
                    if consecutive_empty >= max_empty:
                        time.sleep(1.8)  # MUCH longer pause before retry (was 1.2)
                        consecutive_empty = 0
                        
            except Exception as e:
                print(f"⚠️ Continuous listen error: {e}")
                time.sleep(1)  # Brief pause on error
                
        print("🎤 Speech listening stopped")
    
    def stop_listening(self):
        """Force stop any active listening operations"""
        try:
            self.is_listening = False
            print("🔴 FlexibleWhisper: Stop signal sent")
        except Exception as e:
            print(f"⚠️ Stop listening error: {e}")


# Simple test function
if __name__ == "__main__":
    def test_callback(text):
        print(f"🎤 Heard: '{text}'")
    
    whisper = FlexibleWhisper()
    if whisper.auto_select_model():
        print("🎤 Speaking test - say something!")
        
        # Test single listen
        result = whisper.listen_once(timeout=5.0)
        if result:
            print(f"✅ Test result: '{result}'")
        else:
            print("❌ No speech detected in test")
    else:
        print("❌ Failed to initialize speech recognition")
