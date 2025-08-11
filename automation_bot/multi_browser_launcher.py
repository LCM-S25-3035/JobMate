#!/usr/bin/env python3
"""
Multi-Browser Launcher
Launch multiple automation bots side by side for comparison or parallel processing.
"""

import json
import os
import subprocess
import time
import sys

def update_config_for_position(position, config_file="config.json"):
    """Update config.json to set browser position"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), config_file)
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update window positioning
        if 'window_positioning' not in config:
            config['window_positioning'] = {}
        
        config['window_positioning']['enabled'] = True
        config['window_positioning']['position'] = position
        config['window_positioning']['width_percentage'] = 50
        
        # Save updated config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"✅ Updated config for {position} position")
        return True
        
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False

def launch_browser(position, profile_suffix=""):
    """Launch a browser in specified position"""
    try:
        # Create a copy of config for this instance
        original_config = "config.json"
        temp_config = f"config_{position}{profile_suffix}.json"
        
        # Copy and modify config
        with open(original_config, 'r') as f:
            config = json.load(f)
        
        # Update positioning
        config['window_positioning'] = {
            "enabled": True,
            "position": position,
            "width_percentage": 50
        }
        
        # Update profile path to avoid conflicts
        if profile_suffix:
            original_profile = config.get('profile_path', 'C:/temp/JobMateAutoApplyChrome')
            config['profile_path'] = f"{original_profile}{profile_suffix}"
        
        # Save temp config
        with open(temp_config, 'w') as f:
            json.dump(config, f, indent=4)
        
        print(f"🚀 Launching {position} browser...")
        
        # Launch bot with temp config
        cmd = [sys.executable, "runner.py", "--config", temp_config]
        process = subprocess.Popen(cmd, cwd=os.path.dirname(__file__))
        
        return process, temp_config
        
    except Exception as e:
        print(f"❌ Error launching {position} browser: {e}")
        return None, None

def main():
    print("🔥 Multi-Browser Launcher for JobMate Automation")
    print("=" * 50)
    
    print("Options:")
    print("1. Launch Left + Right browsers")
    print("2. Launch Left browser only")
    print("3. Launch Right browser only")
    print("4. Manual positioning setup")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        print("\n🚀 Launching browsers side by side...")
        
        # Launch left browser
        left_process, left_config = launch_browser("left", "_left")
        time.sleep(3)  # Wait a bit before launching second
        
        # Launch right browser
        right_process, right_config = launch_browser("right", "_right")
        
        if left_process and right_process:
            print("\n✅ Both browsers launched!")
            print("💡 Tip: You can now see both automations running side by side")
            
            input("\nPress Enter to stop both browsers...")
            
            # Clean up
            try:
                left_process.terminate()
                right_process.terminate()
                
                # Remove temp configs
                if os.path.exists(left_config):
                    os.remove(left_config)
                if os.path.exists(right_config):
                    os.remove(right_config)
                    
                print("🧹 Cleaned up temporary files")
            except:
                pass
        
    elif choice == "2":
        print("\n🚀 Launching left browser...")
        update_config_for_position("left")
        subprocess.run([sys.executable, "runner.py"])
        
    elif choice == "3":
        print("\n🚀 Launching right browser...")
        update_config_for_position("right")
        subprocess.run([sys.executable, "runner.py"])
        
    elif choice == "4":
        print("\n⚙️ Manual positioning setup:")
        
        position = input("Position (left/right): ").strip().lower()
        if position not in ['left', 'right']:
            position = 'left'
            
        try:
            width = int(input("Width percentage (default 50): ").strip() or "50")
        except:
            width = 50
            
        # Update config
        try:
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            config['window_positioning'] = {
                "enabled": True,
                "position": position,
                "width_percentage": width
            }
            
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"✅ Configured for {position} position with {width}% width")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
    elif choice == "5":
        print("👋 Goodbye!")
        
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
