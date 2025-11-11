# Audio Intelligence Tool

A smart tool to help Acoustic Measurement Engineers analyze audio data efficiently with real-time monitoring, local file analysis, and optional AI-powered insights.

## 🚀 Quick Start (5 minutes)

### 1. Install

```bash
# Clone and install
git clone <repository-url>
cd audio-intelligence
pip install -e .
```

### 2. First Listening Session

```bash
# Monitor your environment for 30 seconds
audio-intelligence listen --duration 30 --record-events
```

Make some sounds (clap, speak, whistle) and watch events get detected in real-time!

### 3. Analyze an Audio File

```bash
# Analyze any WAV/MP3/FLAC file
audio-intelligence analyze --file your_recording.wav
```

### 4. Enable AI Insights (Optional)

```bash
# Set up GitHub token for AI features
export GITHUB_TOKEN="your_github_token"

# Analyze with AI insights
audio-intelligence analyze --file recording.wav --interactive
```

## 📚 Complete Guide

For detailed documentation, see **[Quickstart Guide](specs/001-audio-intelligence-poc/quickstart.md)** which includes:

- Complete installation walkthrough
- Real-time monitoring tutorial
- File analysis examples
- Interactive AI mode
- Batch processing
- Troubleshooting
- Configuration options

## ✨ Features

- 🎧 **Real-Time Monitoring**: Detect acoustic events as they happen (<2s latency)
- 📁 **File Analysis**: Process WAV/MP3/FLAC files locally (no upload)
- 🤖 **AI Insights**: Natural language Q&A about audio characteristics
- 🎯 **Event Detection**: Automatic detection of volume changes, frequency shifts, clipping
- 💾 **Local Processing**: All audio stays on your machine (privacy-first)
- 🚀 **Fast Setup**: Working in 5 minutes from clone to first analysis

## 🏗️ Architecture

**Simple by Design**:

- Single Python package
- No databases (filesystem only)
- No web framework (terminal UI)
- Optional AI (graceful degradation)

**Philosophy**: POC-First - Working features > Perfect architecture

## 📋 Requirements

- Python 3.8+
- Standard audio hardware (microphone, sound card)
- Optional: GitHub Personal Access Token (for AI features)

## 🛠️ Development

See the [Implementation Plan](specs/001-audio-intelligence-poc/plan.md) and [Tasks](specs/001-audio-intelligence-poc/tasks.md) for development guidelines.

Built with ❤️ following the [Constitution](.specify/memory/constitution.md)
