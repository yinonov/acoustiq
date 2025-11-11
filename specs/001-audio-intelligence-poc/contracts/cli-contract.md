# CLI Contract: Audio Intelligence Tool

**Version**: 1.0.0  
**Date**: 2025-11-11  
**Type**: Command-Line Interface

## Overview

This document defines the command-line interface contract for the Audio Intelligence Tool. The tool provides three primary commands: `analyze` (file analysis), `listen` (real-time monitoring), and `batch` (multiple files).

## Global Options

Available for all commands:

```
--help, -h          Show help message and exit
--version, -v       Show version and exit
--quiet, -q         Suppress non-essential output
--verbose           Enable detailed logging
```

## Commands

### 1. analyze - Analyze Audio File

**Purpose**: Analyze a single audio file for features and anomalies

**Usage**:
```bash
audio-intelligence analyze --file <path> [options]
```

**Required Arguments**:
- `--file, -f PATH` - Path to audio file (WAV, MP3, FLAC)

**Optional Arguments**:
- `--output, -o PATH` - Export results to JSON file
- `--format {text|json}` - Output format (default: text)
- `--ai/--no-ai` - Enable/disable AI insights (default: auto-detect token)
- `--interactive, -i` - Enter interactive Q&A mode after analysis

**Output** (text format):
```
Audio Analysis: /path/to/file.wav
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Basic Features:
  Duration: 120.5 seconds
  Sample Rate: 48000 Hz
  Channels: 1 (mono)
  RMS Energy: 0.42
  Peak Amplitude: 0.89
  Spectral Centroid: 2500.0 Hz

Advanced Features:
  MFCCs: [13 coefficients]
  Chroma: [12 pitch classes]
  Spectral Contrast: [7 bands]

Anomalies Detected: 2
  ⚠️  Clipping (severity: 0.7)
      Time range: 45.2-47.8 seconds
      Audio samples near maximum amplitude detected

  ℹ️  Silence (severity: 0.3)
      Time range: 90.0-95.0 seconds
      Extended low-energy period

AI Insights:
  The recording shows typical speech characteristics with...
  [natural language summary]

Analysis completed in 2.3 seconds
```

**Output** (JSON format):
```json
{
  "file_path": "/path/to/file.wav",
  "duration_seconds": 120.5,
  "sample_rate": 48000,
  "channels": 1,
  "basic_features": {
    "rms_energy": 0.42,
    "peak_amplitude": 0.89,
    "spectral_centroid": 2500.0,
    "zero_crossing_rate": 0.15
  },
  "advanced_features": {
    "mfccs": [...],
    "chroma": [...],
    "spectral_contrast": [...],
    "spectral_rolloff": 8000.0,
    "spectral_bandwidth": 2500.0
  },
  "anomalies": [
    {
      "type": "CLIPPING",
      "severity": 0.7,
      "time_range": [45.2, 47.8],
      "description": "Audio samples near maximum amplitude detected"
    }
  ],
  "ai_insights": "The recording shows...",
  "analysis_time_seconds": 2.3,
  "timestamp": "2025-11-11T14:30:00Z"
}
```

**Exit Codes**:
- `0` - Success
- `1` - File not found or unreadable
- `2` - File format not supported
- `3` - File too large (>2GB)
- `4` - Analysis error

**Examples**:
```bash
# Basic analysis
audio-intelligence analyze --file recording.wav

# Export to JSON
audio-intelligence analyze -f recording.wav -o results.json

# Interactive mode with AI
audio-intelligence analyze -f recording.wav --interactive

# Quiet mode for scripting
audio-intelligence analyze -f recording.wav --quiet --format json
```

---

### 2. listen - Real-Time Environmental Monitoring

**Purpose**: Monitor live microphone input and detect acoustic events

**Usage**:
```bash
audio-intelligence listen [options]
```

**Optional Arguments**:
- `--duration, -d SECONDS` - How long to listen (default: 60)
- `--output-dir, -o PATH` - Directory for event recordings (default: ./events)
- `--record-events` - Save 2-second audio clips of detected events
- `--volume-threshold FLOAT` - Volume change threshold in dB (default: 10.0)
- `--frequency-threshold FLOAT` - Frequency shift threshold in Hz (default: 500.0)
- `--chunk-size FLOAT` - Audio chunk duration in seconds (default: 1.0, range: 0.5-2.0)
- `--device INT` - Audio input device index (default: system default)
- `--list-devices` - Show available audio devices and exit

**Output** (live updates):
```
🎧 Listening Session Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Configuration:
  Duration: 60 seconds
  Sample Rate: 44100 Hz
  Chunk Size: 1.0 second
  Volume Threshold: 10 dB
  Frequency Threshold: 500 Hz
  Recording: Enabled (./events/)

[00:00:00-00:00:10] Establishing baseline...
Baseline RMS: 0.05, Centroid: 1500 Hz

[00:00:12] 🔊 VOLUME_INCREASE detected!
  Magnitude: 15.3 dB above baseline
  RMS Energy: 0.45
  Recorded: event_001.wav

[00:00:18] 📊 FREQUENCY_SHIFT detected!
  Frequency range: 2000-4000 Hz
  Spectral Centroid: 3200 Hz
  Recorded: event_002.wav

[00:00:60] Session complete!

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Duration: 60.0 seconds
  Chunks Processed: 60
  Events Detected: 5
    - VOLUME_INCREASE: 2
    - VOLUME_DECREASE: 1
    - FREQUENCY_SHIFT: 2
  Recordings Saved: 5 files in ./events/
  Session ID: 550e8400-e29b-41d4-a716-446655440000

Session summary saved: events/session_550e8400_summary.json
```

