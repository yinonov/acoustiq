# Data Model: Audio Intelligence Tool POC

**Feature**: Audio Intelligence Tool POC  
**Date**: 2025-11-11  
**Purpose**: Define entities, relationships, and state management

## Overview

The system manages four primary entities for audio analysis and monitoring. All data is stored locally (no database) - in-memory during processing, optionally persisted to filesystem as WAV files (recordings) and JSON files (session summaries).

## Core Entities

### 1. Listening Session

**Purpose**: Represents a real-time monitoring period with detected events

**Attributes**:
- `session_id`: str (UUID) - Unique identifier
- `start_time`: datetime - Session start timestamp
- `end_time`: datetime | None - Session end timestamp (None if active)
- `duration_seconds`: float - Total duration
- `sample_rate`: int - Audio sample rate (Hz)
- `chunk_size`: int - Audio chunk size in samples
- `baseline_rms`: float - Baseline RMS energy level
- `baseline_centroid`: float - Baseline spectral centroid
- `volume_threshold`: float - Detection threshold for volume changes (dB)
- `frequency_threshold`: float - Detection threshold for frequency shifts (Hz)
- `recording_enabled`: bool - Whether event clips are saved
- `output_directory`: Path | None - Where event recordings saved
- `events`: List[AcousticEvent] - Detected events during session
- `total_events`: int - Count of detected events
- `chunk_count`: int - Total audio chunks processed

**Relationships**:
- One-to-many with AcousticEvent (session contains multiple events)

**State Transitions**:
1. INITIALIZING → Baseline calculation (first 10 chunks)
2. MONITORING → Active event detection
3. COMPLETED → Session ended, summary generated

**Validation Rules**:
- `sample_rate` must be > 0 (typically 16000-48000)
- `chunk_size` must correspond to 0.5-2 seconds of audio
- `volume_threshold` typically 5-20 dB
- `frequency_threshold` typically 100-1000 Hz
- `baseline_*` computed from first 10 chunks

**Persistence**:
- In-memory during session
- Optionally saved as `session_{id}_summary.json` on completion
- JSON format includes all attributes + event list

### 2. Acoustic Event

**Purpose**: Represents a detected occurrence during listening

**Attributes**:
- `event_id`: str (UUID) - Unique identifier
- `session_id`: str - Parent session reference
- `timestamp`: datetime - When event detected
- `relative_time`: float - Seconds since session start
- `event_type`: EventType - Classification of event
- `magnitude`: float - Event intensity/strength
- `frequency_range`: Tuple[float, float] | None - (min_hz, max_hz) if frequency-related
- `rms_energy`: float - RMS energy at event time
- `spectral_centroid`: float - Spectral centroid at event time
- `audio_clip_path`: Path | None - Reference to saved 2s WAV file if recorded
- `metadata`: Dict[str, Any] - Additional event-specific data

**EventType Enum**:
- `VOLUME_INCREASE` - Sudden volume spike
- `VOLUME_DECREASE` - Sudden volume drop
- `FREQUENCY_SHIFT` - Significant frequency content change
- `CLIPPING` - Audio clipping detected
- `SPECTRAL_ANOMALY` - Unusual frequency distribution
- `SILENCE` - Extended silence period

**Relationships**:
- Many-to-one with ListeningSession (event belongs to one session)
- Optional reference to audio clip file on disk

**Validation Rules**:
- `magnitude` must be > 0
- `frequency_range[0]` < `frequency_range[1]` if present
- `relative_time` >= 0
- `audio_clip_path` must exist if specified

**Persistence**:
- In-memory in session's event list
- Included in session summary JSON
- Optional 2-second audio clip as `event_{id}.wav` file

### 3. Audio Analysis Result

**Purpose**: Output of file analysis with extracted features and anomalies

