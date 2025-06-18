#!/usr/bin/env python3
"""CLI wrapper for setting up the mem0 environment."""

import os
import subprocess
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def get_project_root() -> Path:
    """Get the project root directory."""
    # Assuming this script is in server/scripts/
    return Path(__file__).parent.parent.parent


@click.command()
@click.option('--force', '-f', is_flag=True, help='Force recreate environment if it exists')
@click.option('--python', '-p', default='python3', help='Python interpreter to use')
def main(force: bool, python: str) -> None:
    """Set up the mem0 local environment with all dependencies."""
    
    project_root = get_project_root()
    venv_path = project_root / ".venv"
    
    console.print(Panel.fit(
        Text("🧠 Mem0 Environment Setup", style="bold blue"),
        border_style="blue"
    ))
    
    try:
        # Check if virtual environment exists
        if venv_path.exists() and not force:
            console.print(f"✅ Virtual environment already exists at {venv_path}")
            console.print("Use --force to recreate it")
            return
        
        # Remove existing environment if force is specified
        if venv_path.exists() and force:
            console.print(f"🗑️  Removing existing environment...")
            import shutil
            shutil.rmtree(venv_path)
        
        # Create virtual environment
        console.print(f"🏗️  Creating virtual environment with {python}...")
        result = subprocess.run([python, "-m", "venv", str(venv_path)], 
                               cwd=project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"❌ Failed to create virtual environment: {result.stderr}")
            sys.exit(1)
        
        # Determine activation script
        if sys.platform == "win32":
            activate_script = venv_path / "Scripts" / "activate"
            pip_cmd = str(venv_path / "Scripts" / "pip")
        else:
            activate_script = venv_path / "bin" / "activate"
            pip_cmd = str(venv_path / "bin" / "pip")
        
        # Install basic dependencies
        console.print("📦 Installing base dependencies...")
        result = subprocess.run([pip_cmd, "install", "--upgrade", "pip"], 
                               cwd=project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"❌ Failed to upgrade pip: {result.stderr}")
            sys.exit(1)
        
        # Install mem0 and other dependencies
        console.print("📦 Installing mem0 and dependencies...")
        deps = [
            "mem0ai",
            "fastapi",
            "uvicorn",
            "qdrant-client",
            "ollama",
            "sentence-transformers",
            "pytest",
            "pytest-asyncio",
            "httpx",
        ]
        
        result = subprocess.run([pip_cmd, "install"] + deps, 
                               cwd=project_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"❌ Failed to install dependencies: {result.stderr}")
            sys.exit(1)
        
        console.print("✅ Environment setup complete!")
        console.print(f"📍 Virtual environment: {venv_path}")
        console.print(f"🔄 To activate: source {activate_script}")
        
        console.print(Panel(
            Text("Next steps:\n"
                "1. Activate the environment\n"
                "2. Install Ollama: brew install ollama\n"
                "3. Install Docker for Qdrant\n"
                "4. Run: mem0-start to start the server", 
                style="green"),
            title="Setup Complete",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 
