#!/usr/bin/env python3

import subprocess
import sys
import os

def main():
    print("=== RAG System Launcher ===")
    print("This will start the RAG system server.")
    
    # Default configuration
    default_host = "0.0.0.0"
    default_port = 5001
    
    # Ask if use defaults
    use_defaults = input(f"Use default configuration? Host: {default_host}, Port: {default_port} (y/n): ").strip().lower()
    if use_defaults == 'y':
        host = default_host
        port = default_port
    else:
        host = input(f"Enter host (default: {default_host}): ").strip() or default_host
        port_input = input(f"Enter port (default: {default_port}): ").strip()
        port = int(port_input) if port_input.isdigit() else default_port
    
    print(f"Configuration: Host={host}, Port={port}")
    confirm = input("Proceed? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Aborted.")
        return
    
    # Activate venv and run
    try:
        # Change to the script directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        # Activate venv
        activate_cmd = ". rag_env/bin/activate && python rag_system.py --host {} --port {}".format(host, port)
        print("Starting server...")
        subprocess.run(activate_cmd, shell=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()