 #!/usr/bin/env python3

"""
Unified Flask Server Launcher - TUI Interface
Combines virtual environment management, imports, and TUI with choice menu
"""

import os
import sys
import subprocess
import time
import signal
import webbrowser
import logging
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.prompt import Prompt
from rich.align import Align

class FlaskLauncher:
    def __init__(self):
        self.console: Console = Console()
        self.server_process = None
        self.project_dir: str = "/home/wildlux/Scaricati/files"
        self.venv_path: str = os.path.join(self.project_dir, "rag_env", "bin", "activate")
        self.cache_cleaned: bool = False
        self.current_host = None
        self.current_port = None
        self.current_protocol: str = "http"

    def show_header(self):
        """Mostra l'header del launcher"""
        header = Panel(
            Align.center(
                Text("🚀 Flask Server Launcher", style="bold blue"),
                vertical="middle"
            ),
            title="[bold green]SDR System[/bold green]",
            border_style="blue"
        )
        self.console.print(header)

    def check_environment(self):
        """Verifica l'ambiente di sviluppo"""
        checks = []

        # Verifica directory progetto
        if os.path.exists(self.project_dir):
            checks.append(("📁 Directory progetto", "✅ OK", "green"))
        else:
            checks.append(("📁 Directory progetto", "❌ Non trovata", "red"))

        # Verifica virtual environment
        if os.path.exists(os.path.join(self.project_dir, "rag_env")):
            checks.append(("🐍 Virtual Environment", "✅ OK", "green"))
        else:
            checks.append(("🐍 Virtual Environment", "❌ Non trovato", "red"))

        # Verifica server.py
        server_py = os.path.join(self.project_dir, "server.py")
        if os.path.exists(server_py):
            checks.append(("⚙️  server.py", "✅ OK", "green"))
        else:
            checks.append(("⚙️  server.py", "❌ Non trovato", "red"))

        # Mostra tabella controlli
        table = Table(title="🔍 Controllo Ambiente")
        table.add_column("Componente", style="cyan")
        table.add_column("Status", style="magenta")

        for component, status, color in checks:
            table.add_row(component, f"[{color}]{status}[/{color}]")

        self.console.print(table)
        return all("✅" in status for _, status, _ in checks)

    def show_menu(self):
        """Mostra il menu principale"""
        self.console.clear()
        self.show_header()

        menu_table: Table = Table(title="🎛️  Menu Principale")
        menu_table.add_column("Opzione", style="cyan", no_wrap=True)
        menu_table.add_column("Descrizione", style="white")
        menu_table.add_column("Stato", style="green")

        if self.server_process and self.server_process.poll() is None:
            server_status = f"🟢 Running su {self.current_protocol}://{self.current_host}:{self.current_port}"
        else:
            server_status = "🔴 Stopped"

        toggle_action = "Ferma Server Flask" if self.server_process and self.server_process.poll() is None else "Avvia Server Flask"
        menu_table.add_row("1", toggle_action, server_status)
        menu_table.add_row("2", "Mostra Messaggi Protocolli", "")
        menu_table.add_row("3", "Controlla Status", "")
        menu_table.add_row("4", "Protocolli", "🔍 Controlli")
        menu_table.add_row("5", "Configurazioni Flask", "⚙️ Setup")
        menu_table.add_row("6", "Pulizia Cache", "🧹 Opzionale")
        menu_table.add_row("7", "(env) 🐚 Shell", "")
        menu_table.add_row("8", "Apri Pagina Server nel Browser", "")
        menu_table.add_row("0", "Esci", "")

        self.console.print(menu_table)

    def start_server(self, host: str = "0.0.0.0", port: str = "8080"):
        """Avvia il server Flask"""
        if self.server_process and self.server_process.poll() is None:
            self.console.print("[red]❌ Server già in esecuzione![/red]")
            return

        try:
            # Cambia directory
            os.chdir(self.project_dir)

            python_exe = os.path.join(self.project_dir, "rag_env", "bin", "python")
            cmd = [python_exe, "server.py", "--host", host, "--port", port]

            self.console.print(f"[green]🚀 Avvio server su {host}:{port}...[/green]")
            self.console.print(f"[dim]Comando: {cmd}[/dim]")

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
                self.console.print(f"[green]✅ Server avviato con successo![/green]")
                self.console.print(f"[blue]📱 Accesso: http://{host}:{port}/[/blue]")

                open_browser = Prompt.ask("Apri browser a questo indirizzo?", choices=["s", "n"], default="s")
                if open_browser == "s":
                    browser_url = f"http://localhost:{port}/"
                    webbrowser.open(browser_url)
                    self.console.print(f"[blue]🌐 Browser aperto su {browser_url}[/blue]")
            else:
                stdout, stderr = self.server_process.communicate()
                self.console.print(f"[red]❌ Errore avvio server:[/red]")
                if stderr:
                    self.console.print(f"[red]{stderr}[/red]")
                if stdout:
                    self.console.print(f"[dim]Output: {stdout}[/dim]")

        except Exception as e:
            self.console.print(f"[red]❌ Errore: {str(e)}[/red]")

    def stop_server(self):
        """Ferma il server Flask"""
        if not self.server_process or self.server_process.poll() is not None:
            self.console.print("[yellow]⚠️  Server non è in esecuzione[/yellow]")
            return

        try:
            # Termina il gruppo di processi
            os.killpg(os.getpgid(self.server_process.pid), signal.SIGTERM)
            self.server_process.wait(timeout=5)
            self.console.print("[green]✅ Server fermato con successo![/green]")
        except subprocess.TimeoutExpired:
            # Forza terminazione se necessario
            os.killpg(os.getpgid(self.server_process.pid), signal.SIGKILL)
            self.console.print("[yellow]⚠️  Server forzatamente terminato[/yellow]")
        except Exception as e:
            self.console.print(f"[red]❌ Errore fermando server: {str(e)}[/red]")
        finally:
            self.server_process = None

    def show_status(self):
        """Mostra lo status del server"""
        table = Table(title="📊 Status Server")
        table.add_column("Parametro", style="cyan")
        table.add_column("Valore", style="white")

        if self.server_process:
            if self.server_process.poll() is None:
                table.add_row("Stato", "[green]🟢 In esecuzione[/green]")
                table.add_row("PID", str(self.server_process.pid))
                table.add_row("Directory", self.project_dir)
            else:
                table.add_row("Stato", "[red]🔴 Fermato[/red]")
                table.add_row("Codice uscita", str(self.server_process.returncode))
        else:
            table.add_row("Stato", "[red]🔴 Non avviato[/red]")

        self.console.print(table)

    def show_logs(self):
        """Mostra i log del server"""
        if not self.server_process:
            self.console.print("[yellow]⚠️  Server non è in esecuzione[/yellow]")
            return

        self.console.print("[blue]📋 Log del server (ultime righe):[/blue]")
        self.console.print("[dim]Premi Ctrl+C per tornare al menu[/dim]")

        try:
            # Mostra output in tempo reale
            while True:
                if self.server_process.stdout:
                    line = self.server_process.stdout.readline()
                    if line:
                        self.console.print(line.strip())
                    else:
                        time.sleep(0.1)
                else:
                    break
        except KeyboardInterrupt:
            self.console.print("[blue]🔙 Ritorno al menu...[/blue]")

    def cleanup_cache(self):
        """Pulisce la cache di Flask"""
        try:
            os.chdir(self.project_dir)

            with self.console.status("[bold green]Pulizia cache in corso..."):
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

            self.console.print("[green]✅ Cache pulita con successo![/green]")
            self.cache_cleaned = True

        except Exception as e:
            self.console.print(f"[red]❌ Errore pulizia cache: {str(e)}[/red]")

    def flask_setup(self):
        """Esegue setup di Flask"""
        try:
            os.chdir(self.project_dir)

            # Menu delle configurazioni
            setup_table = Table(title="⚙️  Configurazioni Flask")
            setup_table.add_column("Opzione", style="cyan", no_wrap=True)
            setup_table.add_column("Descrizione", style="white")
            setup_table.add_column("Status", style="green")

            setup_table.add_row("1", "Installa Dipendenze", "📦 Requirements")
            setup_table.add_row("2", "Controlla Configurazione", "🔍 Verifica")
            setup_table.add_row("3", "Test Server", "🧪 Avvio rapido")
            setup_table.add_row("0", "Torna al Menu Principale", "")

            self.console.print(setup_table)

            while True:
                choice = Prompt.ask("\n[bold cyan]Scegli configurazione", choices=["0", "1", "2", "3"])

                if choice == "0":
                    break

                elif choice == "1":
                    self._install_dependencies()

                elif choice == "2":
                    self._check_config()

                elif choice == "3":
                    self._test_server()

                Prompt.ask("\nPremi Invio per continuare")

        except Exception as e:
            self.console.print(f"[red]❌ Errore nelle configurazioni: {str(e)}[/red]")

    def _install_dependencies(self):
        """Installa dipendenze"""
        try:
            with self.console.status("[bold green]Installando dipendenze..."):
                python_exe = os.path.join(self.project_dir, "rag_env", "bin", "pip")
                cmd = [python_exe, "install", "-r", "requirements.txt"]
                result = subprocess.run(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    self.console.print("[green]✅ Dipendenze installate con successo![/green]")
                else:
                    self.console.print("[red]❌ Errore installazione dipendenze:[/red]")
                    if result.stderr:
                        self.console.print(result.stderr)

        except Exception as e:
            self.console.print(f"[red]❌ Errore: {str(e)}[/red]")

    def _check_config(self):
        """Controlla configurazione"""
        try:
            self.console.print("[blue]🔍 Controllo configurazione...[/blue]")
            
            # Verifica file config
            config_file = os.path.join(self.project_dir, "config.py")
            if os.path.exists(config_file):
                self.console.print("[green]✅ config.py trovato[/green]")
            else:
                self.console.print("[red]❌ config.py non trovato[/red]")

            # Verifica modelli disponibili
            try:
                from config import AVAILABLE_MODELS
                self.console.print(f"[green]✅ Modelli disponibili: {len(AVAILABLE_MODELS)}[/green]")
            except Exception as e:
                self.console.print(f"[red]❌ Errore modelli: {str(e)}[/red]")

        except Exception as e:
            self.console.print(f"[red]❌ Errore controllo: {str(e)}[/red]")

    def _test_server(self):
        """Test rapido del server"""
        try:
            self.console.print("[blue]🧪 Test rapido del server...[/blue]")
            
            python_exe = os.path.join(self.project_dir, "rag_env", "bin", "python")
            cmd = [python_exe, "-c", "from server import SDRServer; print('✅ Server importato con successo')"]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.console.print("[green]✅ Test superato![/green]")
                if result.stdout:
                    self.console.print(result.stdout)
            else:
                self.console.print("[red]❌ Test fallito:[/red]")
                if result.stderr:
                    self.console.print(result.stderr)

        except Exception as e:
            self.console.print(f"[red]❌ Errore test: {str(e)}[/red]")

    def open_shell(self):
        """Apri shell con virtual environment attivato"""
        try:
            os.chdir(self.project_dir)
            self.console.print("[green]🐚 Apertura shell con virtual environment...[/green]")
            self.console.print("[dim]Digita 'exit' per tornare al menu[/dim]")
            # Avvia bash con venv attivato
            subprocess.run(["bash", "-c", f"source {self.venv_path} && bash"], check=True)
        except subprocess.CalledProcessError as e:
            self.console.print(f"[red]❌ Errore apertura shell: {str(e)}[/red]")
        except Exception as e:
            self.console.print(f"[red]❌ Errore: {str(e)}[/red]")

    def open_server_page(self):
        """Apri la pagina del server nel browser"""
        if not self.server_process or self.server_process.poll() is not None:
            self.console.print("[yellow]⚠️  Server non è in esecuzione. Avvia prima il server (opzione 1)[/yellow]")
            return

        try:
            browser_url = f"{self.current_protocol}://localhost:{self.current_port}/"
            webbrowser.open(browser_url)
            self.console.print(f"[green]✅ Browser aperto su {browser_url}[/green]")
        except Exception as e:
            self.console.print(f"[red]❌ Errore apertura browser: {str(e)}[/red]")

    def run(self):
        """Loop principale del launcher"""
        while True:
            self.show_menu()

            try:
                choice = Prompt.ask("\n[bold cyan]Scegli un'opzione", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"])

                if choice == "0":
                    if self.server_process and self.server_process.poll() is None:
                        response = Prompt.ask("Server in esecuzione. Vuoi fermarlo prima di uscire?", choices=["s", "n"], default="s")
                        if response == "s":
                            self.stop_server()
                    self.console.print("[green]👋 Arrivederci![/green]")
                    break

                elif choice == "1":
                    if self.server_process and self.server_process.poll() is None:
                        self.stop_server()
                    else:
                        host = Prompt.ask("Host", default="0.0.0.0")
                        port = Prompt.ask("Porta", default="8080")
                        self.start_server(host, port)

                elif choice == "2":
                    self.show_logs()

                elif choice == "3":
                    self.show_status()

                elif choice == "4":
                    self.show_logs()

                elif choice == "5":
                    self.flask_setup()

                elif choice == "6":
                    self.cleanup_cache()

                elif choice == "7":
                    self.open_shell()

                elif choice == "8":
                    self.open_server_page()

                Prompt.ask("\nPremi Invio per continuare")

            except KeyboardInterrupt:
                self.console.print("\n[blue]🔙 Ritorno al menu...[/blue]")
            except Exception as e:
                self.console.print(f"[red]❌ Errore: {str(e)}[/red]")
                Prompt.ask("\nPremi Invio per continuare")

def main():
    """Main entry point with virtual environment management"""
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
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
        # Verifica dipendenze
        from rich.console import Console
    except ImportError:
        print("❌ Rich non installato. Installa con: pip install rich")
        sys.exit(1)

    launcher = FlaskLauncher()

    # Controllo ambiente
    if not launcher.check_environment():
        print("❌ Ambiente non configurato correttamente")
        sys.exit(1)

    # Avvia launcher
    launcher.run()

if __name__ == "__main__":
    main()