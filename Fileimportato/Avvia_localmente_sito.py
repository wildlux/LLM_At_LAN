#!/usr/bin/env python3
"""
Flask Server Launcher - TUI Interface
Lanciatore con interfaccia testuale per gestire il server Flask
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, ListView, ListItem, Label
from textual.containers import Container, Vertical, Horizontal
from textual import events

class FlaskLauncher(App):
    def __init__(self):
        super().__init__()
        self.server_process = None
        self.project_dir: str = os.getcwd()
        self.venv_path: str = os.path.join(self.project_dir, "rag_env", "bin", "activate")
        self.cache_cleaned: bool = False
        self.current_host = None
        self.current_port = None
        self.current_protocol: str = "http"
        self.status_label = None
        self.log_view = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static("🚀 Flask Server Launcher", id="title"),
            Static("SDR System", id="subtitle"),
            ListView(
                ListItem(Label("1. Avvia/Ferma Server Flask")),
                ListItem(Label("2. Mostra Messaggi Protocolli")),
                ListItem(Label("3. Controlla Status")),
                ListItem(Label("4. Protocolli")),
                ListItem(Label("5. Configurazioni Flask")),
                ListItem(Label("6. Pulizia Cache")),
                ListItem(Label("7. (env) 🐚 Shell")),
                ListItem(Label("8. Apri Pagina Server nel Browser")),
                ListItem(Label("0. Esci")),
                id="menu"
            ),
            Static("", id="status"),
            Static("", id="logs"),
        )
        yield Footer()



    def check_environment(self):
        """Verifica l'ambiente di sviluppo"""
        checks = []

        # Verifica directory progetto
        if os.path.exists(self.project_dir):
            checks.append(("📁 Directory progetto", "✅ OK"))
        else:
            checks.append(("📁 Directory progetto", "❌ Non trovata"))

        # Verifica virtual environment
        if os.path.exists(os.path.join(self.project_dir, "venv")):
            checks.append(("🐍 Virtual Environment", "✅ OK"))
        else:
            checks.append(("🐍 Virtual Environment", "❌ Non trovato"))

        # Verifica server.py
        server_py = os.path.join(self.project_dir, "server.py")
        if os.path.exists(server_py):
            checks.append(("⚙️  server.py", "✅ OK"))
        else:
            checks.append(("⚙️  server.py", "❌ Non trovato"))

        # Mostra controlli
        status_text = "🔍 Controllo Ambiente\n"
        for component, status in checks:
            status_text += f"{component}: {status}\n"

        self.notify(status_text)
        return all("✅" in status for _, status in checks)

    def update_menu(self):
        """Aggiorna il menu con lo stato attuale"""
        menu = self.query_one("#menu", ListView)
        status_widget = self.query_one("#status", Static)

        if self.server_process and self.server_process.poll() is None:
            server_status = f"🟢 Running su {self.current_protocol}://{self.current_host}:{self.current_port}"
        else:
            server_status = "🔴 Stopped"
        cache_status = "🟢 Già pulita!" if self.cache_cleaned else "🔴 Da pulire"

        status_text = f"Server: {server_status} | Cache: {cache_status}"
        status_widget.update(status_text)

    def start_server(self, host: str = "0.0.0.0", port: str = "8080"):
        """Avvia il server Flask"""
        if self.server_process and self.server_process.poll() is None:
            self.notify("Server già in esecuzione!", severity="error")
            return

        try:
            # Cambia directory
            os.chdir(self.project_dir)

            python_exe = os.path.join(self.project_dir, "rag_env", "bin", "python")
            cmd = [python_exe, "server.py", "--host", host, "--port", port]

            self.notify(f"Avvio server su {host}:{port}...")

            # Avvia processo in background
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                preexec_fn=os.setsid
            )

            time.sleep(3)  # Aspetta che il server si avvii

            if self.server_process.poll() is None:
                self.current_host = host
                self.current_port = port
                self.current_protocol = "http"
                self.notify("Server avviato con successo!")
                self.update_menu()

                # Apri browser
                browser_url = f"http://localhost:{port}/"
                webbrowser.open(browser_url)
                self.notify(f"Browser aperto su {browser_url}")
            else:
                stdout, stderr = self.server_process.communicate()
                self.notify("Errore avvio server", severity="error")
                if stderr:
                    self.notify(stderr, severity="error")

        except Exception as e:
            self.notify(f"Errore: {str(e)}", severity="error")

    def stop_server(self):
        """Ferma il server Flask"""
        if not self.server_process or self.server_process.poll() is not None:
            self.notify("Server non è in esecuzione", severity="warning")
            return

        try:
            # Termina il gruppo di processi
            os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
            self.server_process.wait(timeout=5)
            self.notify("Server fermato con successo!")
        except subprocess.TimeoutExpired:
            # Forza terminazione se necessario
            os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
            self.notify("Server forzatamente terminato", severity="warning")
        except Exception as e:
            self.notify(f"Errore fermando server: {str(e)}", severity="error")
        finally:
            self.server_process = None
            self.update_menu()

    def on_key(self, event: events.Key) -> None:
        """Gestisce i tasti premuti"""
        if event.key == "1":
            self.toggle_server()
        elif event.key == "2":
            self.show_logs()
        elif event.key == "3":
            self.show_status()
        elif event.key == "4":
            self.show_logs()
        elif event.key == "5":
            self.flask_setup()
        elif event.key == "6":
            self.cleanup_cache()
        elif event.key == "7":
            self.open_shell()
        elif event.key == "8":
            self.open_server_page()
        elif event.key == "0":
            self.quit_app()

    def toggle_server(self):
        if self.server_process and self.server_process.poll() is None:
            self.stop_server()
        else:
            host = "0.0.0.0"  # Default, could add input later
            port = "8080"
            self.start_server(host, port)

    def show_status(self):
        """Mostra lo status del server"""
        logs_widget = self.query_one("#logs", Static)
        status_text = "📊 Status Server\n"

        if self.server_process:
            if self.server_process.poll() is None:
                status_text += f"Stato: 🟢 In esecuzione\nPID: {self.server_process.pid}\nDirectory: {self.project_dir}"
            else:
                status_text += f"Stato: 🔴 Fermato\nCodice uscita: {self.server_process.returncode}"
        else:
            status_text += "Stato: 🔴 Non avviato"

        logs_widget.update(status_text)

    def show_logs(self):
        """Mostra i log del server"""
        if not self.server_process:
            self.notify("Server non è in esecuzione", severity="warning")
            return

        logs_widget = self.query_one("#logs", Static)
        logs_text = "📋 Log del server\n"

        # Mostra ultime righe
        if self.server_process.stdout:
            lines = []
            while True:
                line = self.server_process.stdout.readline()
                if line:
                    lines.append(line.strip())
                    if len(lines) > 20:
                        lines = lines[-20:]
                else:
                    break
            logs_text += "\n".join(lines)
        else:
            logs_text += "Nessun log disponibile"

        logs_widget.update(logs_text)

    def cleanup_cache(self):
        """Pulisce la cache di Flask"""
        try:
            os.chdir(self.project_dir)

            self.notify("Pulizia cache in corso...")

            # Rimuovi file di cache
            cache_dirs = [
                "__pycache__",
                "*.pyc",
                ".pytest_cache"
            ]

            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    if os.path.isdir(cache_dir):
                        import shutil
                        shutil.rmtree(cache_dir)
                    else:
                        os.remove(cache_dir)

            self.notify("Cache pulita con successo!")
            self.cache_cleaned = True
            self.update_menu()

        except Exception as e:
            self.notify(f"Errore pulizia cache: {str(e)}", severity="error")

    def flask_setup(self):
        """Esegue setup completo di Flask"""
        try:
            os.chdir(self.project_dir)

            logs_widget = self.query_one("#logs", Static)
            logs_widget.update("⚙️ Configurazioni Flask\n1. Installa dipendenze\n2. Controlla configurazione\n3. Test server\n0. Torna al menu")

            # For simplicity, run all steps
            self._install_dependencies()
            self._check_config()
            self._test_server()

        except Exception as e:
            self.notify(f"Errore nelle configurazioni: {str(e)}", severity="error")

    def _install_dependencies(self):
        """Installa dipendenze"""
        try:
            self.notify("Installando dipendenze...")
            python_exe = os.path.join(self.project_dir, "rag_env", "bin", "pip")
            cmd = [python_exe, "install", "-r", "requirements.txt"]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.notify("Dipendenze installate con successo!")
            else:
                self.notify("Errore installazione dipendenze", severity="error")
                if result.stderr:
                    self.notify(result.stderr, severity="error")

        except Exception as e:
            self.notify(f"Errore: {str(e)}", severity="error")

    def _check_config(self):
        """Controlla configurazione"""
        try:
            self.notify("Controllo configurazione...")

            # Verifica file config
            config_file = os.path.join(self.project_dir, "config.py")
            if os.path.exists(config_file):
                self.notify("config.py trovato")
            else:
                self.notify("config.py non trovato", severity="error")

            # Verifica modelli disponibili
            try:
                from config import AVAILABLE_MODELS
                self.notify(f"Modelli disponibili: {len(AVAILABLE_MODELS)}")
            except Exception as e:
                self.notify(f"Errore modelli: {str(e)}", severity="error")

        except Exception as e:
            self.notify(f"Errore controllo: {str(e)}", severity="error")

    def _test_server(self):
        """Test rapido del server"""
        try:
            self.notify("Test rapido del server...")

            python_exe = os.path.join(self.project_dir, "rag_env", "bin", "python")
            cmd = [python_exe, "-c", "from server import SDRServer; print('✅ Server importato con successo')"]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                self.notify("Test superato!")
                if result.stdout:
                    self.notify(result.stdout)
            else:
                self.notify("Test fallito", severity="error")
                if result.stderr:
                    self.notify(result.stderr, severity="error")

        except Exception as e:
            self.notify(f"Errore test: {str(e)}", severity="error")

    def open_shell(self):
        """Apri shell con virtual environment attivato"""
        try:
            os.chdir(self.project_dir)
            self.notify("Apertura shell con virtual environment...")
            # Avvia bash con venv attivato
            subprocess.run(["bash", "-c", f"source {self.venv_path} && bash"])
        except Exception as e:
            self.notify(f"Errore apertura shell: {str(e)}", severity="error")

    def open_server_page(self):
        """Apri la pagina del server nel browser"""
        if not self.server_process or self.server_process.poll() is not None:
            self.notify("Server non è in esecuzione. Avvia prima il server (opzione 1)", severity="warning")
            return

        try:
            browser_url = f"{self.current_protocol}://localhost:{self.current_port}/"
            webbrowser.open(browser_url)
            self.notify(f"Browser aperto su {browser_url}")
        except Exception as e:
            self.notify(f"Errore apertura browser: {str(e)}", severity="error")

    def quit_app(self):
        """Esci dall'app"""
        if self.server_process and self.server_process.poll() is None:
            self.notify("Server in esecuzione. Fermandolo prima di uscire...", severity="warning")
            self.stop_server()
        self.notify("Arrivederci!")
        self.exit()

if __name__ == "__main__":
    # Verifica e installa dipendenze se necessario
    try:
        from textual.app import App
    except ImportError:
        print("❌ Textual non installato. Installando automaticamente...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "textual"], check=True)
            print("✅ Textual installato con successo.")
            from textual.app import App
        except subprocess.CalledProcessError:
            print("❌ Errore durante l'installazione di textual. Installa manualmente con: pip install textual")
            sys.exit(1)

    app = FlaskLauncher()

    # Controllo ambiente
    if not app.check_environment():
        print("❌ Ambiente non configurato correttamente")
        sys.exit(1)

    # Avvia app
    app.run()