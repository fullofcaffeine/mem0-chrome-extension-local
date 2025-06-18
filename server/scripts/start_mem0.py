#!/usr/bin/env python3
"""CLI wrapper for starting the mem0 server."""

import os
import subprocess
import sys
import time
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

console = Console()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def check_service(name: str, check_cmd: list, port: int = None) -> bool:
    """Check if a service is running."""
    try:
        result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


@click.command()
@click.option('--check-deps', '-c', is_flag=True, help='Check dependencies before starting')
@click.option('--dev', '-d', is_flag=True, help='Start in development mode with auto-reload')
@click.option('--port', '-p', default=8000, help='Port to run the server on')
def main(check_deps: bool, dev: bool, port: int) -> None:
    """Start the mem0 local server with all dependencies."""
    
    project_root = get_project_root()
    server_path = project_root / "server"
    venv_path = project_root / ".venv"
    
    console.print(Panel.fit(
        Text("🚀 Starting Mem0 Local Server", style="bold green"),
        border_style="green"
    ))
    
    # Check virtual environment
    if not venv_path.exists():
        console.print("❌ Virtual environment not found. Run 'mem0-setup' first.")
        sys.exit(1)
    
    # Determine Python executable
    if sys.platform == "win32":
        python_cmd = str(venv_path / "Scripts" / "python")
    else:
        python_cmd = str(venv_path / "bin" / "python")
    
    if check_deps:
        console.print("🔍 Checking dependencies...")
        
        # Check Ollama
        if check_service("Ollama", ["ollama", "list"]):
            console.print("✅ Ollama is running")
        else:
            console.print("❌ Ollama not found. Install with: brew install ollama")
            console.print("   Then start with: ollama serve")
            sys.exit(1)
        
        # Check Docker/Qdrant
        if check_service("Docker", ["docker", "ps"], 6333):
            console.print("✅ Docker is running")
            # Check if Qdrant container exists
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=qdrant", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            if "qdrant" in result.stdout:
                console.print("✅ Qdrant container is running")
            else:
                console.print("🔄 Starting Qdrant container...")
                subprocess.run([
                    "docker", "run", "-d", "--name", "qdrant", 
                    "-p", "6333:6333", "-p", "6334:6334", 
                    "qdrant/qdrant"
                ])
                time.sleep(3)  # Give it time to start
                console.print("✅ Qdrant container started")
        else:
            console.print("❌ Docker not found or not running")
            console.print("   Install Docker Desktop or start Docker service")
            sys.exit(1)
    
    # Start the server
    console.print(f"🌐 Starting server on port {port}...")
    
    try:
        server_script = server_path / "local_mem0_with_rag.py"
        if not server_script.exists():
            console.print(f"❌ Server script not found: {server_script}")
            sys.exit(1)
        
        # Server startup command
        cmd = [python_cmd, str(server_script)]
        env = os.environ.copy()
        env["PORT"] = str(port)
        
        if dev:
            console.print("🔧 Starting in development mode...")
            env["DEV_MODE"] = "true"
        
        console.print(Panel(
            Text(f"Server starting at: http://localhost:{port}\n"
                f"API Documentation: http://localhost:{port}/docs\n"
                f"Press Ctrl+C to stop", style="cyan"),
            title="Server Info",
            border_style="cyan"
        ))
        
        # Run the server
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Starting server...", total=None)
            
            process = subprocess.Popen(
                cmd,
                cwd=server_path,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            progress.remove_task(task)
            
            # Stream output
            for line in process.stdout:
                console.print(line.rstrip())
            
            process.wait()
    
    except KeyboardInterrupt:
        console.print("\n🛑 Server stopped by user")
    except Exception as e:
        console.print(f"❌ Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
