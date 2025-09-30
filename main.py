#!/usr/bin/env python3

"""
Main entry point for SDR System
"""

import os
import sys
import logging
from pathlib import Path

def main():
    print("Entering main function...")
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    project_root = Path(__file__).parent
    venv_path = project_root / "rag_env"

    # Ensure we're in the correct environment
    # Temporarily disabled venv check for debugging
    # if venv_path.exists() and venv_path.is_dir():
    #     venv_python = venv_path / "bin" / "python"
    #     if venv_python.exists():
    #         # Re-execute with virtual environment
    #         os.execv(str(venv_python), [str(venv_python)] + sys.argv)

    # Run the unified TUI
    try:
        print("Starting SDR System TUI...")
        from unified_launcher import main as launcher_main
        launcher_main()
        logging.info("SDR System exited successfully")
    except KeyboardInterrupt:
        logging.info("Exiting SDR System...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Error running SDR System: {e}")
        print(f"Error running TUI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()