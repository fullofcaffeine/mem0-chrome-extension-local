#!/usr/bin/env python3
"""
Configure Chrome Extension for Local Mem0 Server
This script modifies the extension files to point to localhost instead of the cloud API.
"""

import os
import re
import json
from pathlib import Path

# Configuration
CLOUD_API_URL = "https://api.mem0.ai"
LOCAL_API_URL = "http://localhost:8000"
CLOUD_APP_URL = "https://app.mem0.ai"
LOCAL_APP_URL = "http://localhost:8000"

def modify_manifest():
    """Update manifest.json to allow localhost permissions"""
    manifest_path = "manifest.json"
    
    try:
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        # Add localhost permissions
        host_permissions = manifest.get("host_permissions", [])
        localhost_permissions = [
            "http://localhost:8000/*",
            "http://127.0.0.1:8000/*"
        ]
        
        for perm in localhost_permissions:
            if perm not in host_permissions:
                host_permissions.append(perm)
        
        manifest["host_permissions"] = host_permissions
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ Updated {manifest_path}")
        return True
    except Exception as e:
        print(f"❌ Error updating {manifest_path}: {e}")
        return False

def modify_file(file_path, description):
    """Modify a JavaScript file to use local API"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace API URLs
        original_content = content
        content = content.replace(CLOUD_API_URL, LOCAL_API_URL)
        content = content.replace(CLOUD_APP_URL, LOCAL_APP_URL)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
            print(f"✅ Updated {file_path}")
            return True
        else:
            print(f"ℹ️  No changes needed in {file_path}")
            return True
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def find_and_modify_js_files():
    """Find and modify all JavaScript files that reference the cloud API"""
    js_files = [
        "sidebar.js",
        "popup.js",
        "background.js",
        "chatgpt/content.js",
        "claude/content.js",
        "perplexity/content.js",
        "grok/content.js",
        "deepseek/content.js",
        "mem0/content.js"
    ]
    
    success_count = 0
    total_count = 0
    
    for file_path in js_files:
        if os.path.exists(file_path):
            total_count += 1
            if modify_file(file_path, f"JavaScript file {file_path}"):
                success_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    return success_count, total_count

def create_local_config():
    """Create a local configuration file for reference"""
    config_content = f"""# Local Mem0 Configuration

## Server URLs
- Local API: {LOCAL_API_URL}
- API Documentation: {LOCAL_API_URL}/docs
- Database: ./local_memories.db

## Usage
1. Start the local server: python local_mem0_server.py
2. Load the extension in Chrome
3. Use ChatGPT, Claude, etc. normally - memories will be stored locally!

## Extension Settings
- No API key required
- Memories stored in local SQLite database
- Search works with simple text matching
"""
    
    with open("LOCAL_SETUP.md", "w") as f:
        f.write(config_content)
    print("✅ Created LOCAL_SETUP.md with configuration details")

def main():
    print("=" * 60)
    print("🔧 Configuring Chrome Extension for Local Mem0")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("manifest.json"):
        print("❌ manifest.json not found. Please run this script from the extension directory.")
        return
    
    print("Modifying extension files...")
    print()
    
    # Update manifest
    if not modify_manifest():
        print("❌ Failed to update manifest.json")
        return
    
    # Update JavaScript files
    success_count, total_count = find_and_modify_js_files()
    
    print()
    print(f"📊 Results: {success_count}/{total_count} files updated successfully")
    
    if success_count == total_count:
        print()
        print("✅ Configuration complete!")
        print()
        print("Next steps:")
        print("1. Start the local server: python local_mem0_server.py")
        print("2. In Chrome, go to chrome://extensions/")
        print("3. Enable 'Developer mode'")
        print("4. Click 'Load unpacked' and select this directory")
        print("5. Use ChatGPT, Claude, etc. - memories will be stored locally!")
        print()
        print("🎉 No API keys needed - everything runs locally!")
    else:
        print()
        print("⚠️  Some files couldn't be updated. Please check the errors above.")
    
    # Create documentation
    create_local_config()
    
    print("=" * 60)

if __name__ == "__main__":
    main() 
