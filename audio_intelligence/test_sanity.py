"""
Sanity Tests for Audio Intelligence Tool
These are NOT comprehensive tests - just smoke tests to catch regressions.
Each test should run in < 2 seconds.
"""

import asyncio
import numpy as np
import tempfile
from pathlib import Path

# Generate a test audio file
def create_test_audio(filepath: str, duration: float = 1.0, sample_rate: int = 22050):
    """Create a simple test audio file."""
    try:
        import soundfile as sf
        
        # Generate simple sine wave
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)  # A4 note
        
        sf.write(filepath, audio, sample_rate)
        return True
    except ImportError:
        print("⚠️  soundfile not available - skipping audio generation")
        return False


def test_analyzer_loads():
    """Sanity: AudioAnalyzer can be imported and initialized."""
    try:
        from audio_intelligence import AudioAnalyzer
        analyzer = AudioAnalyzer(agent_enabled=False)
        assert analyzer is not None
        print("✅ Analyzer loads successfully")
        return True
    except Exception as e:
        print(f"❌ Analyzer failed to load: {e}")
        return False


def test_analyzer_basic_workflow():
    """Sanity: Analyzer can process a test audio file end-to-end."""
    try:
        from audio_intelligence import AudioAnalyzer
        
        # Create temp test file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            test_file = tmp.name
        
        if not create_test_audio(test_file):
            print("⚠️  Skipping analyzer workflow test - no soundfile")
            return True
        
        try:
            analyzer = AudioAnalyzer(agent_enabled=False)
            results = asyncio.run(analyzer.analyze_file(test_file, include_advanced=False))
            
            # Basic sanity checks
            assert "basic_features" in results
            assert "anomalies" in results
            assert results["basic_features"]["duration"] > 0
            assert results["basic_features"]["sample_rate"] > 0
            
            print("✅ Analyzer workflow works end-to-end")
            return True
        finally:
            Path(test_file).unlink(missing_ok=True)
            
    except Exception as e:
        print(f"❌ Analyzer workflow failed: {e}")
        return False


def test_listener_loads():
    """Sanity: EnvironmentListener can be imported and initialized."""
    try:
        from audio_intelligence import EnvironmentListener
        
        # Just test import and init (no actual listening)
        listener = EnvironmentListener(agent_enabled=False)
        assert listener is not None
        assert listener.sample_rate > 0
        
        print("✅ Listener loads successfully")
        return True
    except ImportError as e:
        print(f"⚠️  Listener dependencies not available: {e}")
        return True  # Not a failure if deps aren't installed
    except Exception as e:
        print(f"❌ Listener failed to load: {e}")
        return False


def test_agent_loads_without_token():
    """Sanity: Agent code doesn't crash on import even without GITHUB_TOKEN."""
    try:
        from audio_intelligence import AcousticAgent
        
        # Should import fine (will fail on init without token, which is expected)
        print("✅ Agent module loads successfully")
        return True
    except Exception as e:
        print(f"❌ Agent failed to load: {e}")
        return False


def test_cli_imports():
    """Sanity: CLI code can be imported without errors."""
    try:
        from audio_intelligence.cli import cli
        
        # Just verify it imports (don't run commands)
        assert cli is not None
        print("✅ CLI imports successfully")
        return True
    except ImportError as e:
        print(f"⚠️  CLI dependencies not available (click/rich): {e}")
        return True  # Not a failure if optional deps aren't installed
    except Exception as e:
        print(f"❌ CLI failed to import: {e}")
        return False


def test_feature_extraction():
    """Sanity: Feature extraction produces expected outputs."""
    try:
        from audio_intelligence import AudioAnalyzer
        
        # Create simple test audio in memory
        sample_rate = 22050
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        analyzer = AudioAnalyzer(agent_enabled=False)
        features = analyzer.extract_basic_features(audio, sample_rate)
        
        # Verify expected keys exist
        required_keys = ['duration', 'sample_rate', 'rms_energy', 'spectral_centroid_mean']
        for key in required_keys:
            assert key in features, f"Missing feature: {key}"
        
        # Verify values are reasonable
        assert features['duration'] > 0
        assert features['sample_rate'] == sample_rate
        assert features['rms_energy'] > 0
        
        print("✅ Feature extraction produces valid output")
        return True
    except Exception as e:
        print(f"❌ Feature extraction failed: {e}")
        return False


def test_anomaly_detection():
    """Sanity: Anomaly detection runs without errors."""
    try:
        from audio_intelligence import AudioAnalyzer
        
        # Create test audio with some anomalies
        sample_rate = 22050
        audio = np.random.normal(0, 0.1, sample_rate)  # 1 second of noise
        
        analyzer = AudioAnalyzer(agent_enabled=False)
        anomalies = analyzer.detect_anomalies(audio, sample_rate)
        
        # Verify expected keys
        required_keys = ['clipping_detected', 'silence_ratio', 'dc_offset', 'dynamic_range_db']
        for key in required_keys:
            assert key in anomalies, f"Missing anomaly metric: {key}"
        
        print("✅ Anomaly detection works")
        return True
    except Exception as e:
        print(f"❌ Anomaly detection failed: {e}")
        return False


def run_all_sanity_tests():
    """Run all sanity tests and report results."""
    print("\n" + "="*60)
    print("🧪 Running Audio Intelligence Sanity Tests")
    print("="*60 + "\n")
    
    tests = [
        test_analyzer_loads,
        test_analyzer_basic_workflow,
        test_feature_extraction,
        test_anomaly_detection,
        test_listener_loads,
        test_agent_loads_without_token,
        test_cli_imports,
    ]
    
    results = []
    for test in tests:
        print(f"\nRunning: {test.__name__}")
        print("-" * 40)
        results.append(test())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ ALL SANITY TESTS PASSED ({passed}/{total})")
        print("="*60 + "\n")
        return True
    else:
        print(f"❌ SOME TESTS FAILED ({passed}/{total} passed)")
        print("="*60 + "\n")
        return False


if __name__ == "__main__":
    import sys
    success = run_all_sanity_tests()
    sys.exit(0 if success else 1)