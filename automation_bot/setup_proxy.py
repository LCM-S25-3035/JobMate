#!/usr/bin/env python3
"""
Bright Data Proxy Setup Helper
This script helps you configure your Bright Data proxy settings.
"""

import json
import os

def setup_brightdata_proxy():
    """Interactive setup for Bright Data proxy configuration"""
    
    print("=== Bright Data Proxy Setup ===")
    print("Follow these steps to get your proxy details from Bright Data:")
    print("1. Go to https://brightdata.com/cp/zones/")
    print("2. Select your zone")
    print("3. Go to 'Access parameters' tab")
    print("4. Copy the details below")
    print()
    
    # Get user input
    print("Enter your Bright Data proxy details:")
    host = input("Proxy Host (usually brd.superproxy.io): ").strip() or "brd.superproxy.io"
    port = input("Proxy Port (e.g., 22225): ").strip()
    
    print("\nUsername format should be: brd-customer-YOUR_CUSTOMER_ID-zone-YOUR_ZONE_NAME")
    print("Example: brd-customer-hl_12345678-zone-datacenter_proxy1")
    username = input("Proxy Username: ").strip()
    password = input("Proxy Password: ").strip()
    
    # Validate input
    if not all([host, port, username, password]):
        print("❌ Error: All fields are required!")
        return False
    
    try:
        # Validate port is numeric
        int(port)
    except ValueError:
        print("❌ Error: Port must be a number!")
        return False
    
    # Load current config
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")
        return False
    
    # Update proxy configuration
    config['proxy'] = {
        "enabled": True,
        "host": host,
        "port": port,
        "username": username,
        "password": password
    }
    
    # Save updated config
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        print("\n✅ Proxy configuration saved successfully!")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Username: {username}")
        print(f"Password: {'*' * len(password)}")
        print("\nYour bot will now use Bright Data proxy for reCAPTCHA bypass.")
        print("Set 'enabled': false in config.json to disable proxy.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def disable_proxy():
    """Disable proxy in configuration"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'proxy' in config:
            config['proxy']['enabled'] = False
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print("✅ Proxy disabled successfully!")
        else:
            print("❌ No proxy configuration found.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("Bright Data Proxy Configuration Tool")
    print("1. Setup/Enable Proxy")
    print("2. Disable Proxy")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "1":
        setup_brightdata_proxy()
    elif choice == "2":
        disable_proxy()
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
