# Configuration and Constants for Visual Interpretation System
"""
All configuration settings, constants, and default values for the system.
Keep all magic numbers and settings in one place for easy maintenance.
"""

# ===== SYSTEM CONFIGURATION =====
SYSTEM_VERSION = "v2.0 - Modular Architecture"
WINDOW_TITLE = "Visual Interpretation System v2.0 - Modular"
OLLAMA_BASE_URL = "http://localhost:11434"
VISION_MODEL_NAME = "llava"
WHISPER_MODEL_NAME = "medium"
REQUEST_TIMEOUT = 60

# ===== FILE PATHS =====
SCREENSHOTS_DIR = "screenshots"
MODELS_DIR = "models"

# Memory files
SYSTEM_MEMORY_FILE = "system_memory.json"
CHAT_MEMORY_FILE = "chat_memory.json"
VISION_MEMORY_FILE = "vision_memory.json"

# ===== SPEECH SYSTEM SETTINGS =====
SPEECH_AVAILABLE = True  # Will be updated based on imports

# Whisper artifact filters - common hallucinations to ignore
WHISPER_ARTIFACTS = [
    "you", "uu", "uuu", "uh", "uhh", "um", "umm", "mm", "mmm", 
    "hmm", "hm", "eh", "ah", "oh",
    "thank you", "thanks", "thank you for watching", "thanks for watching"
]

# Default trigger keywords for speech activation
DEFAULT_TRIGGER_KEYWORDS = [
    "send it", "send", "I'm done", "done", "go", 
    "submit", "fire", "execute", "deliver"
]

# Speech timing settings
SPEECH_BUFFER_DURATION = 1.0  # seconds
DEFAULT_SILENCE_DURATION = "3s"
MAX_TEXT_LENGTH = 1000  # Character limit for crash protection

# ===== VISION SYSTEM SETTINGS =====
MAX_SCREENSHOTS = 3  # Rotation limit
DEFAULT_ROTATION_INTERVAL = 5  # seconds
SCREENSHOT_TIMEOUT = 30  # seconds for AI processing

# ===== MEMORY LIMITS =====
MAX_SYSTEM_MEMORY_ENTRIES = 1000
MAX_CHAT_MEMORY_ENTRIES = 500

# ===== GUI SETTINGS =====
WINDOW_GEOMETRY = "1000x800"
VISUAL_LOG_GEOMETRY = "800x1200"

# Modern UI configuration
APP_COLORS = {
    "background": "#f8f9fa",
    "text": "#2c3e50", 
    "button": "#007bff",
    "button_hover": "#0056b3",
    "success": "#28a745",
    "error": "#dc3545",
    "warning": "#ffc107",
    "info": "#17a2b8"
}

UI_FONTS = {
    "default": ("Segoe UI", 9),
    "button": ("Segoe UI", 9, "bold"),
    "label": ("Segoe UI", 9),
    "input": ("Consolas", 10),
    "output": ("Consolas", 9)
}

BUTTON_PADDING = (10, 5)

TEXT_AREAS = {
    "input_height": 4,
    "output_height": 12
}

# Audio configuration  
AUDIO_CHUNK = 1024
AUDIO_FORMAT = 8  # pyaudio.paInt16 equivalent
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
RECORDING_SILENCE_THRESHOLD = 500
RECORDING_SILENCE_DURATION = 3.0

# Vision system message
VISION_SYSTEM_MESSAGE = """
Analyze this screenshot and provide a comprehensive description of what you see. 
Include:
- Main content/application visible
- Any text that appears on screen
- UI elements, buttons, or interactive components
- Overall context and purpose of what's displayed
- Any notable details that would help someone understand the current state

Be thorough but concise in your analysis.
"""

# ===== SYSTEM MESSAGES =====
STARTUP_MESSAGES = [
    "🎯 Visual Interpretation System v2.0 - MODULAR ARCHITECTURE!",
    "",
    "🔥 NEW MODULAR SYSTEM:",
    "🏗️ Clean Architecture: Each module has one focused job",
    "🛡️ System Memory: Debug/technical logs (system_memory.json)",
    "💬 Chat Memory: Your conversations & voice (chat_memory.json)", 
    "👁️ Vision Memory: Screenshot analysis (vision_memory.json)",
    "📝 Speech & Vision systems work seamlessly together!",
    "",
    "✨ Core Features:",
    "📥 Window Selection: Choose any open window as output target",
    "📤 Unified Message Delivery: Complete payload with visual data",
    "🖼️ Full Visual Interpretation: Comprehensive screenshot analysis",
    "⚡ Burst Delivery: Instant paste with no typing delays",
    "🚀 Auto-Press Enter: Automatically sends messages after delivery!",
    "🎯 KEYWORD ACTIVATION: Say trigger words to auto-send!",
    "⬆️⬇️ Message History: Use Up/Down arrows to navigate previous messages",
    "",
    "🎤 SPEECH-TO-TEXT WITH DUAL ACTIVATION MODES:",
    "1. Click 🎤 TTS to start listening",
    "2. Talk naturally - watch text accumulate in real-time",
    "3A. KEYWORD MODE - Say trigger words to auto-send:",
    "    • 'send it' • 'send' • 'I'm done' • 'done'",
    "    • 'go' • 'submit' • 'fire' • 'execute' • 'deliver'",
    "3B. SILENCE MODE - Just pause for 2-5 seconds:",
    "    • Choose duration: 2s/3s/4s/5s",
    "    • Stop talking → auto-send after pause",
    "    • Perfect for natural conversation flow",
    "4. Message automatically sends - continue talking for next message!",
    "5. Mix and match: Use keywords for precision, silence for flow",
    "",
    "🔧 How to Use Unified Delivery:",
    "1. Click 🔄 to refresh available windows",
    "2. Select target window from dropdown",
    "3. Enable 'Include Visual Context' for complete payloads",
    "4. Click 'Direct Output: OFF' to enable targeting",
    "5. Enable '⚡ Auto-Press Enter' for automatic message sending",
    "6. Enable '🎯 Keyword Activation' for hands-free operation",
    "7. Messages now include full visual context + metadata!",
    "   📌 Delivered via instant clipboard paste (Ctrl+V)",
    "   🚀 Plus automatic Enter press when enabled!",
    "",
    "⌨️ Message Entry:",
    "• Type your message and press Enter to send",
    "• Use ⬆️⬇️ arrow keys to navigate message history",
    "• Compatible with speech-to-text software",
    "",
    "📸 Screenshot System:",
    "• Select interval (3s/5s/10s) and click 'Start Rotation'",
    "• AI will continuously interpret your screen",
    "• Everything logged to vision_memory.json",
    "",
    "🎬 ULTIMATE HANDS-FREE EXPERIENCE:",
    "• Start speech listening + screenshot rotation",
    "• Talk naturally while AI watches your screen",
    "• Say 'send it' to deliver messages instantly",
    "• Perfect for gaming, movies, or multitasking!",
    ""
]

# ===== ERROR MESSAGES =====
ERROR_MESSAGES = {
    "ollama_not_connected": "Not connected to Ollama. Please check connection.",
    "no_model_selected": "No model selected. Please select a model first.",
    "speech_not_available": "❌ Speech system not available - check flexible_whisper.py",
    "screenshot_failed": "Screenshot capture failed",
    "file_not_found": "File not found or cannot be read",
    "memory_save_failed": "Failed to save to memory system"
}
