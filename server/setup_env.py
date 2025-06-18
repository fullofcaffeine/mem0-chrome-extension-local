#!/usr/bin/env python3
"""
Setup script for local mem0 environment
"""

import os
import sys

def setup_environment():
    """Setup environment variables for local mem0"""
    
    print("🚀 Setting up local Mem0 environment...")
    print()
    
    # Check if OpenAI API key is set
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_key or openai_key == "your-openai-api-key-here":
        print("❌ OpenAI API key not found!")
        print()
        print("To use mem0 locally, you need an OpenAI API key.")
        print("You can get one from: https://platform.openai.com/api-keys")
        print()
        print("To set it up:")
        print("1. Add this line to your ~/.zshrc or ~/.bash_profile:")
        print("   export OPENAI_API_KEY='your-actual-api-key-here'")
        print()
        print("2. Or create a .env file in this directory with:")
        print("   OPENAI_API_KEY=your-actual-api-key-here")
        print()
        
        # Ask if they want to create a .env file
        response = input("Would you like to create a .env file now? (y/n): ").lower().strip()
        
        if response == 'y' or response == 'yes':
            api_key = input("Enter your OpenAI API key: ").strip()
            if api_key:
                try:
                    with open('.env', 'w') as f:
                        f.write(f"OPENAI_API_KEY={api_key}\n")
                    print("✅ .env file created successfully!")
                    print("🔄 Please restart the terminal and run the server again.")
                    return False
                except Exception as e:
                    print(f"❌ Error creating .env file: {e}")
                    return False
            else:
                print("❌ No API key provided.")
                return False
        else:
            print("❌ Setup cancelled. Please set up your OpenAI API key and try again.")
            return False
    else:
        print("✅ OpenAI API key found!")
        return True

def main():
    """Main setup function"""
    print("=" * 60)
    print("🧠 Mem0 Chrome Extension - Local Setup")
    print("=" * 60)
    print()
    
    if setup_environment():
        print()
        print("🎉 Environment setup complete!")
        print()
        print("Next steps:")
        print("1. Start the local mem0 server:")
        print("   python local_mem0_server.py")
        print()
        print("2. Modify the Chrome extension to point to localhost:8000")
        print("3. Load the extension in Chrome")
        print()
        print("The server will be available at: http://localhost:8000")
        print("API documentation: http://localhost:8000/docs")
        print()
    else:
        print()
        print("⚠️  Setup incomplete. Please follow the instructions above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
