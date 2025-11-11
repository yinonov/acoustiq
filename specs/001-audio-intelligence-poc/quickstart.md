# Quickstart Guide: Audio Intelligence Tool

**Goal**: Get started with audio analysis in 5 minutes

This guide will walk you through installation, your first listening session, and AI-powered file analysis.

---

## Prerequisites

- **Python 3.8+** (check with `python3 --version`)
- **macOS, Linux, or Windows** with working audio input device
- **Optional**: GitHub Personal Access Token (free) for AI insights

---

## 1. Installation (2 minutes)

### Step 1: Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/audio-intelligence.git
cd audio-intelligence

# Install dependencies
pip install -e .
```

### Step 2: Verify Installation

```bash
audio-intelligence --version
```

Expected output:
```
Audio Intelligence Tool v1.0.0
```

### Step 3: Optional - Enable AI Features

For natural language insights, set up a GitHub token:

```bash
# 1. Generate token at: https://github.com/settings/tokens
#    Select scopes: None needed (models.inference.ai.azure.com is free-tier)

# 2. Set environment variable
export GITHUB_TOKEN="your_token_here"

# 3. Verify AI access (should not error)
python -c "from audio_intelligence.agent import AudioAgent; agent = AudioAgent(); print('AI ready!')"
```

**Note**: AI features are optional. The tool works without a token (raw analysis only).

---

## 2. Your First Listening Session (1 minute)

Let's monitor your environment for 30 seconds:

```bash
audio-intelligence listen --duration 30 --record-events
```

**What happens**:
1. Tool captures microphone input in 1-second chunks
2. First 10 seconds establish baseline (room tone)
3. Detects events: loud sounds, frequency shifts, silence
4. Saves 2-second audio clips of interesting events

**Output example**:
```
🎧 Listening Session Started
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[00:00:00-00:00:10] Establishing baseline...
Baseline RMS: 0.05, Centroid: 1500 Hz

[00:00:12] 🔊 VOLUME_INCREASE detected!
  Magnitude: 15.3 dB above baseline
  Recorded: event_001.wav

[00:00:30] Session complete!

Summary:
  Total Duration: 30.0 seconds
  Events Detected: 2
  Recordings Saved: 2 files in ./events/
```

**Try this**: Clap your hands or speak during the session to trigger events!

### Troubleshooting

**"Microphone permission denied"**:
- **macOS**: System Preferences → Security & Privacy → Microphone → Allow Terminal
- **Linux**: Check `pavucontrol` or `alsamixer` permissions
- **Windows**: Settings → Privacy → Microphone → Allow desktop apps

**"No audio device found"**:
```bash
# List available devices
audio-intelligence listen --list-devices

# Use specific device
audio-intelligence listen --device 1
```

---

## 3. Analyze an Audio File (1 minute)

### Step 1: Get a Sample File

Use one of the event recordings from the listening session:

```bash
audio-intelligence analyze --file events/event_001.wav
```

Or use your own WAV/MP3/FLAC file:

```bash
audio-intelligence analyze --file /path/to/your/recording.wav
```

### Step 2: View Results

**Output example**:
```
Audio Analysis: events/event_001.wav
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Basic Features:
  Duration: 2.0 seconds
  Sample Rate: 44100 Hz
  Channels: 1 (mono)
  RMS Energy: 0.45
  Peak Amplitude: 0.89
  Spectral Centroid: 2500.0 Hz

Anomalies Detected: 1
  ⚠️  Clipping (severity: 0.7)
      Time range: 0.5-0.8 seconds
      Audio samples near maximum amplitude detected

AI Insights:
  The recording captures a brief impact sound with high energy 
  in the mid-frequency range (2-4 kHz). The clipping suggests 
  the microphone gain was too high. Recommend reducing input 
  level by -6 dB to preserve dynamic range.

Analysis completed in 0.8 seconds
```

### Step 3: Export to JSON

```bash
audio-intelligence analyze --file events/event_001.wav --output results.json
```

View the JSON:
```bash
cat results.json | python -m json.tool
```

---

## 4. Interactive AI Mode (1 minute)

Ask questions about your audio:

```bash
audio-intelligence analyze --file events/event_001.wav --interactive
```

**Example conversation**:
```
Analysis complete. Enter 'help' for commands or ask a question.

> What caused the clipping?

AI: The clipping occurred because the audio signal exceeded the 
maximum recordable amplitude (±1.0). This typically happens when:
1. Microphone gain is too high
2. Sound source is too close to the microphone
3. Recording level is set incorrectly in the system

> How do I fix it?

AI: To prevent clipping in future recordings:
1. Reduce microphone input gain by 6-12 dB
2. Move microphone farther from sound source
3. Use a limiter/compressor if available
4. Monitor levels during recording (aim for -12 to -6 dBFS peaks)

