# 🎯 RDC Visual Speech-to-Text System v2.0

## 🚀 Advanced AI-Powered Speech Recognition with Direct Window Output

A sophisticated **dual-mode visual speech-to-text system** that combines **CUDA-accelerated Whisper models**, **AI vision capabilities**, and **intelligent window targeting** for seamless productivity workflows.

---

## ✨ Key Features

### 🎤 **Advanced Speech Recognition**
- **CUDA-Accelerated Processing** using `faster-whisper` models
- **Multiple Model Support**: tiny, base, small, medium, large-v3
- **Real-time Speech-to-Text** with ultra-responsive feedback (0.1s buffer)
- **English-Only Mode** for filtered transcription
- **Keyword Activation** with customizable trigger phrases
- **Silence Detection** with configurable timing (2-10 seconds)
- **Auto-Silence Separation** with visual countdown (15s timer)
- **Auto-Cleanup** to prevent text accumulation sluggishness

### 🎯 **Intelligent Window Targeting**
- **Direct Output Delivery** to any Windows application
- **Window Selection** with real-time refresh capabilities  
- **Auto-Press Enter** for seamless message sending
- **Visual Context Integration** for enhanced AI responses
- **Connection Testing** to verify target window setup
- **Multi-Monitor Support** with screen selection

### 🤖 **AI Vision Integration**
- **Dual Vision Modes**: Text Analysis & Image Processing
- **Ollama AI Integration** for intelligent responses
- **Screenshot System** with rotation and multi-screen capture
- **Resolution Control**: 4K Original or 1080p Reduced
- **Visual Log System** for AI interaction history
- **Model Chat Interface** for dedicated AI conversations

### 💻 **Modern UI/UX**
- **Split-Pane Interface**: System Screen + Input Screen
- **Real-time Status Indicators** with visual feedback
- **Customizable Themes** and enhanced button styles
- **Keyboard Shortcuts** (Ctrl+Enter to send, Ctrl+L to focus)
- **Context Menus** with right-click functionality
- **Responsive Layout** with resizable panels

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+** with pip
- **Windows 10/11** (uses Win32 APIs)
- **CUDA-compatible GPU** (optional, for acceleration)
- **Ollama** installed and running on `localhost:11434`

### Quick Start
```bash
# Clone the repository
git clone https://github.com/SeriogaRDC/RDC_Visiual_STT_01---A.git
cd RDC_Visiual_STT_01---A

# Option 1: Use the portable launcher (Recommended)
run_portable.bat

# Option 2: Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python ollama_interface_fixed.py
```

### Model Setup
The system automatically manages Whisper models in the local `models/` folder:

1. **Automatic Detection**: Scans for existing models on startup
2. **Model Manager**: Use `python model_manager.py` for model management
3. **Simple Switching**: Toggle between small/medium models via UI
4. **Local Storage**: All models stored in your project folder

---

## 🎮 Usage Guide

### 1. **Basic Speech Recognition**
- Click **🎤 TTS** to start/stop listening
- Speak naturally - text appears instantly in the Input Screen
- Use **🤫 Silence Activation** for hands-free operation
- **Keyword triggers** like "I'm done talking" for smart activation

### 2. **Window Targeting Workflow**
1. Click **🔄** to refresh available windows
2. Select your target application (ChatGPT, Discord, etc.)
3. Enable **Direct Output: ON**
4. Optional: Enable **⚡ Auto-Press Enter**
5. Click **🔗 Test Connection** to verify setup
6. Speak or type - content goes directly to target window!

### 3. **AI Vision Integration**
1. Select **Vision Mode**: Text or Image
2. Choose screen/resolution in dropdown
3. AI analyzes visual content automatically
4. Responses consider both speech and visual context

### 4. **Advanced Features**
- **🇺🇸 English Only**: Filter out non-English speech
- **🤫 Auto-Silence**: 15s pause = automatic text separation  
- **🧹 Auto-Clean**: Prevent sluggishness from long text
- **📋 Copy All**: Copy entire input text
- **💬 Talk to Model**: Dedicated AI chat interface

---

## 📁 Project Structure

```
RDC_Visiual_STT_01---A/
├── 📄 ollama_interface_fixed.py    # Main application GUI
├── 🎤 flexible_whisper.py          # CUDA speech recognition
├── 🖼️ visual_log_window.py         # Vision log interface  
├── 📸 screenshot_gui.py             # Screenshot utilities
├── 🤖 model_manager.py              # Whisper model management
├── ⚙️ requirements.txt              # Python dependencies
├── 🚀 run_portable.bat              # Portable launcher
├── 📂 models/                       # Local Whisper models
├── 📂 screenshots/                  # Captured screenshots
├── 💾 chat_memory.json              # Conversation history
├── 💾 input_memory.json             # Input text history
├── 💾 vision_log.json               # AI vision logs
└── 📂 __pycache__/                  # Python cache
```

---

## 🔧 Configuration

