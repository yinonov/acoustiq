"""
Command Line Interface for Audio Intelligence Tool
"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.syntax import Syntax

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


async def _analyze_command(file_path: str, output_path: Optional[str], interactive: bool, 
                          ai_enabled: bool, include_advanced: bool):
    """Async implementation of analyze command."""
    
    # Check if file exists
    if not Path(file_path).exists():
        console.print(f"[red]Error: Audio file not found: {file_path}[/red]")
        return
    
    # Initialize analyzer
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Initializing analyzer...", total=None)
        
        try:
            analyzer = AudioAnalyzer(agent_enabled=ai_enabled)
            progress.update(task, description="Getting file information...")
            
            # Get basic file info first
            file_info = analyzer.get_file_info(file_path)
            
            # Display file info
            console.print("\n" + "="*60)
            console.print(f"[bold blue]Audio File Analysis: {Path(file_path).name}[/bold blue]")
            console.print("="*60)
            
            info_table = Table(show_header=False, box=None)
            info_table.add_column("Property", style="cyan")
            info_table.add_column("Value", style="white")
            
            info_table.add_row("File Size", f"{file_info['file_size_bytes']:,} bytes")
            info_table.add_row("Duration", f"{file_info['duration_seconds']:.2f} seconds")
            info_table.add_row("Sample Rate", f"{file_info['sample_rate']:,} Hz")
            info_table.add_row("Channels", str(file_info['channels']))
            info_table.add_row("Format", f"{file_info['format']} ({file_info['subtype']})")
            
            console.print(info_table)
            console.print()
            
            # Perform analysis
            progress.update(task, description="Analyzing audio features...")
            results = await analyzer.analyze_file(file_path, include_advanced=include_advanced)
            
            progress.update(task, description="Analysis complete!")
            
        except Exception as e:
            progress.stop()
            console.print(f"[red]Error during analysis: {e}[/red]")
            return
    
    # Display results
    _display_analysis_results(results)
    
    # Save results if requested
    if output_path:
        try:
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            console.print(f"\n[green]Results saved to: {output_path}[/green]")
        except Exception as e:
            console.print(f"[red]Error saving results: {e}[/red]")
    
    # Interactive mode
    if interactive and ai_enabled:
        await _interactive_mode(analyzer, results)


def _display_analysis_results(results: dict):
    """Display analysis results in a formatted way."""
    
    # Basic Features
    if 'basic_features' in results:
        console.print(Panel.fit("[bold green]Basic Audio Features[/bold green]"))
        
        features_table = Table(show_header=True, header_style="bold magenta")
        features_table.add_column("Feature", style="cyan")
        features_table.add_column("Value", style="white")
        
        basic = results['basic_features']
        features_table.add_row("Duration", f"{basic['duration']:.2f} seconds")
        features_table.add_row("RMS Energy", f"{basic['rms_energy']:.6f}")
        features_table.add_row("Max Amplitude", f"{basic['max_amplitude']:.6f}")
        features_table.add_row("Dominant Frequency", f"{basic.get('dominant_frequency', 'N/A'):.1f} Hz")
        features_table.add_row("Spectral Centroid", f"{basic['spectral_centroid_mean']:.1f} Hz")
        features_table.add_row("Zero Crossing Rate", f"{basic['zero_crossing_rate_mean']:.6f}")
        
        if 'frequency_range_min' in basic:
            freq_range = f"{basic['frequency_range_min']:.0f} - {basic['frequency_range_max']:.0f} Hz"
            features_table.add_row("Significant Freq Range", freq_range)
        
        console.print(features_table)
        console.print()
    
    # Anomalies
    if 'anomalies' in results:
        anomalies = results['anomalies']
        issues_found = []
        
        if anomalies.get('clipping_detected'):
            issues_found.append(f"Clipping detected ({anomalies['clipped_sample_ratio']:.4f} ratio)")
        
        if anomalies.get('excessive_silence'):
            issues_found.append(f"Excessive silence ({anomalies['silence_ratio']:.2f} ratio)")
        
        if anomalies.get('significant_dc_offset'):
            issues_found.append(f"DC offset detected ({anomalies['dc_offset']:.4f})")
        
        if anomalies.get('low_dynamic_range'):
            issues_found.append(f"Low dynamic range ({anomalies['dynamic_range_db']:.1f} dB)")
        
        if issues_found:
            console.print(Panel.fit("[bold red]Audio Quality Issues[/bold red]"))
            for issue in issues_found:
                console.print(f"[red]⚠ {issue}[/red]")
        else:
            console.print(Panel.fit("[bold green]No Audio Quality Issues Detected[/bold green]"))
        
        console.print()
    
    # AI Insights
    if 'ai_insights' in results and results['ai_insights'] != "AI analysis unavailable":
        console.print(Panel.fit("[bold yellow]AI Insights[/bold yellow]"))
        console.print(results['ai_insights'])
        console.print()


async def _interactive_mode(analyzer: AudioAnalyzer, context: dict):
    """Interactive Q&A mode with the AI agent."""
    console.print(Panel.fit("[bold blue]Interactive Mode[/bold blue]"))
    console.print("Ask questions about your audio analysis. Type 'quit' to exit.\n")
    
    while True:
        try:
            question = console.input("[cyan]Question: [/cyan]")
            
            if question.lower() in ['quit', 'exit', 'q']:
                console.print("[green]Goodbye![/green]")
                break
            
            if not question.strip():
                continue
            
            # Get answer from AI agent
            with Progress(
                SpinnerColumn(),
                TextColumn("Thinking..."),
                console=console,
            ) as progress:
                task = progress.add_task("", total=None)
                answer = await analyzer.ask(question, context)
            
            console.print(f"\n[yellow]Answer:[/yellow] {answer}\n")
            
        except KeyboardInterrupt:
            console.print("\n[green]Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--extensions', '-e', default='wav,mp3,flac,m4a', 
              help='Comma-separated list of file extensions to process')
@click.option('--output-dir', '-o', help='Directory to save analysis results')
@click.option('--no-ai', is_flag=True, help='Disable AI agent features')
def batch(directory: str, extensions: str, output_dir: Optional[str], no_ai: bool):
    """Batch process multiple audio files in a directory."""
    asyncio.run(_batch_command(directory, extensions, output_dir, not no_ai))


async def _batch_command(directory: str, extensions: str, output_dir: Optional[str], ai_enabled: bool):
    """Async implementation of batch command."""
    
    # Find audio files
    ext_list = [f".{ext.strip()}" for ext in extensions.split(',')]
    audio_files = []
    
    for ext in ext_list:
        audio_files.extend(Path(directory).glob(f"*{ext}"))
        audio_files.extend(Path(directory).glob(f"*{ext.upper()}"))
    
    if not audio_files:
        console.print(f"[red]No audio files found in {directory} with extensions: {extensions}[/red]")
        return
    
    console.print(f"[green]Found {len(audio_files)} audio files to process[/green]\n")
    
    # Initialize analyzer
    analyzer = AudioAnalyzer(agent_enabled=ai_enabled)
    
    # Process files
    results = {}
    with Progress(console=console) as progress:
        main_task = progress.add_task("Processing files...", total=len(audio_files))
        
        for audio_file in audio_files:
            progress.update(main_task, description=f"Processing {audio_file.name}...")
            
            try:
                file_results = await analyzer.analyze_file(str(audio_file), include_advanced=False)
                results[str(audio_file)] = file_results
                
                # Save individual result if output directory specified
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(exist_ok=True)
                    result_file = output_path / f"{audio_file.stem}_analysis.json"
                    
                    with open(result_file, 'w') as f:
                        json.dump(file_results, f, indent=2, default=str)
                
            except Exception as e:
                console.print(f"[red]Error processing {audio_file.name}: {e}[/red]")
                results[str(audio_file)] = {"error": str(e)}
            
            progress.advance(main_task)
    
    console.print(f"\n[green]Batch processing complete! Processed {len(audio_files)} files.[/green]")
    
    if output_dir:
        console.print(f"[green]Results saved to: {output_dir}[/green]")


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
        console.print("[yellow]Note: sounddevice requires PortAudio library to be installed on your system.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error during listening session: {e}[/red]")


if __name__ == "__main__":
    cli()