> exit
```

**Interactive commands**:
- Ask any question about the audio
- `summary` - Re-display analysis
- `export <path>` - Export to JSON
- `help` - Show commands
- `exit` - Quit

---

## 5. Batch Processing (Optional)

Analyze multiple files at once:

```bash
audio-intelligence batch --files "events/*.wav" --output batch_results.json
```

---

## Quick Reference

### Common Commands

```bash
# Real-time monitoring (60 seconds, default)
audio-intelligence listen

# Long monitoring session (5 minutes)
audio-intelligence listen --duration 300

# Analyze file with AI insights
audio-intelligence analyze --file recording.wav

# Analyze without AI (faster)
audio-intelligence analyze --file recording.wav --no-ai

# Batch analysis
audio-intelligence batch --files "*.wav"

# Get help
audio-intelligence --help
audio-intelligence listen --help
audio-intelligence analyze --help
```

### Configuration

**Environment Variables**:
```bash
# AI features (optional)
export GITHUB_TOKEN="your_token_here"

# Default output directory
export AUDIO_INTELLIGENCE_OUTPUT_DIR="./my_events"

# Default audio device
export AUDIO_INTELLIGENCE_DEVICE=1

# Debug mode
export AUDIO_INTELLIGENCE_LOG_LEVEL=DEBUG
```

---

## What's Next?

### Customize Thresholds

```bash
# More sensitive detection
audio-intelligence listen --volume-threshold 5 --frequency-threshold 200

# Less sensitive (quieter environment)
audio-intelligence listen --volume-threshold 15 --frequency-threshold 800
```

### Adjust Chunk Size

```bash
# Faster updates (0.5s chunks)
audio-intelligence listen --chunk-size 0.5

# More stable baseline (2s chunks)
audio-intelligence listen --chunk-size 2.0
```

### Save Session Data

```bash
# All events go to specific directory
audio-intelligence listen --output-dir "./my_study_001" --record-events
```

This creates:
```
my_study_001/
├── event_001.wav
├── event_002.wav
├── event_003.wav
└── session_550e8400_summary.json
```

---

## Use Cases

**1. Acoustic Environment Studies**:
```bash
# Monitor office for 1 hour, save all events
audio-intelligence listen --duration 3600 --record-events --output-dir office_study
```

**2. Audio Quality Check**:
```bash
# Analyze recording, export report
audio-intelligence analyze -f interview.wav -o interview_qa.json

# Check for clipping, silence, or distortion in report
cat interview_qa.json | jq '.anomalies'
```

**3. Batch Validation**:
```bash
# Check 100 recordings for quality issues
audio-intelligence batch -f "recordings/*.wav" -o validation_report.json

# Filter for files with anomalies
cat validation_report.json | jq '.results[] | select(.anomalies | length > 0)'
```

---

## Troubleshooting

### Issue: Analysis takes too long

**Solution**: Disable AI features for faster processing:
```bash
audio-intelligence analyze --file large.wav --no-ai
```

### Issue: Out of memory

**Solution**: File too large (>2 GB unsupported in POC):
```bash
# Split file with ffmpeg
ffmpeg -i large.wav -f segment -segment_time 1800 -c copy part_%03d.wav

# Analyze parts
audio-intelligence batch --files "part_*.wav"
```

### Issue: AI insights not working

**Checklist**:
1. Token set? `echo $GITHUB_TOKEN`
2. Token valid? Test with: `curl -H "Authorization: Bearer $GITHUB_TOKEN" https://models.inference.ai.azure.com/chat/completions`
3. Quota exceeded? Wait or use new token

**Fallback**: Tool continues with raw analysis if AI unavailable.

---

## Performance Expectations

Based on Constitution success criteria:

- **Real-time latency**: <2 seconds from microphone input to event detection
- **File analysis**: <30 seconds for 10-minute recording
- **Sanity test suite**: <10 seconds total (runs automatically in CI)
- **Memory usage**: <2 GB RAM during analysis

---

## Getting Help

- **CLI help**: `audio-intelligence --help`
- **Command help**: `audio-intelligence <command> --help`
- **Issues**: See project README for contribution guidelines
- **Documentation**: Refer to `specs/001-audio-intelligence-poc/spec.md`

---

## POC Limitations

This is a **Proof of Concept** with focused scope:

✅ **Supported**:
- Real-time monitoring (single-threaded)
- File analysis (WAV, MP3, FLAC via librosa)
- AI natural language insights (optional)
- Basic anomaly detection (clipping, silence, transients)
- Local processing only (<1 KB feature vectors to AI)

❌ **Not Supported** (intentionally out of scope):
- Parallel batch processing
- Persistent database storage
- Multi-user or client-server deployment
- Advanced ML models (spectrograms, neural networks)
- Comprehensive test coverage (only sanity tests)

For production features, see `specs/001-audio-intelligence-poc/spec.md` (Future Scope).

---

**Congratulations!** You've completed the quickstart. You can now:
- ✅ Monitor live audio environments
- ✅ Analyze audio files for features and anomalies
- ✅ Get AI-powered insights and recommendations
- ✅ Export results for further analysis

For advanced usage, see the full specification or run `audio-intelligence --help`.
