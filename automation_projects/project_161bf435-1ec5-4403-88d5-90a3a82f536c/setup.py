#!/usr/bin/env python3
"""
Setup script for Automation Project
Workflow ID: 161bf435-1ec5-4403-88d5-90a3a82f536c
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is supported."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    else:
        print(f"✅ Python {sys.version} detected")

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_directories():
    """Create necessary directories."""
    directories = ["logs", "screenshots", "results"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")

def run_tests():
    """Run test suite."""
    print("🧪 Running tests...")
    try:
        subprocess.check_call([sys.executable, "-m", "pytest", "tests/", "-v"])
        print("✅ All tests passed")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Some tests failed: {e}")

def run_automation():
    """Run the main automation script."""
    print("🚀 Starting automation...")
    try:
        subprocess.check_call([sys.executable, "src/main_automation.py"])
        print("✅ Automation completed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Automation failed: {e}")

def main():
    """Main setup function."""
    print("🔧 Automation Project Setup")
    print("=" * 50)
    print(f"Workflow ID: 161bf435-1ec5-4403-88d5-90a3a82f536c")
    print()
    
    check_python_version()
    install_dependencies()
    setup_directories()
    
    # Ask user what to do next
    print("\n🎯 Setup completed! What would you like to do?")
    print("1. Run tests")
    print("2. Run automation")
    print("3. Both")
    print("4. Exit")
    
    choice = input("Enter your choice (1-4): ").strip()
    
    if choice == "1":
        run_tests()
    elif choice == "2":
        run_automation()
    elif choice == "3":
        run_tests()
        run_automation()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main()
