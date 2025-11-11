# Research: Audio Intelligence Tool POC

**Feature**: Audio Intelligence Tool POC  
**Date**: 2025-11-11  
**Purpose**: Resolve technical unknowns and validate technology choices

## Research Tasks Completed

### 1. Audio Processing Library Selection

**Decision**: Use librosa for audio analysis

**Rationale**:

- Industry standard for audio feature extraction
- Supports all required formats (WAV, MP3, FLAC)
- Efficient RMS energy, spectral centroid, MFCC computation
- Well-documented with extensive examples
- Works entirely locally (no cloud dependencies)
- Active maintenance and community support

**Alternatives Considered**:

- **pydub**: Too basic, lacks advanced feature extraction
- **aubio**: Good for onset detection but less comprehensive for spectral features
- **essentia**: Powerful but heavier dependency, overkill for POC

**Best Practices**:

- Load audio with `librosa.load()` with sr=None to preserve original sample rate
- Process in chunks for real-time (use `sounddevice` for capture, librosa for analysis)
- Use `librosa.feature.*` for extracting MFCCs, chroma, spectral features
- Cache sample rate and duration to avoid reloading

### 2. Real-Time Audio Capture

**Decision**: Use sounddevice for microphone input

**Rationale**:

- Cross-platform (macOS/Linux/Windows)
- Low-latency callback-based streaming
- Easy integration with numpy arrays
- Mature library with good error handling
- Supports configurable chunk sizes (0.5-2s requirement)

**Alternatives Considered**:

- **pyaudio**: Older, less maintained, platform-specific issues
- **portaudio directly**: Too low-level for POC
- **wave module**: File I/O only, no real-time capture

**Best Practices**:

- Use `sounddevice.InputStream` with callback function
- Set blocksize to achieve 0.5-2s chunks (e.g., 44100 * 1.0 for 1-second at 44.1kHz)
- Process chunks in callback to avoid blocking
- Use queue for thread-safe event handling
- Detect device permissions early with try/except on stream creation

### 3. AI Agent Framework

**Decision**: Use Microsoft Agent Framework (preview) with GitHub Models

**Rationale**:

- Designed for agentic workflows (tools, function calling)
- Free tier via GitHub Models (no credit card required)
- Supports phi-4-mini-instruct (fast, small model suitable for POC)
- Simple tool registration pattern
- Graceful degradation possible (optional import)

**Alternatives Considered**:

- **LangChain**: Heavier, more complex for single-agent POC
- **Direct OpenAI SDK**: No agent framework, would need custom tool handling
- **Anthropic Claude**: No free tier, additional cost

**Best Practices**:

- Import agent framework conditionally (try/except) for graceful degradation
- Keep tool functions simple (analyze features, not raw audio)
- Pass only extracted feature vectors (<1KB) to agent
- Set reasonable timeouts (5s for AI responses per SC-010)
- Cache agent instance, don't recreate for each query

### 4. Event Detection Algorithms

**Decision**: Threshold-based detection with configurable parameters

**Rationale**:

- Simple, fast, interpretable for POC
- Engineers can adjust thresholds based on environment
- No ML training required (POC constraint)
- Reliable for obvious events (loud sounds, frequency shifts)
- Aligns with 90%+ accuracy goal for obvious events (SC-002)

**Approach**:

- **Volume change**: Compare RMS energy to baseline + threshold (>10dB default)
- **Frequency shift**: Compare spectral centroid to baseline + threshold
- **Clipping**: Detect samples near ±1.0 (e.g., >0.99)
- **Spectral anomaly**: Detect unusual frequency band energy distributions

**Best Practices**:

- Establish baseline from first 10 chunks (configurable)
- Use exponential moving average for baseline adaptation
- Make all thresholds configurable via CLI args
- Fire callbacks immediately when threshold exceeded (<2s latency)
- Store event metadata (timestamp, magnitude, frequency range)

### 5. Memory Management for Long Sessions

**Decision**: Process-and-release pattern with explicit buffer cleanup

**Rationale**:

- Prevents memory accumulation over hours
- Simple to implement (no complex streaming architecture)
- Aligns with assumptions (minutes to hours, not days)
- Python GC handles released references automatically

**Implementation Strategy**:

- Process each audio chunk in callback
- Extract features and detect events immediately
- Release chunk buffer after processing (no accumulation)
- Store only event metadata (timestamps, types) not raw audio
- Optionally save 2-second event clips as separate WAV files
- Use generator pattern for batch file processing

**Best Practices**:

- Don't store entire audio stream in memory
- Use numpy views where possible (avoid copies)
- Clear event lists periodically if session is very long
- Monitor memory usage in sanity tests (basic check)

### 6. Error Handling Patterns

**Decision**: Fail-fast with clear error messages and remediation steps

**Rationale**:

- Aligns with POC-first philosophy (simple, clear)
- Better UX than silent failures
- Enables self-service troubleshooting
- Follows CLI best practices

**Patterns by Error Type**:

- **Missing permissions**: Check before starting, display OS-specific fix instructions
- **Corrupted files**: Validate format early, skip in batch mode with warning
- **Large files**: Check size before loading, suggest splitting at 2GB limit
- **AI token invalid**: Try AI call, catch error, display token setup instructions, continue without AI
- **No audio device**: Enumerate devices, show available options, exit gracefully

