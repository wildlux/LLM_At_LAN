from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Log
import time
import os

class RAGTUI(App):
    """TUI for RAG System with operations history and server log."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with Vertical(id="left"):
                yield Static("Operations History", id="history_title")
                yield Static(self.get_operations_history(), id="history")
            with Vertical(id="right"):
                yield Static("Server Log", id="log_title")
                yield Log(id="log")
        yield Footer()

    def get_operations_history(self) -> str:
        """Get the list of executed operations."""
        operations = [
            "1. Installed langchain and dependencies",
            "2. Set up virtual environment",
            "3. Fixed start.sh script",
            "4. Updated AVAILABLE_MODELS to match Ollama",
            "5. Added ollama Python package",
            "6. Modified query function to use ollama directly",
            "7. Fixed indentation errors",
            "8. Created LLM folder",
            "9. Added textual for TUI",
            "10. Improved HTML layout with themes",
            "11. Added collapsible sidebar",
            "12. Enhanced CSS styling"
        ]
        return "\n".join(operations)

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.update_log()

    def update_log(self) -> None:
        """Update the log widget with the latest server log."""
        log_widget = self.query_one("#log", Log)
        log_file = "/home/wildlux/Scaricati/files/server.log"
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                lines = f.readlines()
                # Show last 50 lines
                for line in lines[-50:]:
                    log_widget.write_line(line.strip())
        else:
            log_widget.write_line("Log file not found.")

if __name__ == "__main__":
    app = RAGTUI()
    app.run()