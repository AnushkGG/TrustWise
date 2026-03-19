"""
TrustWise Setup Script

This script helps you set up TrustWise quickly by:
1. Creating necessary directories
2. Checking Python version
3. Installing dependencies
4. Setting up environment file
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    dirs = [
        Path("data/raw"),
        Path("data/plans"),
        Path("config")
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {dir_path}")

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing dependencies...")
    print("   This may take a few minutes...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("   ✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("   ❌ Failed to install dependencies")
        return False

def setup_env_file():
    """Setup .env file from .env.example"""
    print("\n⚙️  Setting up environment file...")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if env_file.exists():
        print("   ℹ️  .env file already exists")
        response = input("   Overwrite? (y/N): ").strip().lower()
        if response != 'y':
            print("   Skipped")
            return
    
    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_file)
        print("   ✓ .env file created")
        print("\n   ⚠️  IMPORTANT: Edit .env and add your OpenAI API key")
    else:
        print("   ❌ .env.example not found")

def main():
    print("=" * 60)
    print("TrustWise Setup")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    print("\n" + "=" * 60)
    response = input("Install Python dependencies? (Y/n): ").strip().lower()
    if response != 'n':
        if not install_dependencies():
            print("\n⚠️  Some dependencies failed to install")
            print("   You can install them manually with: pip install -r requirements.txt")
    
    # Setup .env
    setup_env_file()
    
    # Final instructions
    print("\n" + "=" * 60)
    print("✅ Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Edit .env and add your OpenAI API key")
    print("2. Run the system: python main.py")
    print("\nFor mock testing without API key, just run: python main.py")
    print()

if __name__ == "__main__":
    main()