**Attributes**:
- `file_path`: Path - Source audio file
- `file_size_bytes`: int - File size for validation
- `duration_seconds`: float - Audio duration
- `sample_rate`: int - Audio sample rate
- `channels`: int - Mono (1) or stereo (2)
- `basic_features`: BasicFeatures - Simple metrics
- `advanced_features`: AdvancedFeatures - Detailed analysis
- `anomalies`: List[Anomaly] - Detected issues
- `ai_insights`: str | None - AI-generated analysis (if available)
- `analysis_time_seconds`: float - Processing duration
- `timestamp`: datetime - When analysis performed

**BasicFeatures**:
- `rms_energy`: float - Root mean square energy
- `peak_amplitude`: float - Maximum amplitude value
- `frequency_spectrum`: np.ndarray - FFT magnitude spectrum
- `spectral_centroid`: float - Center of mass of spectrum
- `zero_crossing_rate`: float - Rate of sign changes

**AdvancedFeatures**:
- `mfccs`: np.ndarray - Mel-frequency cepstral coefficients (13 coefficients)
- `chroma`: np.ndarray - Chromagram (12 pitch classes)
- `spectral_contrast`: np.ndarray - Spectral valley-peak contrast
- `spectral_rolloff`: float - Frequency below which 85% of energy concentrated
- `spectral_bandwidth`: float - Weighted std of frequencies

**Anomaly**:
- `type`: AnomalyType - Classification
- `severity`: float - 0.0-1.0 scale
- `time_range`: Tuple[float, float] - (start_sec, end_sec)
- `description`: str - Human-readable explanation

**AnomalyType Enum**:
- `CLIPPING` - Samples near ±1.0
- `DC_OFFSET` - Non-zero mean
- `SILENCE` - Extended low-energy periods
- `DYNAMIC_RANGE_LOW` - Compressed dynamic range
- `DYNAMIC_RANGE_HIGH` - Unusual amplitude variation

**Relationships**:
- References source file on disk
- Optionally references AI agent for insights

**Validation Rules**:
- `file_size_bytes` must match actual file size
- `duration_seconds` > 0
- `channels` in [1, 2]
- `sample_rate` typically 8000-96000
- File must exist and be readable

**Persistence**:
- Not persisted by default (computed on-demand)
- Optionally exported as JSON via `--output` flag
- AI insights cached in-memory for interactive session

### 4. Feature Vector

**Purpose**: Compact representation for AI analysis (<1KB)

**Attributes**:
- `source_type`: SourceType - Whether from file or session
- `source_id`: str - File path or session ID
- `summary_stats`: SummaryStats - Aggregate metrics
- `frequency_bands`: np.ndarray - Energy in standard bands (8 bands)
- `temporal_pattern`: TemporalPattern - Time-domain characteristics
- `size_bytes`: int - Actual size for validation (<1024)

**SummaryStats**:
- `mean_rms`: float - Average energy
- `std_rms`: float - Energy standard deviation
- `peak_rms`: float - Maximum energy
- `mean_centroid`: float - Average spectral centroid
- `std_centroid`: float - Centroid standard deviation

**Frequency Bands** (energy in each):
- Sub-bass: 20-60 Hz
- Bass: 60-250 Hz
- Low-mid: 250-500 Hz
- Mid: 500-2000 Hz
- High-mid: 2000-4000 Hz
- Presence: 4000-6000 Hz
- Brilliance: 6000-20000 Hz
- Air: 20000+ Hz (if sample rate supports)

**TemporalPattern**:
- `attack_rate`: float - How quickly sound emerges
- `sustain_level`: float - Average sustained level
- `decay_rate`: float - How quickly sound fades
- `event_density`: float - Events per second

**Relationships**:
- Derived from Audio Analysis Result or Listening Session
- Sent to AI Agent (not persisted locally)

**Validation Rules**:
- `size_bytes` MUST be < 1024 (hard requirement from spec)
- All floats must be finite (no NaN/Inf)
- `frequency_bands` length = 8

