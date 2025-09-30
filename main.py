#!/usr/bin/env python3

"""
Main entry point for SDR System
"""

import os
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent
    venv_path = project_root / "rag_env"

    # Ensure we're in the correct environment
    if venv_path.exists() and venv_path.is_dir():
        venv_python = venv_path / "bin" / "python"
        if venv_python.exists():
            # Re-execute with virtual environment
            os.execv(str(venv_python), [str(venv_python)] + sys.argv)

    # Run the TUI
    try:
        from tui import SDRTUI
        tui = SDRTUI()
        tui.run()
    except KeyboardInterrupt:
        print("\nExiting SDR System...")
    except Exception as e:
        print(f"Error running SDR System: {e}")

if __name__ == "__main__":
    main()