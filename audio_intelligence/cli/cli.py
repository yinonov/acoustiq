"""
Command Line Interface for Audio Intelligence Tool
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

try:
    import click
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.panel import Panel
    CLI_DEPS_AVAILABLE = True
except ImportError:
    CLI_DEPS_AVAILABLE = False
    print("CLI dependencies not installed. Run: pip install click rich")

if CLI_DEPS_AVAILABLE:
    from ..analyzer import AudioAnalyzer

    console = Console()

    @click.group()
    def cli():
        """Audio Intelligence Tool - Smart audio analysis for acoustic engineers."""
        pass

    @cli.command()
    @click.option('--file', '-f', required=True, help='Path to audio file to analyze')
    @click.option('--output', '-o', help='Output file for results (JSON format)')
    @click.option('--interactive', '-i', is_flag=True, help='Start interactive Q&A mode after analysis')
    @click.option('--no-ai', is_flag=True, help='Disable AI agent features')
    @click.option('--basic-only', is_flag=True, help='Only extract basic features (faster)')
    def analyze(file: str, output: Optional[str], interactive: bool, no_ai: bool, basic_only: bool):
        """Analyze an audio file and generate insights."""
        asyncio.run(_analyze_command(file, output, interactive, not no_ai, not basic_only))

    # ... rest of the CLI implementation would go here
    # For now, creating a minimal version

    @cli.command()
    @click.option('--duration', '-d', type=float, help='Duration to listen in seconds (default: infinite)')
    @click.option('--device', type=int, help='Audio input device ID (default: system default)')
    @click.option('--sample-rate', '-sr', default=44100, help='Sample rate in Hz')
    @click.option('--chunk-duration', '-cd', default=1.0, help='Analysis chunk duration in seconds')
    @click.option('--record-events', '-r', is_flag=True, help='Record audio snippets of detected events')
    @click.option('--output-dir', '-o', default='session_data', help='Output directory for recordings and data')
    @click.option('--no-ai', is_flag=True, help='Disable AI agent features')
    def listen(duration, device, sample_rate, chunk_duration, record_events, output_dir, no_ai):
        """Start a real-time environmental listening session."""
        import asyncio
        asyncio.run(_listen_command(duration, device, sample_rate, chunk_duration, 
                                   record_events, output_dir, not no_ai))

    async def _listen_command(duration, device, sample_rate, chunk_duration, 
                             record_events, output_dir, ai_enabled):
        """Async implementation of listen command."""
        try:
            from ..listener import EnvironmentListener
            
            console.print("[bold green]Starting Environmental Listening Session[/bold green]")
            
            # Initialize listener
            listener = EnvironmentListener(
                sample_rate=sample_rate,
                chunk_duration=chunk_duration,
                device=device,
                agent_enabled=ai_enabled
            )
            
            # Set up recording if requested
            if record_events:
                from pathlib import Path
                Path(output_dir).mkdir(exist_ok=True)
                listener.set_recording(True, output_dir)
                console.print(f"[green]Event recordings will be saved to: {output_dir}[/green]")
            
            # Add event callback for real-time display
            def display_event(event):
                severity_colors = {
                    'low': 'blue',
                    'medium': 'yellow',
                    'high': 'red',
                    'critical': 'bright_red'
                }
                color = severity_colors.get(event.severity, 'white')
                
                console.print(f"[{color}]{event.timestamp.strftime('%H:%M:%S')} - "
                            f"{event.event_type.upper()}: {event.description}[/{color}]")
            
            listener.add_event_callback(display_event)
            
            # Start listening
            try:
                await listener.start_listening(duration)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping listening session...[/yellow]")
            
            # Display session summary
            summary = listener.get_session_summary()
            console.print("\n" + "="*60)
            console.print("[bold blue]Session Summary[/bold blue]")
            console.print("="*60)
            
            console.print(f"Duration: {summary['session_duration_seconds']:.1f} seconds")
            console.print(f"Total Events: {summary['total_events']}")
            
            if summary['total_events'] > 0:
                console.print("\nEvents by Type:")
                for event_type, count in summary['events_by_type'].items():
                    console.print(f"  {event_type}: {count}")
                
                console.print("\nEvents by Severity:")
                for severity, count in summary['events_by_severity'].items():
                    console.print(f"  {severity}: {count}")
            
            # Export session data
            from datetime import datetime
            session_file = f"{output_dir}/session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            listener.export_session_data(session_file)
            console.print(f"\n[green]Session data exported to: {session_file}[/green]")
            
            # Interactive Q&A about the session
            if ai_enabled and summary['total_events'] > 0:
                console.print("\n[cyan]Ask questions about the listening session (type 'quit' to exit):[/cyan]")
                while True:
                    try:
                        question = console.input("\nQuestion: ")
                        if question.lower() in ['quit', 'exit', 'q']:
                            break
                        if question.strip():
                            answer = await listener.ask_about_session(question)
                            console.print(f"[yellow]Answer:[/yellow] {answer}")
                    except KeyboardInterrupt:
                        break
            
        except ImportError as e:
            console.print(f"[red]Error: {e}[/red]")
            console.print("[yellow]Install real-time audio dependencies with:[/yellow]")
            console.print("pip install sounddevice soundfile")
        except Exception as e:
            console.print(f"[red]Error during listening session: {e}[/red]")

else:
    def cli():
        print("CLI dependencies not available. Please install: pip install click rich")