**Persistence**:
- Never persisted locally (ephemeral for AI calls)
- Transmitted via HTTPS to GitHub Models API
- Discarded after AI response received

## Relationships Diagram

```
ListeningSession (1) ----< (N) AcousticEvent
      |
      | (has optional audio clips on disk)
      v
  WAV files (event_{id}.wav)

AudioAnalysisResult
      |
      | (references)
      v
  Audio File (on disk)
      |
      | (optionally analyzed by)
      v
  AI Agent ← receives ← FeatureVector (derived from Result or Session)
```

## Data Flow

### Real-Time Listening (P1)
1. Create ListeningSession with configuration
2. Capture audio chunk (sounddevice callback)
3. Compute baseline (first 10 chunks)
4. For each subsequent chunk:
   - Extract features (RMS, centroid)
   - Compare to baseline + thresholds
   - If threshold exceeded → Create AcousticEvent
   - Fire callback with event
   - Optionally save 2s audio clip to disk
5. On session end → Generate summary JSON

### File Analysis (P2)
1. Validate file exists and size < 2GB
2. Load audio with librosa
3. Create AudioAnalysisResult
4. Extract BasicFeatures (RMS, spectrum, centroid)
5. Extract AdvancedFeatures (MFCCs, chroma)
6. Detect anomalies → Create Anomaly objects
7. Display results in terminal
8. Optionally export to JSON

### AI Insights (P3)
1. From AudioAnalysisResult or ListeningSession
2. Create FeatureVector (compress to <1KB)
3. Send to AI Agent via GitHub Models API
4. Receive natural language insights
5. Display or return to user
6. If AI fails → gracefully return None, continue

## State Management

**In-Memory State**:
- Active ListeningSession during real-time monitoring
- Current AudioAnalysisResult during file analysis
- AI agent instance (singleton, reused across queries)

**Disk State**:
- Audio recordings: `{output_dir}/event_{id}.wav` (2-second clips)
- Session summaries: `{output_dir}/session_{id}_summary.json`
- Analysis exports: `{output_path}` (JSON format)

**No Database Required**: All state is ephemeral or file-based per Constitution Principle II (Local Processing Only)

## Validation & Constraints

### File Size Limits
- Maximum file size: 2GB (FR-022)
- Check before loading to prevent OOM
- Display clear error with splitting suggestion

### Memory Constraints
- Audio chunks: Released after processing (no accumulation)
- Event list: Grows with events but metadata only (~100 bytes/event)
- Feature vectors: <1KB guaranteed
- Expected memory: <100MB typical, <2GB maximum (SC-004)

### Data Integrity
- All file paths validated before access
- Sample rates validated (typically 8kHz-96kHz)
- Float values checked for NaN/Inf
- JSON export includes schema version for future compatibility

## Example Data Structures

### Listening Session Summary JSON
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_time": "2025-11-11T14:30:00Z",
  "end_time": "2025-11-11T14:31:00Z",
  "duration_seconds": 60.0,
  "sample_rate": 44100,
  "total_events": 5,
  "events": [
    {
      "event_id": "...",
      "timestamp": "2025-11-11T14:30:15Z",
      "event_type": "VOLUME_INCREASE",
      "magnitude": 15.3,
      "frequency_range": null,
      "audio_clip_path": "event_....wav"
    }
  ]
}
```

### Analysis Result JSON
```json
{
  "file_path": "/path/to/recording.wav",
  "duration_seconds": 120.5,
  "sample_rate": 48000,
  "channels": 1,
  "basic_features": {
    "rms_energy": 0.42,
    "peak_amplitude": 0.89,
    "spectral_centroid": 2500.0
  },
  "anomalies": [
    {
      "type": "CLIPPING",
      "severity": 0.7,
      "time_range": [45.2, 47.8],
      "description": "Audio clipping detected in 2.6 second range"
    }
  ]
}
```

## Schema Version

**Current Version**: 1.0.0

Future changes will increment version and maintain backward compatibility for JSON import/export.
