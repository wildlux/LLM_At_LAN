#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

# Ensure we're in the correct environment
project_root = Path(__file__).parent
venv_path = project_root / "rag_env"

# Note: Virtual environment should already be activated by start.sh

# Import urwid for TUI
try:
    import urwid
except ImportError as e:
    print(f"Error importing urwid: {e}")
    print("Please install urwid: pip install urwid")
    sys.exit(1)

class SDRTUI:
    """Enhanced TUI for System Discovery and Researching using Urwid"""

    def __init__(self):
        self.server_process = None
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "rag_env"
        self.log_lines = []
        self.status_text = "Status: Ready"

        # Color palette
        self.palette = [
            ('title', 'white,bold', 'black'),
            ('status', 'white', 'dark blue'),
            ('button', 'black', 'light gray'),
            ('button_focus', 'white', 'dark green'),
            ('log', 'light gray', 'black'),
            ('error', 'light red', 'black'),
            ('success', 'light green', 'black'),
        ]

        # Build UI
        self.title = urwid.Text(("title", "🚀 SDR - System Discovery and Researching TUI"), align='center')
        self.status = urwid.Text(("status", self.status_text), align='center')

        # Buttons with styles
        self.start_button = urwid.AttrMap(urwid.Button("Start Server", on_press=self.start_server), 'button', 'button_focus')
        self.stop_button = urwid.AttrMap(urwid.Button("Stop Server", on_press=self.stop_server), 'button', 'button_focus')
        self.controls_button = urwid.AttrMap(urwid.Button("Controlli e Impostazioni", on_press=self.controls_and_settings), 'button', 'button_focus')
        self.visit_button = urwid.AttrMap(urwid.Button("Visita Server", on_press=self.visit_server), 'button', 'button_focus')
        self.exit_button = urwid.AttrMap(urwid.Button("Exit", on_press=self.exit_app), 'button', 'button_focus')

        # Button grid
        self.button_grid = urwid.GridFlow([
            self.start_button, self.stop_button,
            self.controls_button, self.visit_button,
            self.exit_button
        ], 25, 2, 1, 'center')

        # Log area with header
        self.log_header = urwid.Text(("title", "📋 System Log"), align='center')
        self.log_list = urwid.SimpleFocusListWalker([urwid.Text(("log", "Log initialized..."))])
        self.log_box = urwid.ListBox(self.log_list)

        # Main layout
        self.main_pile = urwid.Pile([
            ('pack', self.title),
            ('pack', urwid.Divider()),
            ('pack', self.button_grid),
            ('pack', urwid.Divider()),
            ('pack', self.status),
            ('pack', urwid.Divider()),
            ('pack', self.log_header),
            ('weight', 1, urwid.AttrMap(self.log_box, 'log'))
        ])

        self.loop = None

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        if isinstance(message, tuple):
            # Handle colored messages
            color, text = message
            log_entry = f"[{timestamp}] {text}"
            self.log_lines.append((color, log_entry))
            # Update log display with colors
            self.log_list[:] = [urwid.AttrMap(urwid.Text(line), color) if isinstance(line, str) else urwid.AttrMap(urwid.Text(line[1]), line[0]) for line in self.log_lines[-20:]]
        else:
            log_entry = f"[{timestamp}] {message}"
            self.log_lines.append(log_entry)
            # Update log display (keep last 20 lines)
            self.log_list[:] = [urwid.Text(line) if isinstance(line, str) else urwid.AttrMap(urwid.Text(line[1]), line[0]) for line in self.log_lines[-20:]]
        if self.loop:
            self.loop.draw_screen()

    def update_status(self, status: str):
        self.status_text = f"Status: {status}"
        self.status.set_text(self.status_text)
        if self.loop:
            self.loop.draw_screen()

    def setup_environment(self, button=None):
        """Setup virtual environment and dependencies"""
        try:
            # Check if virtual environment exists
            if not self.venv_path.exists():
                self.log("Creating virtual environment...")
                result = subprocess.run([sys.executable, "-m", "venv", str(self.venv_path)],
                                      capture_output=True, text=True, cwd=self.project_root)
                if result.returncode != 0:
                    self.log(f"Error creating venv: {result.stderr}")
                    return
                self.log("Virtual environment created")

            # Check and install dependencies
            requirements_path = self.project_root / "requirements.txt"
            if requirements_path.exists():
                self.log("Installing/updating dependencies...")
                pip_cmd = str(self.venv_path / "bin" / "pip")
                result = subprocess.run([pip_cmd, "install", "-q", "-r", str(requirements_path)],
                                      capture_output=True, text=True, cwd=self.project_root)
                if result.returncode != 0:
                    self.log(f"Error installing dependencies: {result.stderr}")
                else:
                    self.log("Dependencies updated")

        except Exception as e:
            self.log(f"Environment setup error: {str(e)}")

    def start_server(self, button=None):
        """Start the RAG server"""
        if self.server_process and self.server_process.poll() is None:
            self.log(("error", "Server already running"))
            return

        # Check if Ollama is running
        try:
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.log(("error", "Ollama is not running. Please start 'ollama serve' first"))
                self.update_status("Ollama Required")
                return
        except Exception as e:
            self.log(("error", f"Error checking Ollama: {str(e)}"))
            return

        try:
            self.log(("success", "Starting server..."))
            self.update_status("Starting")

            server_script = self.project_root / "rag_system.py"
            self.server_process = subprocess.Popen(
                [sys.executable, str(server_script)],
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Monitor output in thread
            def monitor(loop):
                if self.server_process and self.server_process.stdout:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if line:
                            # Schedule log update in main thread
                            loop.set_alarm(0, lambda: self.log(line.strip()))
                        if self.server_process.poll() is not None:
                            break

            threading.Thread(target=monitor, args=(self.loop,), daemon=True).start()

            self.log(("success", "Server started on http://localhost:8080"))
            self.update_status("Running")

        except Exception as e:
            self.log(("error", f"Error starting server: {str(e)}"))
            self.update_status("Error")

    def stop_server(self, button=None):
        """Stop the RAG server"""
        if not self.server_process:
            self.log("No server to stop")
            return

        try:
            self.log("Stopping server...")
            self.update_status("Stopping")

            if self.server_process.poll() is None:
                self.server_process.terminate()
                try:
                    self.server_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.server_process.kill()
                    self.server_process.wait()

            self.server_process = None
            self.log("Server stopped")
            self.update_status("Stopped")

        except Exception as e:
            self.log(f"Error stopping server: {str(e)}")

    def controls_and_settings(self, button=None):
        """Combined controls and settings"""
        self.log(("success", "Running system checks and setup..."))
        self.setup_environment()
        self.check_system()

    def visit_server(self, button=None):
        """Open server in browser"""
        try:
            # Try to open the URL in the default browser
            subprocess.run(["xdg-open", "http://localhost:8080"], check=True)
            self.log(("success", "Opening http://localhost:5001 in browser..."))
        except Exception as e:
            self.log(("error", f"Could not open browser: {str(e)}. Visit http://localhost:5001 manually"))

    def check_system(self, button=None):
        """Check system status"""
        self.log(("success", "Checking system status..."))

        # Check ports
        try:
            result = subprocess.run(["lsof", "-i", ":8080"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(("success", "Port 5001: In use (Server likely running)"))
            else:
                self.log(("error", "Port 5001: Free (Server not running)"))

            # Check Ollama
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True)
            if result.returncode == 0:
                self.log(("success", "Ollama: Running"))
            else:
                self.log(("error", "Ollama: Not running - Please start with 'ollama serve'"))

        except Exception as e:
            self.log(("error", f"Check error: {str(e)}"))

    def exit_app(self, button=None):
        """Exit the application"""
        if self.server_process:
            self.stop_server()
        raise urwid.ExitMainLoop()

    def run(self):
        """Run the TUI"""
        self.log(("success", "SDR TUI started successfully"))
        self.setup_environment()

        # Create the main frame with palette
        self.loop = urwid.MainLoop(self.main_pile, self.palette, unhandled_input=self.handle_input)
        self.loop.run()

    def handle_input(self, key):
        """Handle keyboard input"""
        if key in ('q', 'Q', 'esc'):
            self.exit_app()

if __name__ == "__main__":
    try:
        tui = SDRTUI()
        tui.run()
    except KeyboardInterrupt:
        print("\nTUI interrupted. Exiting...")
    except Exception as e:
        print(f"Error running TUI: {e}")