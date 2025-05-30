#!/usr/bin/env python3
"""
Chrome Installation and Driver Compatibility Checker for Windows
"""

import os
import sys
import subprocess
from pathlib import Path

def check_chrome_installation():
    """Check if Chrome is installed on Windows"""
    print("🔍 Checking Chrome installation...")
    
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv("USERNAME", "")),
    ]
    
    for chrome_path in chrome_paths:
        if os.path.exists(chrome_path):
            print(f"✅ Chrome found at: {chrome_path}")
            return chrome_path
    
    print("❌ Chrome not found. Please install Google Chrome.")
    print("📥 Download from: https://www.google.com/chrome/")
    return None

def check_webdriver_manager():
    """Check webdriver-manager installation"""
    print("\n🔍 Checking webdriver-manager...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ webdriver-manager is installed")
        
        # Try to get driver path
        try:
            driver_path = ChromeDriverManager().install()
            print(f"✅ ChromeDriver downloaded/cached at: {driver_path}")
            return True
        except Exception as e:
            print(f"❌ ChromeDriver download failed: {e}")
            return False
            
    except ImportError:
        print("❌ webdriver-manager not installed")
        print("📦 Install with: pip install webdriver-manager")
        return False

def test_selenium():
    """Test basic Selenium functionality"""
    print("\n🔍 Testing Selenium...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Test navigation
        driver.get("data:text/html,<html><body><h1>Test Page</h1></body></html>")
        title = driver.page_source
        driver.quit()
        
        print("✅ Selenium test successful")
        return True
        
    except Exception as e:
        print(f"❌ Selenium test failed: {e}")
        print("\n🔧 Try these fixes:")
        print("1. Update Chrome to latest version")
        print("2. Run: pip install --upgrade selenium webdriver-manager")
        print("3. Restart your terminal/IDE")
        print("4. Try running as administrator")
        return False

def check_dependencies():
    """Check required Python packages"""
    print("\n🔍 Checking Python dependencies...")
    
    required_packages = [
        'selenium',
        'webdriver-manager',
        'fastapi',
        'uvicorn',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    """Main check function"""
    print("🚀 Chrome and Selenium Compatibility Checker")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check Chrome installation
    chrome_path = check_chrome_installation()
    if not chrome_path:
        all_checks_passed = False
    
    # Check dependencies
    if not check_dependencies():
        all_checks_passed = False
    
    # Check webdriver-manager
    if not check_webdriver_manager():
        all_checks_passed = False
    
    # Test Selenium
    if not test_selenium():
        all_checks_passed = False
    
    print("\n" + "=" * 50)
    
    if all_checks_passed:
        print("🎉 All checks passed! Your system is ready for automation.")
        print("✅ You can now run: python main.py")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("📚 For help, see: https://selenium-python.readthedocs.io/")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 