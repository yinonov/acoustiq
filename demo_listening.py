#!/usr/bin/env python3
"""
Quick Demo of Environmental Listening Features
Run this to see the real-time listening capabilities in action.
"""

import asyncio
import sys
from pathlib import Path

# Add the package to path for demo
sys.path.insert(0, str(Path(__file__).parent))

try:
    from audio_intelligence import EnvironmentListener, ListeningEvent
    DEMO_AVAILABLE = True
except ImportError as e:
    print(f"Demo not available: {e}")
    print("Install dependencies: pip install -r requirements.txt")
    DEMO_AVAILABLE = False


def create_demo_callback():
    """Create a colorful callback for demo purposes."""
    
    def demo_callback(event: ListeningEvent):
        # ANSI color codes
        colors = {
            'low': '\033[94m',      # Blue
            'medium': '\033[93m',   # Yellow
            'high': '\033[91m',     # Red
            'critical': '\033[95m'  # Magenta
        }
        reset = '\033[0m'
        
        severity_icons = {
            'low': 'ℹ️',
            'medium': '⚠️',
            'high': '🚨',
            'critical': '🔥'
        }
        
        color = colors.get(event.severity, '')
        icon = severity_icons.get(event.severity, '📢')
        
        timestamp = event.timestamp.strftime('%H:%M:%S')
        print(f"{color}{icon} [{timestamp}] {event.event_type.upper()}: {event.description}{reset}")
        
        # Show key audio features for interesting events
        if event.severity in ['medium', 'high', 'critical']:
            features = event.audio_features
            if 'dominant_frequency' in features:
                print(f"    🎵 Frequency: {features['dominant_frequency']:.1f} Hz")
            if 'rms_energy' in features:
                print(f"    🔊 Energy: {features['rms_energy']:.6f}")
    
    return demo_callback


async def quick_demo():
    """Quick 30-second demo of listening features."""
    if not DEMO_AVAILABLE:
        return
    
    print("🎧 Audio Intelligence - Environmental Listening Demo")
    print("=" * 55)
    print()
    print("This demo will listen to your environment for 30 seconds")
    print("and detect various audio events in real-time.")
    print()
    print("Try these during the demo:")
    print("  • Clap your hands")
    print("  • Say something")
    print("  • Play music")
    print("  • Create silence")
    print("  • Make any interesting sounds!")
    print()
    
    input("Press Enter to start the demo... ")
    print()
    
    try:
        # Initialize listener
        listener = EnvironmentListener(
            sample_rate=44100,
            chunk_duration=0.5,  # Fast response
            agent_enabled=False  # Disable AI for quick demo
        )
        
        # Set sensitive thresholds for demo
        listener.set_thresholds(
            amplitude_threshold=0.005,      # Sensitive to sounds
            frequency_change_threshold=150,  # Detect frequency changes
            silence_duration_threshold=2.0,  # 2 seconds of silence
        )
        
        # Add colorful callback
        listener.add_event_callback(create_demo_callback())
        
        print("🎤 Listening... (30 seconds)")
        print("-" * 40)
        
        # Listen for 30 seconds
        await listener.start_listening(duration=30.0)
        
        # Show summary
        summary = listener.get_session_summary()
        print()
        print("📊 Demo Summary:")
        print("-" * 20)
        print(f"Total events detected: {summary['total_events']}")
        
        if summary['total_events'] > 0:
            print("\nEvent breakdown:")
            for event_type, count in summary['events_by_type'].items():
                print(f"  • {event_type}: {count}")
            
            print("\nSeverity breakdown:")
            for severity, count in summary['events_by_severity'].items():
                print(f"  • {severity}: {count}")
        else:
            print("No events detected - try making some sounds!")
        
        print(f"\nDemo complete! 🎉")
        print("\nTo use the full tool:")
        print("  audio-intelligence listen --duration 60")
        print("  audio-intelligence listen --record-events")
        
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user.")
    except Exception as e:
        print(f"\nDemo error: {e}")
        print("\nTroubleshooting:")
        print("• Check your microphone is working")
        print("• Try: pip install sounddevice soundfile")
        print("• Check audio device permissions")


def print_usage_examples():
    """Print usage examples."""
    print("""
🎧 Environmental Listening - Usage Examples:

COMMAND LINE:
  # Basic listening session
  audio-intelligence listen --duration 60
  
  # Record interesting events
  audio-intelligence listen --record-events --output-dir recordings
  
  # Continuous monitoring
  audio-intelligence listen --sample-rate 22050 --chunk-duration 2.0
  
  # Use specific audio device
  audio-intelligence listen --device 1

PYTHON API:
  from audio_intelligence import EnvironmentListener
  
  listener = EnvironmentListener()
  listener.add_event_callback(lambda e: print(f"Event: {e.description}"))
  await listener.start_listening(duration=60)

PERFECT FOR:
  🏭 Industrial monitoring - detect machinery issues
  🏠 Home security - monitor for unusual sounds  
  🌿 Environmental research - track wildlife sounds
  🏗️ Construction - monitor noise compliance
  🎵 Acoustic testing - validate audio equipment
  
Real-time processing keeps your audio data completely local! 🔒
""")


async def main():
    """Main demo function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        print_usage_examples()
        return
    
    if not DEMO_AVAILABLE:
        print("Environmental Listening Demo")
        print("=" * 30)
        print()
        print("❌ Demo dependencies not installed")
        print()
        print("To install:")
        print("  pip install -r requirements.txt")
        print()
        print("Or install individually:")
        print("  pip install sounddevice soundfile librosa numpy")
        print()
        print_usage_examples()
        return
    
    try:
        await quick_demo()
    except Exception as e:
        print(f"Error running demo: {e}")
        print("\nFor usage examples: python demo_listening.py --examples")


if __name__ == "__main__":
    asyncio.run(main())