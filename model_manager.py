"""
Simple Model Manager - YOUR control over Whisper models!
Add/Delete/Activate models with simple commands
"""

from flexible_whisper import FlexibleWhisper
import os
import shutil

def main():
    print("🎯 Whisper Model Manager - YOUR CONTROL!")
    print("=" * 50)
    
    whisper = FlexibleWhisper()
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Check what models you have")
        print("2. Activate/Switch to a model")
        print("3. Download new model")
        print("4. Delete model from your folder")
        print("5. Clean up system cache")
        print("6. Exit")
        
        choice = input("\nYour choice (1-6): ").strip()
        
        if choice == "1":
            print("\n📁 Checking YOUR models folder...")
            local_models = whisper.check_local_models()
            if local_models:
                print(f"✅ You have {len(local_models)} models:")
                for model in local_models:
                    sizes = {"tiny": "39MB", "base": "74MB", "small": "244MB", "medium": "769MB", "large-v3": "1.5GB"}
                    size = sizes.get(model, "Unknown")
                    # Show which one is currently active
                    if hasattr(whisper, 'selected_model_name') and model in whisper.selected_model_name:
                        print(f"  - {model} (~{size}) ✅ ACTIVE")
                    else:
                        print(f"  - {model} (~{size})")
            else:
                print("📁 No models in your folder yet")
                print("💡 Use option 3 to download models")
                
        elif choice == "2":
            print("\n🔄 ACTIVATE/SWITCH MODEL")
            local_models = whisper.check_local_models()
            if not local_models:
                print("❌ No models available to activate")
                print("💡 Use option 3 to download models first")
                continue
                
            print("Available models to activate:")
            for i, model in enumerate(local_models, 1):
                sizes = {"tiny": "39MB", "base": "74MB", "small": "244MB", "medium": "769MB", "large-v3": "1.5GB"}
                size = sizes.get(model, "Unknown")
                print(f"  {i}. {model} (~{size})")
                
            try:
                model_choice = int(input(f"\nWhich model to activate (1-{len(local_models)}): ")) - 1
                if 0 <= model_choice < len(local_models):
                    selected_model = local_models[model_choice]
                    print(f"\n🚀 Activating {selected_model}...")
                    success = whisper.switch_model(selected_model)
                    if success:
                        print(f"✅ SUCCESS! Now using: {whisper.selected_model_name}")
                    else:
                        print(f"❌ Failed to activate {selected_model}")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a number")
                
        elif choice == "3":
            print("\n📥 DOWNLOAD NEW MODEL")
            print("Available models to download:")
            for i, model in enumerate(whisper.available_model_names, 1):
                sizes = {"tiny": "39MB", "base": "74MB", "small": "244MB", "medium": "769MB", "large-v3": "1.5GB"}
                size = sizes.get(model, "Unknown")
                print(f"  {i}. {model} (~{size})")
                
            try:
                model_choice = int(input(f"\nWhich model to download (1-{len(whisper.available_model_names)}): ")) - 1
                if 0 <= model_choice < len(whisper.available_model_names):
                    model_name = whisper.available_model_names[model_choice]
                    print(f"\n📥 Downloading {model_name}...")
                    success = whisper.download_model(model_name)
                    if success:
                        print(f"✅ Downloaded {model_name} successfully!")
                    else:
                        print(f"❌ Failed to download {model_name}")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a number")
                
        elif choice == "4":
            print("\n�️ DELETE MODEL")
            local_models = whisper.check_local_models()
            if not local_models:
                print("❌ No models to delete")
                continue
                
            print("Models you can delete:")
            for i, model in enumerate(local_models, 1):
                sizes = {"tiny": "39MB", "base": "74MB", "small": "244MB", "medium": "769MB", "large-v3": "1.5GB"}
                size = sizes.get(model, "Unknown")
                print(f"  {i}. {model} (~{size})")
                
            try:
                model_choice = int(input(f"\nWhich model to DELETE (1-{len(local_models)}): ")) - 1
                if 0 <= model_choice < len(local_models):
                    model_to_delete = local_models[model_choice]
                    
                    # Double confirmation for deletion
                    confirm = input(f"⚠️  Are you SURE you want to delete '{model_to_delete}'? (yes/no): ").lower()
                    if confirm == "yes":
                        model_path = os.path.join(whisper.models_dir, f"models--Systran--faster-whisper-{model_to_delete}")
                        if os.path.exists(model_path):
                            try:
                                shutil.rmtree(model_path)
                                print(f"✅ Deleted {model_to_delete} successfully!")
                            except Exception as e:
                                print(f"❌ Error deleting model: {e}")
                        else:
                            print(f"❌ Model path not found: {model_path}")
                    else:
                        print("❌ Deletion cancelled")
                else:
                    print("❌ Invalid choice")
            except ValueError:
                print("❌ Please enter a number")
                
        elif choice == "6":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Please choose 1-6")

if __name__ == "__main__":
    main()
