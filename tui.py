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

# Note: Virtual environment should already be activated externally

# Import textual for TUI
try:
    from textual.app import App, ComposeResult
    from textual.containers import Vertical, Horizontal, ScrollableContainer
    from textual.widgets import Header, Footer, Static, Button, Label, Log
    from textual import events
except ImportError as e:
    print(f"Error importing textual: {e}")
    print("Please install textual: pip install textual")
    sys.exit(1)

class SDRTUI(App):
    """Enhanced TUI for System Discovery and Researching using Textual"""

    TITLE = "🚀 SDR - System Discovery and Researching TUI"
    CSS = """
    Screen {
        layout: vertical;
    }
    #main {
        height: 100%;
        padding: 1;
    }
    #title {
        text-align: center;
        text-style: bold;
        margin-bottom: 1;
        color: blue;
    }
    #controls {
        height: auto;
        margin-bottom: 1;
    }
    Button {
        margin: 0 1 0 0;
        min-width: 20;
    }
    #status {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 0 1;
        margin-bottom: 1;
    }
    #log-container {
        height: 1fr;
        border: solid $primary;
        padding: 1;
    }
    #log-title {
        text-style: bold;
        margin-bottom: 0.5;
    }
    """

    def __init__(self):
        super().__init__()
        self.server_process = None
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "rag_env"

    def compose(self) -> ComposeResult:
        yield Header()

        with Vertical(id="main"):
            yield Static(self.TITLE, id="title")

            # Controls section
            with Horizontal(id="controls"):
                yield Button("Start Server", id="start", variant="success")
                yield Button("Stop Server", id="stop", variant="error")
                yield Button("Controlli e Impostazioni", id="controls", variant="primary")
                yield Button("Visita Server", id="visit", variant="warning")
                yield Button("Exit", id="exit", variant="default")

            yield Label("Status: Ready", id="status")

            # Log section
            with ScrollableContainer(id="log-container"):
                yield Static("📋 System Log", id="log-title")
                yield Log(id="system_log", auto_scroll=True)

        yield Footer()

    def on_mount(self) -> None:
        self.update_status("Ready")
        self.log("SDR TUI started successfully")
        self.setup_environment()

    def setup_environment(self):
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id

        if button_id == "start":
            self.start_server()
        elif button_id == "stop":
            self.stop_server()
        elif button_id == "controls":
            self.controls_and_settings()
        elif button_id == "visit":
            self.visit_server()
        elif button_id == "exit":
            self.exit()

    def update_status(self, status: str):
        status_label = self.query_one("#status", Label)
        status_label.update(f"Status: {status}")

    def log(self, message: str):
        log_widget = self.query_one("#system_log", Log)
        timestamp = time.strftime("%H:%M:%S")
        log_widget.write_line(f"[{timestamp}] {message}")

    def controls_and_settings(self):
        """Combined controls and settings"""
        self.log("Running system checks and setup...")
        self.setup_environment()
        self.check_system()

    def visit_server(self):
        """Open server in browser"""
        try:
            subprocess.run(["xdg-open", "http://localhost:8080"], check=True)
            self.log("Opening http://localhost:8080 in browser...")
        except Exception as e:
            self.log(f"Could not open browser: {str(e)}. Visit http://localhost:8080 manually")

    def check_system(self):
        """Check system status"""
        self.log("Checking system status...")

        # Check ports
        try:
            result = subprocess.run(["lsof", "-i", ":8080"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Port 8080: In use (Server likely running)")
            else:
                self.log("Port 8080: Free (Server not running)")

            # Check Ollama
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True)
            if result.returncode == 0:
                self.log("Ollama: Running")
            else:
                self.log("Ollama: Not running - Please start with 'ollama serve'")

        except Exception as e:
            self.log(f"Check error: {str(e)}")

    def start_server(self):
        """Start the RAG server"""
        if self.server_process and self.server_process.poll() is None:
            self.log("Server already running")
            return

        # Check if Ollama is running
        try:
            result = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, timeout=5)
            if result.returncode != 0:
                self.log("Ollama is not running. Please start 'ollama serve' first")
                self.update_status("Ollama Required")
                return
        except Exception as e:
            self.log(f"Error checking Ollama: {str(e)}")
            return

        try:
            self.log("Starting server...")
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
            def monitor():
                if self.server_process and self.server_process.stdout:
                    for line in iter(self.server_process.stdout.readline, ''):
                        if line:
                            self.call_from_thread(self.log, line.strip())
                        if self.server_process.poll() is not None:
                            break

            threading.Thread(target=monitor, daemon=True).start()

            self.log("Server started on http://localhost:8080")
            self.update_status("Running")

        except Exception as e:
            self.log(f"Error starting server: {str(e)}")
            self.update_status("Error")

    def stop_server(self):
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

    def on_key(self, event: events.Key) -> None:
        if event.key == "q" or event.key == "ctrl+c":
            self.exit()

if __name__ == "__main__":
    try:
        SDRTUI().run()
    except KeyboardInterrupt:
        print("\nTUI interrupted. Exiting...")
    except Exception as e:
        print(f"Error running TUI: {e}")