**Best Practices**:

- Use rich/click for formatted terminal output
- Include actionable steps in every error message
- Exit with appropriate codes (0=success, 1=user error, 2=system error)
- Log errors to stderr, results to stdout (for piping)

### 7. File Format Support

**Decision**: Support WAV, MP3, FLAC via librosa

**Rationale**:

- Covers 95%+ of acoustic measurement scenarios
- librosa handles format detection automatically
- No additional dependencies needed
- Falls back to soundfile for robust WAV support

**Format Handling**:

- **WAV**: Native support via soundfile (preferred format)
- **MP3**: Supported via audioread backend (requires ffmpeg/gstreamer on system)
- **FLAC**: Supported via soundfile
- **Others**: Graceful error with format not supported message

**Best Practices**:

- Let librosa auto-detect format (don't force based on extension)
- Validate format in try/except, provide clear error on unsupported
- Document ffmpeg requirement for MP3 in README
- Suggest WAV conversion for unsupported formats

### 8. CLI Design

**Decision**: Use click framework with subcommands

**Rationale**:

- Industry standard for Python CLIs
- Clean subcommand pattern (analyze, listen, batch)
- Automatic help generation
- Decorators keep code clean
- Good integration with rich for output formatting

**Command Structure**:

```bash
audio-intelligence analyze --file <path> [--output json]
audio-intelligence listen --duration <seconds> [--record-events] [--output-dir <dir>]
audio-intelligence batch --files <pattern> [--output <path>]
```

**Best Practices**:

- Use click.Path for file validation
- Provide --help for all commands and options
- Use rich.console for colored terminal output
- Support --quiet flag for automation
- Output JSON for scripting, rich tables for humans

### 9. Configuration Management

**Decision**: Environment variables + CLI arguments only

**Rationale**:

- Aligns with Constitution (no YAML/JSON config files)
- 12-factor app principles
- Simple to test and document
- Works in containers/CI if needed later

**Configuration Sources** (priority order):

1. CLI arguments (highest priority)
2. Environment variables (GITHUB_TOKEN, etc.)
3. Hardcoded defaults in code

**Best Practices**:

- Prefix env vars with AUDIO_INTELLIGENCE_ for namespacing
- Use sensible defaults (10dB volume threshold, 1s chunks, etc.)
- Document all env vars in README
- Validate at startup, fail fast with clear message

### 10. Testing Strategy

**Decision**: Sanity tests only using pytest

**Rationale**:

- Aligns with Constitution Principle III
- Fast feedback (<10s total)
- Catches regressions without testing theater
- Simple to maintain

**Test Coverage** (7 tests planned):

1. test_analyzer_loads() - Module imports without errors
2. test_analyzer_basic_workflow() - Analyze test file end-to-end
3. test_feature_extraction() - Basic features present in output
4. test_anomaly_detection() - Detects clipping in test file
5. test_listener_loads() - Real-time module imports
6. test_agent_loads_without_token() - AI gracefully degrades
7. test_cli_imports() - CLI commands discoverable

**Best Practices**:

- Use pytest fixtures for test audio files (generated sine waves)
- Mock AI calls to avoid network dependency
- Test happy path only (no edge case coverage)
- Each test <2 seconds
- Run with `pytest audio_intelligence/test_sanity.py -v`

## Technology Stack Summary

**Core Dependencies**:

- librosa >= 0.10.0 (audio analysis)
- soundfile >= 0.12.0 (audio I/O)
- sounddevice >= 0.4.6 (real-time capture)
- numpy >= 1.24.0 (numerical computation)
- scipy >= 1.10.0 (signal processing)

**Optional Dependencies**:

- agent-framework-azure-ai (preview) (AI agent)
- openai >= 1.0.0 (GitHub Models client)
- click >= 8.1.0 (CLI framework)
- rich >= 13.0.0 (terminal formatting)

**Development Dependencies**:

- pytest >= 7.4.0 (testing framework)

**System Requirements**:

- Python 3.8+
- FFmpeg/GStreamer (for MP3 support, optional)
- Standard audio drivers (CoreAudio/ALSA/WASAPI)

## Implementation Risks & Mitigations

### Risk 1: Real-time latency exceeds 2s target

**Mitigation**: Use callback-based processing, avoid blocking operations in audio thread, profile with cProfile if needed, use smaller chunk sizes if necessary

### Risk 2: Memory accumulation in long sessions

**Mitigation**: Explicit buffer release, test with 1-hour session in sanity tests, monitor memory usage, document session restart recommendation

### Risk 3: AI service unavailable/rate limited

**Mitigation**: Optional import with try/except, graceful degradation to raw analysis, clear error messages, document free tier limits

### Risk 4: Platform-specific audio issues

**Mitigation**: Test on macOS/Linux/Windows, document known issues, provide OS-specific troubleshooting, use sounddevice (cross-platform)

### Risk 5: Large file OOM crashes

**Mitigation**: Pre-check file size, 2GB hard limit, clear error with splitting suggestion, document memory requirements

## Open Questions

None - all technical unknowns resolved. Ready for Phase 1 (Design & Contracts).
