#!/usr/bin/env python3
"""
Git Helper for RDC Visual STT Project
Safe, careful, and user-friendly git operations
"""

import os
import sys
import subprocess
import datetime

def run_git_command(command, capture_output=True):
    """Run a git command safely with error handling"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)

def check_git_status():
    """Check current git status"""
    print("🔍 Checking Git Status...")
    
    # Check if we're in a git repo
    success, stdout, stderr = run_git_command("git rev-parse --is-inside-work-tree")
    if not success:
        print("❌ Not in a Git repository")
        return False
    
    # Get current branch
    success, branch, _ = run_git_command("git branch --show-current")
    if success:
        print(f"📍 Current branch: {branch.strip()}")
    
    # Check status
    success, status, _ = run_git_command("git status --porcelain")
    if success:
        if status.strip():
            print("📝 Files with changes:")
            for line in status.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
        else:
            print("✅ No changes to commit")
    
    # Check if we're ahead/behind remote
    success, ahead_behind, _ = run_git_command("git rev-list --left-right --count HEAD...@{upstream}")
    if success and ahead_behind.strip():
        ahead, behind = ahead_behind.strip().split('\t')
        if ahead != '0':
            print(f"⬆️ {ahead} commits ahead of remote")
        if behind != '0':
            print(f"⬇️ {behind} commits behind remote")
        if ahead == '0' and behind == '0':
            print("🔄 Up to date with remote")
    
    return True

def safe_add_and_commit():
    """Safely add and commit changes"""
    print("\n🔄 Safe Add and Commit Process...")
    
    # Show what will be added
    success, status, _ = run_git_command("git status --porcelain")
    if not success or not status.strip():
        print("✅ No changes to commit")
        return True
    
    print("📝 Files that will be added:")
    modified_files = []
    for line in status.strip().split('\n'):
        if line.strip():
            filename = line[3:].strip()
            modified_files.append(filename)
            print(f"   {line}")
    
    # Confirm with user
    print(f"\nReady to add {len(modified_files)} files to git.")
    confirm = input("Continue? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Cancelled by user")
        return False
    
    # Add files
    success, _, stderr = run_git_command("git add .")
    if not success:
        print(f"❌ Failed to add files: {stderr}")
        return False
    print("✅ Files added to staging area")
    
    # Create commit message
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    default_message = f"System stabilization update - {timestamp}"
    print(f"\nDefault commit message: '{default_message}'")
    custom_message = input("Enter custom message (or press Enter for default): ").strip()
    commit_message = custom_message if custom_message else default_message
    
    # Commit
    success, _, stderr = run_git_command(f'git commit -m "{commit_message}"')
    if not success:
        print(f"❌ Failed to commit: {stderr}")
        return False
    print(f"✅ Committed successfully: '{commit_message}'")
    
    return True

def safe_push():
    """Safely push to remote"""
    print("\n🚀 Safe Push Process...")
    
    # Check if there are commits to push
    success, ahead_behind, _ = run_git_command("git rev-list --left-right --count HEAD...@{upstream}")
    if success and ahead_behind.strip():
        ahead, behind = ahead_behind.strip().split('\t')
        if ahead == '0':
            print("✅ Nothing to push - already up to date")
            return True
        print(f"📤 Ready to push {ahead} commits")
    
    # Show what will be pushed
    success, log, _ = run_git_command("git log --oneline @{upstream}..HEAD")
    if success and log.strip():
        print("📋 Commits to be pushed:")
        for line in log.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
    
    # Confirm with user
    confirm = input("\nPush to remote repository? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Push cancelled by user")
        return False
    
    # Push
    success, _, stderr = run_git_command("git push")
    if not success:
        print(f"❌ Push failed: {stderr}")
        return False
    print("✅ Pushed successfully!")
    
    return True

def create_backup_tag():
    """Create a backup tag before major changes"""
    print("\n🏷️ Creating Backup Tag...")
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    tag_name = f"backup_before_changes_{timestamp}"
    
    success, _, stderr = run_git_command(f'git tag {tag_name}')
    if not success:
        print(f"❌ Failed to create tag: {stderr}")
        return False
    print(f"✅ Created backup tag: {tag_name}")
    
    # Push tag to remote
    confirm = input("Push backup tag to remote? (yes/no): ").lower().strip()
    if confirm == 'yes':
        success, _, stderr = run_git_command(f'git push origin {tag_name}')
        if success:
            print("✅ Backup tag pushed to remote")
        else:
            print(f"⚠️ Failed to push tag: {stderr}")
    
    return True

def show_git_help():
    """Show git helper menu"""
    print("\n🎯 RDC Visual STT Git Helper")
    print("=" * 40)
    print("1. Check git status")
    print("2. Safe add and commit")
    print("3. Safe push to remote")
    print("4. Create backup tag")
    print("5. Show recent commits")
    print("6. Show all files in repo")
    print("7. Complete safe workflow (add → commit → push)")
    print("0. Exit")
    print("=" * 40)

def show_recent_commits():
    """Show recent commits"""
    print("\n📋 Recent Commits...")
    success, log, _ = run_git_command("git log --oneline -10")
    if success and log.strip():
        for line in log.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("❌ No commits found")

def show_repo_files():
    """Show all files tracked by git"""
    print("\n📁 Files in Repository...")
    success, files, _ = run_git_command("git ls-files")
    if success and files.strip():
        file_list = files.strip().split('\n')
        print(f"📊 Total files tracked: {len(file_list)}")
        for file in sorted(file_list):
            if file.strip():
                print(f"   {file}")
    else:
        print("❌ No files found")

def complete_workflow():
    """Complete safe workflow: add → commit → push"""
    print("\n🔄 Complete Safe Workflow: Add → Commit → Push")
    print("=" * 50)
    
    # Step 1: Check status
    if not check_git_status():
        return False
    
    # Step 2: Add and commit
    if not safe_add_and_commit():
        return False
    
    # Step 3: Push
    if not safe_push():
        return False
    
    print("\n✅ Complete workflow finished successfully!")
    return True

def main():
    """Main git helper interface"""
    if not os.path.exists('.git'):
        print("❌ Not in a Git repository!")
        print("💡 Initialize with: git init")
        return
    
    while True:
        show_git_help()
        try:
            choice = input("\nChoose an option (0-7): ").strip()
            
            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                check_git_status()
            elif choice == '2':
                safe_add_and_commit()
            elif choice == '3':
                safe_push()
            elif choice == '4':
                create_backup_tag()
            elif choice == '5':
                show_recent_commits()
            elif choice == '6':
                show_repo_files()
            elif choice == '7':
                complete_workflow()
            else:
                print("❌ Invalid choice. Please enter 0-7.")
                
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
