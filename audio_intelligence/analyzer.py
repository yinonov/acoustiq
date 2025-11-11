"""
Local Audio Processing and Analysis
Handles audio file processing, feature extraction, and speckit integration.
"""

import numpy as np
import librosa
import soundfile as sf
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

# Will integrate speckit once installed
# import speckit

from .agent import AcousticAgent


class AudioAnalyzer:
    """Main audio analysis class combining local processing with AI insights."""
    
    def __init__(self, agent_enabled: bool = True):
        """Initialize the audio analyzer.
        
        Args:
            agent_enabled: Whether to enable AI agent for intelligent analysis
        """
        self.agent_enabled = agent_enabled
        self.agent = None
        
        if agent_enabled:
            try:
                self.agent = AcousticAgent()
            except Exception as e:
                logging.warning(f"Could not initialize AI agent: {e}")
                self.agent_enabled = False
    
    def load_audio(self, file_path: str, sr: Optional[int] = None) -> Tuple[np.ndarray, int]:
        """Load audio file locally.
        
        Args:
            file_path: Path to audio file
            sr: Target sample rate (None for original)
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Load audio using librosa
        audio_data, sample_rate = librosa.load(file_path, sr=sr)
        
        return audio_data, sample_rate
    
    def extract_basic_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract basic audio features locally.
        
        Args:
            audio_data: Audio signal array
            sr: Sample rate
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        # Basic signal properties
        features['duration'] = len(audio_data) / sr
        features['sample_rate'] = sr
        features['num_samples'] = len(audio_data)
        features['rms_energy'] = float(np.sqrt(np.mean(audio_data**2)))
        features['max_amplitude'] = float(np.max(np.abs(audio_data)))
        
        # Spectral features
        stft = librosa.stft(audio_data)
        magnitude = np.abs(stft)
        
        # Spectral centroid (brightness)
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroid))
        features['spectral_centroid_std'] = float(np.std(spectral_centroid))
        
        # Spectral rolloff
        spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sr)[0]
        features['spectral_rolloff_mean'] = float(np.mean(spectral_rolloff))
        
        # Zero crossing rate
        zcr = librosa.feature.zero_crossing_rate(audio_data)[0]
        features['zero_crossing_rate_mean'] = float(np.mean(zcr))
        
        # Frequency domain analysis
        fft = np.fft.fft(audio_data)
        frequencies = np.fft.fftfreq(len(fft), 1/sr)
        magnitude_spectrum = np.abs(fft)
        
        # Find dominant frequency
        dominant_freq_idx = np.argmax(magnitude_spectrum[:len(magnitude_spectrum)//2])
        features['dominant_frequency'] = float(frequencies[dominant_freq_idx])
        
        # Frequency range with significant energy (above 10% of max)
        threshold = 0.1 * np.max(magnitude_spectrum)
        significant_freqs = frequencies[magnitude_spectrum > threshold]
        if len(significant_freqs) > 0:
            features['frequency_range_min'] = float(np.min(significant_freqs[significant_freqs >= 0]))
            features['frequency_range_max'] = float(np.max(significant_freqs[significant_freqs >= 0]))
        
        return features
    
    def extract_advanced_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract advanced acoustic features using librosa.
        
        Args:
            audio_data: Audio signal array
            sr: Sample rate
            
        Returns:
            Dictionary of advanced features
        """
        features = {}
        
        # MFCC features (for pattern recognition)
        mfccs = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=13)
        for i in range(13):
            features[f'mfcc_{i}_mean'] = float(np.mean(mfccs[i]))
            features[f'mfcc_{i}_std'] = float(np.std(mfccs[i]))
        
        # Chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=sr)
        features['chroma_mean'] = float(np.mean(chroma))
        features['chroma_std'] = float(np.std(chroma))
        
        # Spectral contrast
        contrast = librosa.feature.spectral_contrast(y=audio_data, sr=sr)
        features['spectral_contrast_mean'] = float(np.mean(contrast))
        features['spectral_contrast_std'] = float(np.std(contrast))
        
        # Tonnetz (tonal centroid features)
        tonnetz = librosa.feature.tonnetz(y=audio_data, sr=sr)
        features['tonnetz_mean'] = float(np.mean(tonnetz))
        features['tonnetz_std'] = float(np.std(tonnetz))
        
        return features
    
    def detect_anomalies(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Detect potential anomalies in audio signal.
        
        Args:
            audio_data: Audio signal array
            sr: Sample rate
            
        Returns:
            Dictionary of anomaly detection results
        """
        anomalies = {}
        
        # Check for clipping
        clipping_threshold = 0.95
        clipped_samples = np.sum(np.abs(audio_data) > clipping_threshold)
        anomalies['clipping_detected'] = clipped_samples > 0
        anomalies['clipped_sample_ratio'] = float(clipped_samples / len(audio_data))
        
        # Check for silence
        silence_threshold = 0.01
        silent_samples = np.sum(np.abs(audio_data) < silence_threshold)
        anomalies['silence_ratio'] = float(silent_samples / len(audio_data))
        anomalies['excessive_silence'] = anomalies['silence_ratio'] > 0.5
        
        # Check for DC offset
        dc_offset = np.mean(audio_data)
        anomalies['dc_offset'] = float(dc_offset)
        anomalies['significant_dc_offset'] = abs(dc_offset) > 0.1
        
        # Dynamic range analysis
        dynamic_range = 20 * np.log10(np.max(np.abs(audio_data)) / (np.mean(np.abs(audio_data)) + 1e-10))
        anomalies['dynamic_range_db'] = float(dynamic_range)
        anomalies['low_dynamic_range'] = dynamic_range < 10  # Less than 10 dB
        
        return anomalies
    
    async def analyze_file(self, file_path: str, include_advanced: bool = True) -> Dict[str, Any]:
        """Analyze an audio file completely.
        
        Args:
            file_path: Path to audio file
            include_advanced: Whether to include advanced feature extraction
            
        Returns:
            Complete analysis results
        """
        # Load audio locally
        audio_data, sr = self.load_audio(file_path)
        
        # Extract features locally
        basic_features = self.extract_basic_features(audio_data, sr)
        anomalies = self.detect_anomalies(audio_data, sr)
        
        results = {
            'file_path': file_path,
            'basic_features': basic_features,
            'anomalies': anomalies
        }
        
        if include_advanced:
            advanced_features = self.extract_advanced_features(audio_data, sr)
            results['advanced_features'] = advanced_features
        
        # If AI agent is enabled, get intelligent insights
        if self.agent_enabled and self.agent:
            try:
                # Combine features for AI analysis
                all_features = {**basic_features, **anomalies}
                if include_advanced:
                    all_features.update(results['advanced_features'])
                
                ai_insights = await self.agent.analyze_audio_features(all_features)
                results['ai_insights'] = ai_insights
            except Exception as e:
                logging.warning(f"Could not get AI insights: {e}")
                results['ai_insights'] = "AI analysis unavailable"
        
        return results
    
    async def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Ask a question about audio analysis.
        
        Args:
            question: Natural language question
            context: Optional context from previous analysis
            
        Returns:
            Answer to the question
        """
        if not self.agent_enabled or not self.agent:
            return "AI agent not available. Please enable AI features or check your GitHub token."
        
        try:
            return await self.agent.answer_question(question, context)
        except Exception as e:
            return f"Could not process question: {e}"
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get basic information about an audio file without loading it entirely.
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Basic file information
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Get file info using soundfile (faster than loading entire file)
        info = sf.info(file_path)
        
        return {
            'file_name': file_path.name,
            'file_size_bytes': file_path.stat().st_size,
            'duration_seconds': info.frames / info.samplerate,
            'sample_rate': info.samplerate,
            'channels': info.channels,
            'format': info.format,
            'subtype': info.subtype,
            'frames': info.frames
        }