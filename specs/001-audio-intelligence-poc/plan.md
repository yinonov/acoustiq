# Implementation Plan: Audio Intelligence Tool POC

**Branch**: `001-audio-intelligence-poc` | **Date**: 2025-11-11 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-audio-intelligence-poc/spec.md`

**Note**: This plan follows the POC-first constitution principles: working features > perfect architecture, sanity tests only, local processing only.

## Summary

Build a smart audio analysis tool for Acoustic Measurement Engineers featuring **real-time environmental monitoring** (P1), **local file analysis** (P2), and **optional AI insights** (P3). Core value proposition: reduce audio review time by 80% through real-time event detection instead of post-hoc file analysis. All audio processing happens locally (privacy-first), with chunk-based architecture (0.5-2s chunks) for immediate feedback. System degrades gracefully when AI unavailable. Single Python package, terminal UI, sanity tests only (<10s total).

## Technical Context

**Language/Version**: Python 3.8+  
**Primary Dependencies**: librosa (audio analysis), soundfile (I/O), sounddevice (real-time input), numpy/scipy (computation), agent-framework-azure-ai (optional AI), click/rich (CLI)  
**Storage**: Local filesystem only - no databases, event recordings saved as WAV files, session summaries as JSON  
**Testing**: pytest with sanity tests only (<10s total, single test_sanity.py file, happy path coverage)  
**Target Platform**: macOS/Linux/Windows with Python 3.8+, standard audio hardware (microphone, sound card)  
**Project Type**: Single Python package (audio_intelligence/) - no microservices, no web framework  
**Performance Goals**: <2s event detection latency, <30s file analysis for typical recordings (10-60min), <10s sanity test suite  
**Constraints**: <2GB RAM for 1GB files, local-only processing (no audio upload), graceful AI degradation, 2GB file size limit  
**Scale/Scope**: Single-user POC, no multi-user/collaboration, terminal-only UI, 3 user stories (P1: real-time, P2: files, P3: AI)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: POC-First Development ✅ PASS

- ✅ Feature can be demoed in <1 hour (real-time listening with test sounds)
- ✅ Single Python package (audio_intelligence/) - no microservices
- ✅ Direct processing without abstraction layers
- ✅ Simple functions over complex class hierarchies planned
- ✅ Working POC prioritized over perfect architecture

### Principle II: Local Processing Only ✅ PASS

- ✅ No cloud dependencies for audio processing
- ✅ All audio analysis happens locally (librosa, sounddevice)
- ✅ No databases or cloud storage required
- ✅ Only tiny feature vectors (<1KB) sent to optional AI
- ✅ Raw audio never uploaded

### Principle III: Sanity Tests Only ✅ PASS

- ✅ Single test_sanity.py file planned
- ✅ One test per feature (7 tests total)
- ✅ <10 second total runtime target
- ✅ Happy path coverage only
- ✅ No comprehensive test suites

### Principle IV: Real-Time First ✅ PASS

- ✅ Real-time monitoring is P1 (PRIMARY use case)
- ✅ Chunk-based processing (0.5-2 second chunks)
- ✅ Event callbacks for immediate feedback
- ✅ File analysis is P2 (SECONDARY)
- ✅ Configurable thresholds

### Principle V: AI Agent as Assistant ✅ PASS

- ✅ AI features are P3 (OPTIONAL)
- ✅ Graceful degradation when AI unavailable (FR-015, FR-023)
- ✅ Single agent, no orchestration
- ✅ AI analyzes features, not raw audio
- ✅ System works without AI

**Overall Assessment**: ✅ ALL GATES PASS - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
audio_intelligence/              # Single Python package
├── __init__.py                  # Package exports (AudioAnalyzer, AudioAgent, EnvironmentListener)
├── analyzer.py                  # File analysis engine (P2)
├── listener.py                  # Real-time monitoring (P1)  
├── agent.py                     # AI agent integration (P3)
├── cli/                         # Command-line interface
│   └── __init__.py             # Commands: analyze, listen, batch
└── test_sanity.py              # Single sanity test file (<10s total)

Supporting files:
├── requirements.txt             # Dependencies list
├── setup.py                     # Package installation
├── README.md                    # Quick start guide
├── GETTING_STARTED.md          # Detailed usage docs
├── demo_listening.py           # Quick demo script
└── run_sanity_tests.py         # Test runner
```

