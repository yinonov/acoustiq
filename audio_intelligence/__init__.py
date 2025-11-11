"""
Audio Intelligence Tool
A smart tool for acoustic measurement engineers using AI agents and local processing.
"""

from .analyzer import AudioAnalyzer
from .agent import AcousticAgent

# Listener has optional dependencies (sounddevice requires PortAudio)
try:
    from .listener import EnvironmentListener, ListeningEvent
    _LISTENER_AVAILABLE = True
except (ImportError, OSError):
    _LISTENER_AVAILABLE = False
    EnvironmentListener = None
    ListeningEvent = None

__version__ = "0.1.0"
__all__ = ["AudioAnalyzer", "AcousticAgent", "EnvironmentListener", "ListeningEvent"]