### Speech Settings
```python
# Whisper Models (auto-detected from models/ folder)
- tiny: ~39 MB (fastest)
- small: ~244 MB (recommended)  
- medium: ~769 MB (better accuracy)
- large-v3: ~1550 MB (best quality)

# Activation Methods
- Manual: Click 🎤 TTS button
- Keyword: "I'm done talking" (customizable)
- Silence: 2-10 second pause detection
- Auto-Silence: 15 second separation timer
```

### Window Targeting
```python
# Target any Windows application:
- Web browsers (Chrome, Firefox, Edge)
- Chat applications (Discord, Slack, Teams)
- AI interfaces (ChatGPT, Claude)
- Text editors (Notepad, VSCode)
- Any window that accepts text input
```

### AI Vision Modes
```python
# Vision Text: Analyze screen content as text
# Vision Image: Process screenshots with AI
# Resolution: Original (4K) or Reduced (1080p)
# Multi-screen: Individual screen selection
```

---

## 🎯 Use Cases

### **Content Creation**
- **Blogging**: Speak your ideas, AI enhances with visual context
- **Documentation**: Describe screenshots while AI analyzes them
- **Social Media**: Quick posts with intelligent formatting

### **Development Workflow**  
- **Code Review**: Describe code issues while AI sees the screen
- **Bug Reports**: Voice description + automatic screenshot capture
- **Pair Programming**: Voice notes with visual code context

### **Communication**
- **Meeting Notes**: Real-time transcription with screen analysis
- **Customer Support**: Voice responses with visual problem context
- **Training Materials**: Spoken explanations with screenshot integration

### **Accessibility**
- **Voice Control**: Hands-free operation with silence detection
- **Visual Assistance**: AI describes screen content via speech
- **Multi-Modal**: Combined speech, vision, and text interaction

---

## 🔌 Integrations

### **AI Platforms**
- **Ollama**: Local AI models (llama2, mistral, codellama)
- **Vision Models**: Multi-modal AI with image understanding
- **Custom Models**: Support for specialized AI models

### **Windows APIs**
- **Win32GUI**: Window detection and manipulation
- **PyAutoGUI**: Screen capture and interaction
- **MSS**: High-performance multi-screen capture
- **Clipboard**: Automatic text copying and pasting

### **Speech Technologies**
- **Faster-Whisper**: CUDA-accelerated transcription
- **SpeechRecognition**: Fallback to Google Speech API
- **PyAudio**: Real-time audio capture and processing

---

## 🐛 Troubleshooting

### Common Issues

**Speech Recognition Not Working**
```bash
# Check if models exist
python model_manager.py

# Test CUDA availability  
python -c "import torch; print(torch.cuda.is_available())"

# Verify microphone permissions in Windows Settings
```

**Window Targeting Failed**
```bash
# Refresh window list
Click 🔄 button in the interface

# Test connection
Click 🔗 Test Connection button

# Check if target window accepts input
Try manual typing in the target application
```

**AI Vision Issues**
```bash
# Check Ollama service
http://localhost:11434

# Restart Ollama service
ollama serve

# Verify model availability
ollama list
```

### Performance Optimization
- **Use smaller Whisper models** for faster response (tiny/small)
- **Enable CUDA acceleration** for better performance
- **Close unnecessary applications** to free memory
- **Use 1080p resolution** for faster image processing

---

## 🔄 Updates & Roadmap

### Recent Updates (v2.0)
- ✅ **Dual-pane interface** with split screen design
- ✅ **Auto-silence detection** with visual countdown
- ✅ **English-only mode** for filtered transcription  
- ✅ **Auto-cleanup system** to prevent sluggishness
- ✅ **Enhanced window targeting** with connection testing
- ✅ **Model switching interface** with simple toggle
- ✅ **Visual feedback system** for all operations

### Planned Features
- 🔜 **Browser automation** integration
- 🔜 **Custom keyword training** system
- 🔜 **Plugin architecture** for extensions
- 🔜 **Cloud model support** (OpenAI, Anthropic)
- 🔜 **Mobile companion app** for remote control
- 🔜 **Advanced noise filtering** for better accuracy

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper testing
4. **Commit changes**: `git commit -m 'Add amazing feature'`
5. **Push to branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request** with detailed description

### Development Guidelines
- Follow **PEP 8** Python style guide
- Add **docstrings** for new functions
- Include **error handling** for robust operation
- Test on **multiple Windows versions**
- Update **README** for new features

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - State-of-the-art speech recognition
- **Faster-Whisper** - CUDA acceleration implementation  
- **Ollama** - Local AI model hosting
- **Python Community** - Amazing libraries and tools
- **Windows API** - System integration capabilities

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/SeriogaRDC/RDC_Visiual_STT_01---A/issues)
- **Discussions**: [GitHub Discussions](https://github.com/SeriogaRDC/RDC_Visiual_STT_01---A/discussions)  
- **Email**: [Your Contact Email]
- **Documentation**: [Wiki Pages](https://github.com/SeriogaRDC/RDC_Visiual_STT_01---A/wiki)

---

**Made with ❤️ by SeriogaRDC | Powered by AI and Windows Innovation**