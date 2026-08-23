"""Verify player sprite discovery and loading behavior."""
#!/usr/bin/env python3
 # Verify that representative player and UI sprite assets are discoverable.
import os
import sys

# Add the Engine directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Engine'))

print("Testing sprite loading...")

# Test the directory paths
root_dir = os.path.dirname(__file__)
player_resources_dir = os.path.join(root_dir, "Contents", "Resources", "Player")
print(f"Player resources dir: {player_resources_dir}")
print(f"Directory exists: {os.path.isdir(player_resources_dir)}")

# Test idle directory
idle_dir = os.path.join(player_resources_dir, "Idle", "Test - Static")
print(f"Idle dir: {idle_dir}")
print(f"Idle directory exists: {os.path.isdir(idle_dir)}")

if os.path.isdir(idle_dir):
    files = os.listdir(idle_dir)
    print(f"Files in idle dir: {files}")
    
    # Test loading files with 'A' in name
    a_files = [f for f in files if 'A' in f.upper()]
    print(f"Files containing 'A': {a_files}")

print("Test complete")