"""
Main SDR system server - now using modular structure
"""

import sys
import os

# Note: Virtual environment should be activated externally

# Import the modular server (dependencies should be available now)
try:
    from server import SDRServer
except ImportError as e:
    print(f"Error importing server module: {e}")
    print("Please ensure dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

if __name__ == "__main__":
    print("Starting SDR system...")
    # For backward compatibility, just run the server
    server = SDRServer()
    server.run()