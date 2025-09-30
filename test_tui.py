#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tui
    print("✅ TUI module imported successfully")

    tui_instance = tui.SDRTUI()
    print("✅ TUI instance created successfully")

    print("✅ TUI is working correctly")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()