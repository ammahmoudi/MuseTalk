#!/usr/bin/env python3
"""
MuseTalk Dependencies Installation Script

This script installs all required dependencies for MuseTalk using uv pip install,
including both the main requirements and API requirements.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Error: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"❌ {description} - FAILED: Command not found")
        return False

def check_uv():
    """Check if uv is installed"""
    try:
        result = subprocess.run(["uv", "--version"], capture_output=True, text=True, check=True)
        print(f"✅ UV found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ UV not found. Please install UV first:")
        print("   curl -LsSf https://astral.sh/uv/install.sh | sh")
        return False

def main():
    """Main installation function"""
    print("🚀 MuseTalk Dependencies Installation")
    print("=" * 50)
    
    # Check if uv is available
    if not check_uv():
        sys.exit(1)
    
    # Get project root directory
    project_root = Path(__file__).parent
    os.chdir(project_root)
    print(f"📁 Working directory: {project_root}")
    
    # Check if requirements files exist
    main_req = project_root / "requirements.txt"
    api_req = project_root / "api" / "requirements.txt"
    
    if not main_req.exists():
        print(f"❌ Main requirements file not found: {main_req}")
        sys.exit(1)
    
    if not api_req.exists():
        print(f"❌ API requirements file not found: {api_req}")
        sys.exit(1)
    
    print(f"📋 Found requirements files:")
    print(f"   • Main: {main_req}")
    print(f"   • API:  {api_req}")
    
    success_count = 0
    total_steps = 4
    
    # Step 1: Install main requirements
    if run_command(
        ["uv", "pip", "install", "-r", str(main_req)],
        "Installing main requirements.txt"
    ):
        success_count += 1
    
    # Step 2: Install API requirements  
    if run_command(
        ["uv", "pip", "install", "-r", str(api_req)],
        "Installing API requirements.txt"
    ):
        success_count += 1
    
    # Step 3: Install current project in editable mode
    if run_command(
        ["uv", "pip", "install", "-e", "."],
        "Installing current project in editable mode"
    ):
        success_count += 1
    
    # Step 4: Install additional dependencies that might be missing
    additional_deps = [
        "aiohttp",  # For streaming tests
        "websockets",  # For WebSocket streaming
        "pytest",  # For testing
        "black",  # For code formatting
    ]
    
    if run_command(
        ["uv", "pip", "install"] + additional_deps,
        "Installing additional development dependencies"
    ):
        success_count += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {success_count}/{total_steps} steps completed")
    
    if success_count == total_steps:
        print("🎉 All dependencies installed successfully!")
        print("\n💡 You can now:")
        print("   • Run the API: python api/musetalk_native_api.py")
        print("   • Test streaming: python test_streaming_api.py")
        print("   • Run realtime inference: python scripts/realtime_inference.py")
        
        # Show installed packages
        print("\n📦 Verifying key packages...")
        key_packages = ["torch", "numpy", "fastapi", "gradio", "transformers"]
        
        for package in key_packages:
            try:
                result = subprocess.run(
                    ["uv", "pip", "show", package], 
                    capture_output=True, text=True, check=True
                )
                # Extract version from pip show output
                for line in result.stdout.split('\n'):
                    if line.startswith('Version:'):
                        version = line.split(':', 1)[1].strip()
                        print(f"   ✅ {package}: {version}")
                        break
            except subprocess.CalledProcessError:
                print(f"   ❌ {package}: Not found")
        
    else:
        print("⚠️ Some installations failed. Please check the error messages above.")
        print("💡 You may need to:")
        print("   • Update uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("   • Check your Python version compatibility")
        print("   • Install system dependencies (ffmpeg, etc.)")
    
    print(f"\n🏁 Installation script completed!")

if __name__ == "__main__":
    main()