#!/usr/bin/env python3
"""
RDC Visual STT System Health Check
Chief Engineer Stability Verification Script
"""

import sys
import os
import traceback

def test_core_imports():
    """Test all core system imports"""
    print("🔍 Testing Core Imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter: OK")
    except ImportError as e:
        print(f"❌ tkinter: FAILED - {e}")
        return False
        
    try:
        import requests
        print("✅ requests: OK")
    except ImportError as e:
        print(f"❌ requests: FAILED - {e}")
        return False
        
    try:
        from PIL import Image
        print("✅ PIL: OK")
    except ImportError as e:
        print(f"❌ PIL: FAILED - {e}")
        return False
        
    try:
        import mss
        print("✅ mss: OK")
    except ImportError as e:
        print(f"❌ mss: FAILED - {e}")
        return False
        
    try:
        import pygetwindow as gw
        print("✅ pygetwindow: OK")
    except ImportError as e:
        print(f"❌ pygetwindow: FAILED - {e}")
        return False
        
    try:
        import pyautogui
        print("✅ pyautogui: OK")
    except ImportError as e:
        print(f"❌ pyautogui: FAILED - {e}")
        return False
        
    try:
        import win32gui
        import win32con
        import win32api
        print("✅ win32 APIs: OK")
    except ImportError as e:
        print(f"❌ win32 APIs: FAILED - {e}")
        return False
        
    try:
        import pyperclip
        print("✅ pyperclip: OK")
    except ImportError as e:
        print(f"❌ pyperclip: FAILED - {e}")
        return False
        
    return True

def test_optional_imports():
    """Test optional system imports"""
    print("\n🔍 Testing Optional Imports...")
    
    try:
        import torch
        print(f"✅ torch: OK (CUDA available: {torch.cuda.is_available()})")
    except ImportError as e:
        print(f"⚠️ torch: Not available - {e}")
        
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper: OK")
    except ImportError as e:
        print(f"⚠️ faster-whisper: Not available - {e}")
        
    try:
        import speech_recognition as sr
        print("✅ speech_recognition: OK")
    except ImportError as e:
        print(f"⚠️ speech_recognition: Not available - {e}")

def test_file_structure():
    """Test project file structure"""
    print("\n🔍 Testing File Structure...")
    
    required_files = [
        "ollama_interface_fixed.py",
        "flexible_whisper.py",
        "visual_log_window.py",
        "model_manager.py",
        "requirements.txt",
        "run_portable.bat",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: OK")
        else:
            print(f"❌ {file}: MISSING")
            missing_files.append(file)
    
    required_dirs = ["screenshots", "models"]
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✅ {dir_name}/: OK")
        else:
            print(f"⚠️ {dir_name}/: Missing (will be created)")
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ {dir_name}/: Created")
    
    return len(missing_files) == 0

def test_main_module():
    """Test that main module can be imported"""
    print("\n🔍 Testing Main Module Import...")
    
    try:
        # Try to import the main interface
        sys.path.insert(0, os.getcwd())
        
        # First test basic import without running
        import ollama_interface_fixed
        print("✅ ollama_interface_fixed: Import OK")
        
        # Test flexible whisper
        import flexible_whisper
        print("✅ flexible_whisper: Import OK")
        
        # Test visual log window
        import visual_log_window
        print("✅ visual_log_window: Import OK")
        
        return True
        
    except Exception as e:
        print(f"❌ Module import failed: {e}")
        traceback.print_exc()
        return False

def test_system_capabilities():
    """Test system capabilities"""
    print("\n🔍 Testing System Capabilities...")
    
    try:
        # Test screen detection
        import mss
        with mss.mss() as sct:
            monitors = sct.monitors
            print(f"✅ Screen detection: {len(monitors)} monitors found")
    except Exception as e:
        print(f"❌ Screen detection failed: {e}")
        
    try:
        # Test window enumeration
        import pygetwindow as gw
        windows = gw.getAllWindows()
        visible_windows = [w for w in windows if w.visible and w.title.strip()]
        print(f"✅ Window detection: {len(visible_windows)} windows found")
    except Exception as e:
        print(f"❌ Window detection failed: {e}")
        
    try:
        # Test clipboard
        import pyperclip
        test_text = "Health check test"
        pyperclip.copy(test_text)
        retrieved = pyperclip.paste()
        if retrieved == test_text:
            print("✅ Clipboard: OK")
        else:
            print("⚠️ Clipboard: Partial functionality")
    except Exception as e:
        print(f"❌ Clipboard failed: {e}")

def main():
    """Run complete health check"""
    print("🚀 RDC Visual STT System Health Check")
    print("=" * 50)
    print(f"Python Version: {sys.version}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 50)
    
    # Run all tests
    core_ok = test_core_imports()
    test_optional_imports()
    files_ok = test_file_structure()
    modules_ok = test_main_module()
    test_system_capabilities()
    
    print("\n" + "=" * 50)
    print("📋 HEALTH CHECK SUMMARY:")
    print("=" * 50)
    
    if core_ok and files_ok and modules_ok:
        print("✅ SYSTEM STATUS: HEALTHY")
        print("🎯 All critical components working")
        print("🚀 Ready for production use!")
        return 0
    else:
        print("❌ SYSTEM STATUS: NEEDS ATTENTION")
        if not core_ok:
            print("🔧 Fix: Install missing dependencies")
        if not files_ok:
            print("🔧 Fix: Restore missing files")
        if not modules_ok:
            print("🔧 Fix: Check module syntax errors")
        return 1

if __name__ == "__main__":
    exit_code = main()
    input("\nPress Enter to continue...")
    sys.exit(exit_code)
