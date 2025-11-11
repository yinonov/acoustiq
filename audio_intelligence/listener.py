"""
Real-time Audio Monitoring and Listening Session
Continuously monitors environmental sounds with live analysis and alerts.
"""

import asyncio
import numpy as np
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from pathlib import Path
import threading
import queue
from datetime import datetime
import json

AUDIO_INPUT_AVAILABLE = False
sd = None
sf = None

def _check_audio_imports():
    """Lazy import of audio dependencies."""
    global AUDIO_INPUT_AVAILABLE, sd, sf
    if AUDIO_INPUT_AVAILABLE:
        return True
    
    try:
        import sounddevice as _sd
        import soundfile as _sf
        sd = _sd
        sf = _sf
        AUDIO_INPUT_AVAILABLE = True
        return True
    except (ImportError, OSError) as e:
        # OSError occurs when PortAudio is not installed
        return False

from .analyzer import AudioAnalyzer


@dataclass
class ListeningEvent:
    """Represents an event detected during listening session."""
    timestamp: datetime
    event_type: str
    description: str
    audio_features: Dict[str, Any]
    severity: str  # 'low', 'medium', 'high', 'critical'
    audio_snippet: Optional[np.ndarray] = None


class EnvironmentListener:
    """Real-time environmental sound monitoring system."""
    
    def __init__(self, 
                 sample_rate: int = 44100,
                 chunk_duration: float = 1.0,
                 device: Optional[int] = None,
                 agent_enabled: bool = True):
        """Initialize the environment listener.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of each analysis chunk in seconds
            device: Audio input device ID (None for default)
            agent_enabled: Whether to enable AI agent for analysis
        """
        if not _check_audio_imports():
            raise ImportError("sounddevice and soundfile required for real-time monitoring. "
                            "Install with: pip install sounddevice soundfile\n"
                            "Note: sounddevice requires PortAudio library to be installed on your system.")
        
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        self.device = device
        
        # Initialize analyzer
        self.analyzer = AudioAnalyzer(agent_enabled=agent_enabled)
        
        # Session state
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.events: List[ListeningEvent] = []
        self.session_start_time = None
        
        # Thresholds and settings (can be customized)
        self.amplitude_threshold = 0.01  # Minimum amplitude to consider
        self.frequency_change_threshold = 100  # Hz change to trigger alert
        self.silence_duration_threshold = 5.0  # Seconds of silence to alert
        self.anomaly_sensitivity = 0.8  # 0-1, higher = more sensitive
        
        # Baseline measurements (updated during listening)
        self.baseline_amplitude = None
        self.baseline_frequency = None
        self.baseline_spectral_centroid = None
        
        # Event callbacks
        self.event_callbacks: List[Callable[[ListeningEvent], None]] = []
        
        # Recording settings
        self.record_events = False
        self.recording_dir = None
        self.event_recording_duration = 5.0  # seconds
    
    def add_event_callback(self, callback: Callable[[ListeningEvent], None]):
        """Add a callback function to be called when events are detected."""
        self.event_callbacks.append(callback)
    
    def set_recording(self, enabled: bool, output_dir: str = "recordings"):
        """Enable/disable recording of detected events.
        
        Args:
            enabled: Whether to record audio snippets of events
            output_dir: Directory to save recordings
        """
        self.record_events = enabled
        if enabled:
            self.recording_dir = Path(output_dir)
            self.recording_dir.mkdir(exist_ok=True)
    
    def set_thresholds(self, 
                      amplitude_threshold: Optional[float] = None,
                      frequency_change_threshold: Optional[float] = None,
                      silence_duration_threshold: Optional[float] = None,
                      anomaly_sensitivity: Optional[float] = None):
        """Update detection thresholds."""
        if amplitude_threshold is not None:
            self.amplitude_threshold = amplitude_threshold
        if frequency_change_threshold is not None:
            self.frequency_change_threshold = frequency_change_threshold
        if silence_duration_threshold is not None:
            self.silence_duration_threshold = silence_duration_threshold
        if anomaly_sensitivity is not None:
            self.anomaly_sensitivity = anomaly_sensitivity
    
    def _audio_callback(self, indata, frames, time, status):
        """Callback function for audio input stream."""
        if status:
            print(f"Audio input status: {status}")
        
        # Put audio data in queue for processing
        audio_chunk = indata[:, 0].copy()  # Use first channel
        self.audio_queue.put((audio_chunk, time.inputBufferAdcTime))
    
    def _establish_baseline(self, initial_chunks: int = 10):
        """Establish baseline measurements from initial audio chunks."""
        print(f"Establishing baseline from {initial_chunks} chunks...")
        baseline_data = []
        
        for i in range(initial_chunks):
            try:
                audio_chunk, timestamp = self.audio_queue.get(timeout=2.0)
                baseline_data.append(audio_chunk)
            except queue.Empty:
                print("Warning: Could not get enough baseline data")
                break
        
        if baseline_data:
            # Combine all baseline chunks
            combined_baseline = np.concatenate(baseline_data)
            
            # Calculate baseline features
            features = self.analyzer.extract_basic_features(combined_baseline, self.sample_rate)
            
            self.baseline_amplitude = features['rms_energy']
            self.baseline_frequency = features.get('dominant_frequency', 440.0)
            self.baseline_spectral_centroid = features['spectral_centroid_mean']
            
            print(f"Baseline established:")
            print(f"  Amplitude: {self.baseline_amplitude:.6f}")
            print(f"  Dominant Frequency: {self.baseline_frequency:.1f} Hz")
            print(f"  Spectral Centroid: {self.baseline_spectral_centroid:.1f} Hz")
        else:
            print("Warning: Could not establish baseline")
    
    def _analyze_chunk(self, audio_chunk: np.ndarray, timestamp: float) -> List[ListeningEvent]:
        """Analyze a single audio chunk for events."""
        events = []
        
        # Extract features
        features = self.analyzer.extract_basic_features(audio_chunk, self.sample_rate)
        anomalies = self.analyzer.detect_anomalies(audio_chunk, self.sample_rate)
        
        current_time = datetime.fromtimestamp(timestamp)
        
        # Check for silence
        if features['rms_energy'] < self.amplitude_threshold:
            if len(self.events) == 0 or (current_time - self.events[-1].timestamp).total_seconds() > self.silence_duration_threshold:
                event = ListeningEvent(
                    timestamp=current_time,
                    event_type="silence",
                    description=f"Environment became quiet (amplitude: {features['rms_energy']:.6f})",
                    audio_features=features,
                    severity="low"
                )
                events.append(event)
        
        # Check for amplitude changes (if baseline established)
        if self.baseline_amplitude is not None:
            amplitude_ratio = features['rms_energy'] / self.baseline_amplitude
            if amplitude_ratio > 2.0:  # 2x louder than baseline
                event = ListeningEvent(
                    timestamp=current_time,
                    event_type="amplitude_increase",
                    description=f"Significant volume increase ({amplitude_ratio:.1f}x baseline)",
                    audio_features=features,
                    severity="medium" if amplitude_ratio < 5.0 else "high",
                    audio_snippet=audio_chunk.copy() if self.record_events else None
                )
                events.append(event)
            elif amplitude_ratio < 0.3:  # Much quieter than baseline
                event = ListeningEvent(
                    timestamp=current_time,
                    event_type="amplitude_decrease",
                    description=f"Significant volume decrease ({amplitude_ratio:.1f}x baseline)",
                    audio_features=features,
                    severity="low",
                    audio_snippet=audio_chunk.copy() if self.record_events else None
                )
                events.append(event)
        
        # Check for frequency changes
        if self.baseline_frequency is not None and 'dominant_frequency' in features:
            freq_diff = abs(features['dominant_frequency'] - self.baseline_frequency)
            if freq_diff > self.frequency_change_threshold:
                event = ListeningEvent(
                    timestamp=current_time,
                    event_type="frequency_shift",
                    description=f"Frequency shift detected: {freq_diff:.1f} Hz from baseline",
                    audio_features=features,
                    severity="medium",
                    audio_snippet=audio_chunk.copy() if self.record_events else None
                )
                events.append(event)
        
        # Check for audio quality issues
        if anomalies.get('clipping_detected'):
            event = ListeningEvent(
                timestamp=current_time,
                event_type="clipping",
                description=f"Audio clipping detected ({anomalies['clipped_sample_ratio']:.4f} ratio)",
                audio_features=features,
                severity="high",
                audio_snippet=audio_chunk.copy() if self.record_events else None
            )
            events.append(event)
        
        # Check for unusual spectral characteristics
        if (self.baseline_spectral_centroid is not None and 
            abs(features['spectral_centroid_mean'] - self.baseline_spectral_centroid) > 1000):
            event = ListeningEvent(
                timestamp=current_time,
                event_type="spectral_change",
                description=f"Unusual spectral characteristics detected",
                audio_features=features,
                severity="medium",
                audio_snippet=audio_chunk.copy() if self.record_events else None
            )
            events.append(event)
        
        return events
    
    def _save_event_recording(self, event: ListeningEvent):
        """Save audio snippet of an event to file."""
        if not self.record_events or not self.recording_dir or event.audio_snippet is None:
            return
        
        timestamp_str = event.timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp_str}_{event.event_type}.wav"
        filepath = self.recording_dir / filename
        
        try:
            sf.write(filepath, event.audio_snippet, self.sample_rate)
            print(f"Event recording saved: {filepath}")
        except Exception as e:
            print(f"Error saving event recording: {e}")
    
    def _process_events(self, events: List[ListeningEvent]):
        """Process detected events (callbacks, recording, etc.)."""
        for event in events:
            # Add to events list
            self.events.append(event)
            
            # Save recording if enabled
            if self.record_events:
                self._save_event_recording(event)
            
            # Call event callbacks
            for callback in self.event_callbacks:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")
    
    async def start_listening(self, duration: Optional[float] = None):
        """Start listening session.
        
        Args:
            duration: Duration to listen in seconds (None for indefinite)
        """
        if not AUDIO_INPUT_AVAILABLE:
            raise RuntimeError("Audio input not available")
        
        if self.is_listening:
            raise RuntimeError("Already listening")
        
        print("Starting environmental listening session...")
        print(f"Sample Rate: {self.sample_rate} Hz")
        print(f"Chunk Duration: {self.chunk_duration} seconds")
        print(f"Device: {self.device if self.device is not None else 'Default'}")
        
        self.is_listening = True
        self.session_start_time = datetime.now()
        self.events.clear()
        
        try:
            # Start audio input stream
            with sd.InputStream(
                callback=self._audio_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.chunk_size,
                device=self.device
            ):
                print("Audio stream started. Listening...")
                
                # Establish baseline
                await asyncio.sleep(1)  # Wait for some data
                self._establish_baseline()
                
                print("Monitoring environment... Press Ctrl+C to stop")
                
                end_time = time.time() + duration if duration else None
                
                while self.is_listening:
                    if end_time and time.time() > end_time:
                        break
                    
                    try:
                        # Process audio chunks
                        audio_chunk, timestamp = self.audio_queue.get(timeout=0.1)
                        
                        # Analyze chunk for events
                        events = self._analyze_chunk(audio_chunk, timestamp)
                        
                        if events:
                            self._process_events(events)
                        
                    except queue.Empty:
                        continue
                    except KeyboardInterrupt:
                        break
                    
                    await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
                
        except Exception as e:
            print(f"Error during listening session: {e}")
        finally:
            self.is_listening = False
            print(f"\nListening session ended. Detected {len(self.events)} events.")
    
    def stop_listening(self):
        """Stop the current listening session."""
        self.is_listening = False
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of the listening session."""
        if not self.session_start_time:
            return {"error": "No session started"}
        
        session_duration = (datetime.now() - self.session_start_time).total_seconds()
        
        # Count events by type and severity
        event_types = {}
        event_severities = {}
        
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            event_severities[event.severity] = event_severities.get(event.severity, 0) + 1
        
        return {
            "session_start": self.session_start_time.isoformat(),
            "session_duration_seconds": session_duration,
            "total_events": len(self.events),
            "events_by_type": event_types,
            "events_by_severity": event_severities,
            "baseline_measurements": {
                "amplitude": self.baseline_amplitude,
                "frequency": self.baseline_frequency,
                "spectral_centroid": self.baseline_spectral_centroid
            } if self.baseline_amplitude else None
        }
    
    def export_session_data(self, output_file: str):
        """Export session data to JSON file."""
        session_data = {
            "summary": self.get_session_summary(),
            "events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "description": event.description,
                    "severity": event.severity,
                    "audio_features": event.audio_features
                }
                for event in self.events
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        print(f"Session data exported to: {output_file}")
    
    async def ask_about_session(self, question: str) -> str:
        """Ask AI agent about the listening session.
        
        Args:
            question: Question about the session
            
        Returns:
            AI agent's response
        """
        if not self.analyzer.agent_enabled:
            return "AI agent not available for session analysis"
        
        session_context = {
            "summary": self.get_session_summary(),
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "type": event.event_type,
                    "description": event.description,
                    "severity": event.severity
                }
                for event in self.events[-10:]  # Last 10 events
            ]
        }
        
        return await self.analyzer.ask(
            f"Based on this listening session data: {session_context}\n\nQuestion: {question}",
            session_context
        )