**Exit Codes**:
- `0` - Success
- `1` - No audio device available
- `2` - Microphone permission denied
- `3` - Audio device error during capture
- `4` - Keyboard interrupt (Ctrl+C) - graceful shutdown

**Examples**:
```bash
# Basic 60-second session
audio-intelligence listen

# 5-minute session with event recording
audio-intelligence listen --duration 300 --record-events

# Custom thresholds for sensitive environment
audio-intelligence listen -d 120 --volume-threshold 5 --frequency-threshold 200

# List available audio devices
audio-intelligence listen --list-devices
```

---

### 3. batch - Analyze Multiple Files

**Purpose**: Process multiple audio files sequentially

**Usage**:
```bash
audio-intelligence batch --files <pattern> [options]
```

**Required Arguments**:
- `--files, -f PATTERN` - File pattern (glob) or space-separated paths

**Optional Arguments**:
- `--output, -o PATH` - Export aggregated results to JSON file
- `--format {text|json}` - Output format (default: text)
- `--continue-on-error` - Skip corrupted files, continue processing (default: true)
- `--parallel` - Process files in parallel (NOT IMPLEMENTED in POC)

**Output** (text format):
```
Batch Analysis: 3 files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1/3] recording_001.wav
  ✓ Analyzed in 1.2s
  Duration: 45.2s, RMS: 0.35
  Anomalies: 1 (clipping)

[2/3] recording_002.wav
  ✗ Error: File format not supported (unsupported.xyz)
  Skipping...

[3/3] recording_003.wav
  ✓ Analyzed in 2.1s
  Duration: 120.5s, RMS: 0.42
  Anomalies: 0

Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Files: 3
  Successful: 2
  Failed: 1
  Total Duration: 165.7 seconds
  Average RMS: 0.385
  Total Anomalies: 1

Results exported: batch_results.json
```

**Exit Codes**:
- `0` - All files processed successfully
- `1` - Some files failed (with --continue-on-error)
- `2` - All files failed
- `3` - No files matched pattern

**Examples**:
```bash
# Analyze all WAV files in directory
audio-intelligence batch --files "*.wav"

# Multiple specific files
audio-intelligence batch -f "file1.wav file2.wav file3.wav"

# Export results to JSON
audio-intelligence batch -f "recordings/*.wav" -o batch_results.json
```

---

## Environment Variables

The tool respects the following environment variables:

- `GITHUB_TOKEN` - GitHub Personal Access Token for AI features (optional)
- `AUDIO_INTELLIGENCE_OUTPUT_DIR` - Default output directory for recordings
- `AUDIO_INTELLIGENCE_DEVICE` - Default audio input device index
- `AUDIO_INTELLIGENCE_LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Messages

### Common Error Patterns

**Microphone Permission Denied**:
```
❌ Error: Microphone permission denied

To grant microphone access:
  • macOS: System Preferences → Security & Privacy → Microphone
  • Linux: Check PulseAudio/ALSA permissions
  • Windows: Settings → Privacy → Microphone

After granting permission, restart the application.
```

**File Too Large**:
```
❌ Error: File exceeds maximum size limit

File: recording.wav (3.5 GB)
Limit: 2.0 GB

Suggestion: Split file into smaller chunks:
  ffmpeg -i recording.wav -f segment -segment_time 1800 -c copy output%03d.wav
```

**AI Token Invalid**:
```
⚠️  Warning: AI features unavailable

GitHub token is invalid or quota exceeded.

To enable AI insights:
  1. Generate token: https://github.com/settings/tokens
  2. Set token: export GITHUB_TOKEN="your_token_here"
  3. Restart analysis

Continuing with raw analysis features...
```

**Corrupted File**:
```
❌ Error: Unable to read audio file

File: recording.wav
Reason: File appears corrupted or format unsupported

Supported formats: WAV, MP3 (requires ffmpeg), FLAC
```

## Interactive Mode

When `--interactive` flag is used with `analyze`, the tool enters Q&A mode:

```
Analysis complete. Enter 'help' for commands or ask a question.

> What frequency ranges show the most energy?

AI: The frequency analysis shows dominant energy in the 1-3 kHz range, 
typical of human speech. The 4-6 kHz presence band is also elevated, 
suggesting good vocal clarity. Low frequencies (<200 Hz) are minimal.

> Suggest what to investigate

AI: Based on the detected clipping at 45-48 seconds, I recommend:
1. Check microphone gain settings
2. Review recording levels during that time period
3. Consider re-recording with -6dB headroom

> exit

Exiting interactive mode. Goodbye!
```

**Interactive Commands**:
- `help` - Show available commands
- `summary` - Re-display analysis summary
- `export <path>` - Export current analysis to JSON
- `exit` / `quit` - Exit interactive mode

## Version Information

```bash
$ audio-intelligence --version
Audio Intelligence Tool v1.0.0
Python: 3.11.5
librosa: 0.10.1
sounddevice: 0.4.6
```

## Sanity Test Coverage

The CLI interface is tested with:
- `test_cli_imports()` - Verify all commands discoverable
- `test_cli_help()` - Ensure --help works for all commands
- Manual smoke test: `audio-intelligence analyze --file test.wav` completes successfully

No comprehensive CLI integration tests per Constitution Principle III (Sanity Tests Only).

## Notes

- All timestamps in output use ISO 8601 format with timezone
- Progress indicators use rich library for terminal formatting
- JSON output always includes schema version for compatibility
- Commands designed to be pipeline-friendly (stdin/stdout separation)
