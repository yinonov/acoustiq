#!/usr/bin/env python3
"""
Quick sanity check script - run this before committing code.
Should complete in < 10 seconds.
"""

import sys

print("\n🧪 Audio Intelligence - Quick Sanity Check")
print("="*60)

# Check if dependencies are installed
try:
    import numpy
    import scipy
    print("✅ numpy, scipy installed")
except ImportError as e:
    print(f"❌ Missing core dependencies: {e}")
    print("\nInstall with: pip install -r requirements.txt")
    sys.exit(1)

try:
    import librosa
    import soundfile
    print("✅ librosa, soundfile installed")
except ImportError as e:
    print(f"❌ Missing audio dependencies: {e}")
    print("\nInstall with: pip install librosa soundfile")
    sys.exit(1)

# Now run the actual sanity tests
try:
    from audio_intelligence.test_sanity import run_all_sanity_tests
    success = run_all_sanity_tests()
    sys.exit(0 if success else 1)
except Exception as e:
    print(f"\n❌ Error running sanity tests: {e}")
    print("\nMake sure you're in the project root directory")
    sys.exit(1)