**Structure Decision**: Single project structure selected per Constitution Principle I (POC-First, Single Package). No backend/frontend split, no microservices. Flat hierarchy with analyzer.py, listener.py, agent.py as peer modules. Tests collocated in single test_sanity.py file per Principle III. Structure already exists in repository - this plan documents and extends it.

## Complexity Tracking

> No constitution violations - all principles pass. No justification needed.

---

## Phase 1: Design & Contracts Summary

**Status**: ✅ COMPLETE

**Artifacts Created**:

1. ✅ `research.md` (Phase 0) - Technology research and validation
   - 10 research tasks (library selection, real-time capture, AI framework, event detection, memory management, error handling, file formats, CLI design, configuration, testing)
   - Technology stack decisions with rationale and alternatives
   - 5 implementation risks with mitigations

2. ✅ `data-model.md` (Phase 1) - Core entity definitions
   - 4 core entities: ListeningSession, AcousticEvent, AudioAnalysisResult, FeatureVector
   - Entity relationships and data flow diagrams
   - Validation rules and example JSON structures
   - Storage strategy: in-memory during processing, optional filesystem persistence

3. ✅ `contracts/cli-contract.md` (Phase 1) - Command-line interface specification
   - 3 primary commands: analyze (file), listen (real-time), batch (multiple files)
   - Global options, arguments, output formats (text/JSON)
   - Error messages and exit codes
   - Interactive mode specification

4. ✅ `quickstart.md` (Phase 1) - User onboarding guide
   - 5-minute installation walkthrough
   - First listening session tutorial
   - First file analysis tutorial
   - Interactive AI mode examples
   - Troubleshooting and configuration reference

5. ✅ Agent context updated - `.github/copilot-instructions.md`
   - Technologies: Python 3.8+, librosa, sounddevice, soundfile, numpy, scipy, Agent Framework, click/rich
   - Database: Local filesystem only (no databases)
   - Project type: Single Python package

**Design Decisions**:

- **Data Model**: All entities in-memory during processing, no persistent database (aligns with Principle I: POC-First)
- **CLI Contract**: Terminal-only interface with rich formatting, no web UI (aligns with Principle I: POC-First)
- **Event Storage**: Optional WAV file recording for events, JSON summaries for sessions (aligns with Principle II: Local Processing)
- **Error Handling**: Fail-fast with clear user instructions (microphone permissions, file errors, AI failures)
- **AI Integration**: Optional, graceful degradation pattern (aligns with Principle V: AI as Assistant)

**Key Architecture Insights**:

- **Chunk-Based Processing**: 0.5-2 second audio chunks for real-time feedback (<2s latency requirement)
- **Baseline Calibration**: First 10 seconds establish environmental baseline for anomaly detection
- **Memory Management**: Process-and-release pattern to handle large files within 2GB RAM constraint
- **Feature Vector Size**: <1KB per analysis (enables AI processing without uploading raw audio)
- **Single Package Design**: Flat hierarchy with analyzer/listener/agent as peer modules (no layers)

**Constitution Re-Check** (Post-Design):

- ✅ Principle I (POC-First): Single package, no layers, direct processing confirmed
- ✅ Principle II (Local Processing): No audio upload, only feature vectors to AI confirmed
- ✅ Principle III (Sanity Tests): test_sanity.py approach maintained
- ✅ Principle IV (Real-Time First): Chunk architecture supports <2s latency
- ✅ Principle V (AI Assistant): Graceful degradation designed (FR-015, FR-023)

**Next Steps**: Run `/speckit.tasks` to generate task breakdown from this plan.

---

## Notes

- **POC Scope**: This is a proof-of-concept with focused scope. Advanced features (parallel batch processing, persistent database, multi-user deployment) intentionally excluded per Constitution Principle I.
- **Performance Targets**: All latency/throughput requirements validated in research.md against library benchmarks.
- **Test Strategy**: Sanity tests only (<10s total) per Constitution Principle III - no comprehensive test suites.
- **AI Dependency**: Optional GitHub Models (phi-4-mini-instruct) via Agent Framework, free tier sufficient for POC usage patterns.
