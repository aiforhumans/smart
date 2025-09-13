"""
Quick start script for the AI User Learning System
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version_info.major}.{sys.version_info.minor}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize the database"""
    print("🗄️ Initializing database...")
    try:
        from database.init_db import main as init_db_main
        init_db_main()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("🚀 Starting server...")
    try:
        # Import after dependencies are installed
        from app import app
        print("✅ Server starting at http://localhost:5000")
        print("📖 API documentation: http://localhost:5000/health")
        print("🌐 Web interface: http://localhost:5000")
        print("\nPress Ctrl+C to stop the server")
        
        app.run(host='0.0.0.0', port=5000, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def run_demo():
    """Run the demo script"""
    print("🎭 Running demo...")
    try:
        from examples.demo import AILearningDemo
        demo = AILearningDemo()
        demo.run_all_scenarios()
        print("✅ Demo completed successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to run demo: {e}")
        return False

def main():
    """Main setup and start function"""
    print("🧠 AI User Learning System - Quick Start")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print(f"📂 Working directory: {script_dir}")
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Initialize database
    if not initialize_database():
        return
    
    # Ask user what to do
    print("\n🎯 What would you like to do?")
    print("1. Start the web server")
    print("2. Run the demo scenarios")
    print("3. Run interactive demo")
    print("4. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            start_server()
            break
        elif choice == "2":
            run_demo()
            break
        elif choice == "3":
            print("🎮 Starting interactive demo...")
            try:
                from examples.demo import interactive_demo
                interactive_demo()
            except Exception as e:
                print(f"❌ Failed to run interactive demo: {e}")
            break
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()