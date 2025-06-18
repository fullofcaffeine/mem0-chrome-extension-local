#!/usr/bin/env python3
"""
List all memories from the local Mem0 database.
This script helps you inspect what memories have been stored.
"""

import json
import sys
from pathlib import Path

import click
import requests
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@click.command()
@click.option('--user-id', '-u', default='chrome-extension-user', 
              help='User ID to list memories for')
@click.option('--limit', '-l', default=50, help='Maximum number of memories to show')
@click.option('--search', '-s', help='Search query to filter memories')
@click.option('--format', '-f', type=click.Choice(['table', 'json', 'text']), 
              default='table', help='Output format')
@click.option('--server', default='http://localhost:8000', 
              help='Server URL')
@click.option('--full', is_flag=True, help='Show full memory text without truncation')
def main(user_id: str, limit: int, search: str, format: str, server: str, full: bool) -> None:
    """List memories from the local Mem0 server."""
    
    console.print(Panel.fit(
        Text("🧠 Mem0 Memory Explorer", style="bold purple"),
        border_style="purple"
    ))
    
    try:
        # Check if server is running
        try:
            response = requests.get(f"{server}/health", timeout=5)
            if response.status_code != 200:
                console.print(f"❌ Server health check failed: {response.status_code}")
                sys.exit(1)
        except requests.exceptions.ConnectionError:
            console.print(f"❌ Cannot connect to mem0 server at {server}")
            console.print("   Make sure the server is running with: mem0-start")
            sys.exit(1)
        
        # Get memories
        if search:
            # Search endpoint
            response = requests.post(
                f"{server}/v1/memories/search/",
                json={"query": search, "user_id": user_id, "limit": limit},
                timeout=30
            )
        else:
            # List endpoint
            params = {"user_id": user_id, "limit": limit}
            response = requests.get(f"{server}/v1/memories/", params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            memories = data.get("results", data) if "results" in data else data
            
            if not memories:
                console.print(f"📭 No memories found for user: {user_id}")
                if search:
                    console.print(f"   Search query: '{search}'")
                return
            
            console.print(f"🧠 Found {len(memories)} memories for user: {user_id}")
            if search:
                console.print(f"🔍 Search query: '{search}'")
            
            if format == "json":
                console.print_json(data=memories)
            elif format == "table":
                display_table(memories, full)
            else:  # text format
                display_text(memories, full)
                
        else:
            console.print(f"❌ Failed to fetch memories: {response.status_code}")
            console.print(f"Response: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Error: {e}")
        sys.exit(1)


def display_table(memories, full: bool):
    """Display memories in a table format."""
    table = Table(title="Memories")
    table.add_column("ID", style="cyan", min_width=8)
    table.add_column("Memory", style="white", min_width=40 if not full else 80)
    table.add_column("Created", style="green", min_width=12)
    table.add_column("Platform", style="yellow", min_width=10)
    
    for memory in memories:
        memory_id = str(memory.get('id', 'N/A'))[:8]
        memory_text = str(memory.get('memory', 'N/A'))
        
        if not full and len(memory_text) > 60:
            memory_text = memory_text[:60] + "..."
        
        created = memory.get('created_at', 'N/A')
        if created != 'N/A' and 'T' in created:
            created = created.split('T')[0]  # Just the date part
        
        platform = memory.get('metadata', {}).get('platform', 'Unknown')
        
        table.add_row(memory_id, memory_text, created, platform)
    
    console.print(table)


def display_text(memories, full: bool):
    """Display memories in text format."""
    for i, memory in enumerate(memories, 1):
        memory_text = memory.get('memory', 'N/A')
        if not full and len(memory_text) > 200:
            memory_text = memory_text[:200] + "..."
        
        console.print(Panel(
            f"[bold]Memory #{i}[/bold]\n"
            f"[cyan]ID:[/cyan] {memory.get('id', 'N/A')}\n"
            f"[cyan]Text:[/cyan] {memory_text}\n"
            f"[cyan]Created:[/cyan] {memory.get('created_at', 'N/A')}\n"
            f"[cyan]Metadata:[/cyan] {json.dumps(memory.get('metadata', {}), indent=2)}",
            title=f"Memory {i}",
            border_style="blue"
        ))


if __name__ == "__main__":
    main() 
