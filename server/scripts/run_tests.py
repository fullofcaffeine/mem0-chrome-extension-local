#!/usr/bin/env python3
"""CLI wrapper for running mem0 tests with proper dependency management."""

import subprocess
import sys
import time
import signal
import os
import requests
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def check_service(url: str, name: str, timeout: int = 30) -> bool:
    """Check if a service is responding."""
    console.print(f"🔍 Checking {name}...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                console.print(f"✅ {name} is running")
                return True
        except (requests.RequestException, requests.ConnectionError):
            pass
        time.sleep(2)
    
    console.print(f"❌ {name} not responding after {timeout}s")
    return False


def start_ollama() -> bool:
    """Start Ollama service if not running."""
    if check_service("http://localhost:11434/api/version", "Ollama", timeout=5):
        return True
    
    console.print("⏳ Starting Ollama...")
    try:
        subprocess.run(["brew", "services", "start", "ollama"], 
                      check=False, capture_output=True)
        time.sleep(5)
        return check_service("http://localhost:11434/api/version", "Ollama", timeout=15)
    except Exception as e:
        console.print(f"⚠️ Failed to start Ollama: {e}")
        return False


def start_qdrant() -> bool:
    """Start Qdrant container if not running."""
    if check_service("http://localhost:6333/", "Qdrant", timeout=5):
        return True
    
    console.print("⏳ Starting Qdrant container...")
    try:
        project_root = get_project_root()
        storage_path = project_root / "server" / "qdrant_storage"
        storage_path.mkdir(exist_ok=True)
        
        # Stop any existing container
        subprocess.run(["docker", "stop", "qdrant"], 
                      check=False, capture_output=True)
        subprocess.run(["docker", "rm", "qdrant"], 
                      check=False, capture_output=True)
        
        # Start new container
        cmd = [
            "docker", "run", "-d", "--name", "qdrant",
            "-p", "6333:6333", "-p", "6334:6334",
            "-v", f"{storage_path}:/qdrant/storage:z",
            "qdrant/qdrant"
        ]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        time.sleep(10)
        return check_service("http://localhost:6333/", "Qdrant", timeout=20)
    except Exception as e:
        console.print(f"⚠️ Failed to start Qdrant: {e}")
        return False


def start_mem0_server() -> tuple[bool, Optional[subprocess.Popen]]:
    """Start the Mem0 server."""
    if check_service("http://localhost:8000/health", "Mem0 server", timeout=5):
        console.print("✅ Mem0 server already running")
        return True, None
    
    console.print("⏳ Starting Mem0 server...")
    try:
        project_root = get_project_root()
        venv_path = project_root / ".venv"
        
        if sys.platform == "win32":
            python_cmd = str(venv_path / "Scripts" / "python")
        else:
            python_cmd = str(venv_path / "bin" / "python")
        
        # Kill any existing server processes
        try:
            subprocess.run(["pkill", "-f", "local_mem0_with_rag.py"], 
                          check=False, capture_output=True)
            subprocess.run(["lsof", "-ti", "tcp:8000"], 
                          capture_output=True, text=True, check=False)
        except Exception:
            pass
        
        # Start server
        server_script = project_root / "server" / "local_mem0_with_rag.py"
        env = os.environ.copy()
        env["MEM0_TEST_MODE"] = "1"
        env["PYTHONPATH"] = str(project_root)
        
        process = subprocess.Popen(
            [python_cmd, str(server_script)],
            cwd=project_root / "server",
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to be ready
        if check_service("http://localhost:8000/health", "Mem0 server", timeout=40):
            return True, process
        else:
            process.terminate()
            return False, None
            
    except Exception as e:
        console.print(f"❌ Failed to start Mem0 server: {e}")
        return False, None


@click.command()
@click.option('--type', '-t', type=click.Choice(['all', 'unit', 'integration', 'server']), 
              default='all', help='Type of tests to run')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--coverage', '-c', is_flag=True, help='Run with coverage report')
@click.option('--fail-fast', '-x', is_flag=True, help='Stop on first failure')
@click.option('--no-deps', is_flag=True, help='Skip dependency checks (assume services are running)')
def main(type: str, verbose: bool, coverage: bool, fail_fast: bool, no_deps: bool) -> None:
    """Run mem0 test suite with proper dependency management."""
    
    project_root = get_project_root()
    venv_path = project_root / ".venv"
    server_process: Optional[subprocess.Popen] = None
    
    console.print(Panel.fit(
        Text("🧪 Running Mem0 Integration Tests", style="bold yellow"),
        border_style="yellow"
    ))
    
    # Check virtual environment
    if not venv_path.exists():
        console.print("❌ Virtual environment not found. Run 'mem0-setup' first.")
        sys.exit(1)
    
    try:
        # Start dependencies if needed
        if not no_deps:
            console.print(Panel.fit(
                Text("🚀 Starting Dependencies", style="bold blue"),
                border_style="blue"
            ))
            
            # Start Ollama
            if not start_ollama():
                console.print("⚠️ Ollama not available - some tests may fail")
            
            # Start Qdrant
            if not start_qdrant():
                console.print("❌ Failed to start Qdrant - tests will likely fail")
                sys.exit(1)
            
            # Start Mem0 server
            server_started, server_process = start_mem0_server()
            if not server_started:
                console.print("❌ Failed to start Mem0 server - tests will fail")
                sys.exit(1)
            
            console.print("✅ All dependencies are ready!")
        
        # Determine Python executable
        if sys.platform == "win32":
            python_cmd = str(venv_path / "Scripts" / "python")
        else:
            python_cmd = str(venv_path / "bin" / "python")
        
        # Build pytest command
        cmd = [python_cmd, "-m", "pytest"]
        
        # Add test paths based on type
        if type == "all":
            cmd.extend(["tests/", "server/tests/"])
        elif type == "unit":
            cmd.extend(["tests/", "-m", "unit"])
        elif type == "integration":
            cmd.extend(["tests/", "-m", "integration"])
        elif type == "server":
            cmd.extend(["server/tests/"])
        
        # Add options
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if fail_fast:
            cmd.append("-x")
        
        if coverage:
            cmd.extend(["--cov=server", "--cov-report=term-missing"])
        
        # Add test discovery options
        cmd.extend([
            "--tb=short",
            "--strict-markers",
        ])
        
        console.print(f"📝 Running: {' '.join(cmd[2:])}")  # Skip python -m pytest
        
        # Set environment variables
        env = os.environ.copy()
        env["PYTHONPATH"] = str(project_root)
        
        # Run tests
        result = subprocess.run(cmd, cwd=project_root, env=env)
        
        if result.returncode == 0:
            console.print("✅ All tests passed!")
        else:
            console.print("❌ Some tests failed")
            sys.exit(result.returncode)
            
    except KeyboardInterrupt:
        console.print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        console.print(f"❌ Failed to run tests: {e}")
        sys.exit(1)
    finally:
        # Clean up server process
        if server_process:
            console.print("🛑 Stopping Mem0 server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()


if __name__ == "__main__":
    main() 
