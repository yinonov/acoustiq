# Tasks: Audio Intelligence Tool POC

**Input**: Design documents from `/specs/001-audio-intelligence-poc/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli-contract.md

**Tests**: Sanity tests only per Constitution Principle III (<10s total, happy path coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Single Python package structure at repository root:

- `audio_intelligence/` - Main package
- `audio_intelligence/cli/` - Command-line interface
- Supporting files at root level

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create audio_intelligence/ package directory structure with **init**.py
- [ ] T002 Create requirements.txt with dependencies: librosa>=0.10.0, soundfile>=0.12.0, sounddevice>=0.4.6, numpy>=1.24.0, scipy>=1.10.0, agent-framework-azure-ai, click>=8.1.0, rich>=13.0.0, pytest>=7.4.0
- [ ] T003 Create setup.py for package installation with entry point for audio-intelligence CLI command
- [ ] T004 [P] Create README.md with quick start guide based on quickstart.md
- [ ] T005 [P] Create GETTING_STARTED.md with detailed usage documentation
- [ ] T006 [P] Create .gitignore for Python project (venv/, **pycache**/, *.pyc, events/,*.wav)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T007 Create audio_intelligence/**init**.py with package exports (AudioAnalyzer, EnvironmentListener, AudioAgent)
- [ ] T008 Create audio_intelligence/cli/**init**.py with Click group and main() entry point
- [ ] T009 [P] Create data model classes in audio_intelligence/models.py: ListeningSession, AcousticEvent, AudioAnalysisResult, FeatureVector with all attributes from data-model.md. Use Python dataclasses (@dataclass decorator) with type hints for attributes only, no business logic methods (POC-first approach)
- [ ] T010 [P] Create audio_intelligence/utils.py with helper functions: validate_file_size, check_audio_device_permissions, format_error_message
- [ ] T011 Create audio_intelligence/config.py for configuration management: environment variables (GITHUB_TOKEN, AUDIO_INTELLIGENCE_OUTPUT_DIR, AUDIO_INTELLIGENCE_DEVICE, AUDIO_INTELLIGENCE_LOG_LEVEL), default values

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Real-Time Environmental Monitoring (Priority: P1) 🎯 MVP

**Goal**: Monitor live environmental sounds and detect acoustic events in real-time with <2s latency

**Independent Test**: Start listening session, generate test sounds (clap, whistle), verify events detected within 2 seconds

### Sanity Test for User Story 1

> **NOTE: Write this test FIRST, ensure it FAILS before implementation**

- [ ] T012 [US1] Create audio_intelligence/test_sanity.py with test_listener_imports() to verify EnvironmentListener module loads without errors

### Implementation for User Story 1

- [ ] T013 [P] [US1] Create audio_intelligence/listener.py with EnvironmentListener class skeleton: **init**, start_session, stop_session,_audio_callback methods
- [ ] T014 [US1] Implement baseline calibration in EnvironmentListener._establish_baseline() using first 10 audio chunks to compute baseline RMS and spectral centroid
- [ ] T015 [US1] Implement real-time audio capture in EnvironmentListener.start_session() using sounddevice.InputStream with configurable chunk size (0.5-2s), sample rate detection, callback registration
- [ ] T016 [US1] Implement event detection in EnvironmentListener._audio_callback(): extract RMS energy and spectral centroid using librosa, compare to baseline values from T014 using dB difference for RMS and Hz difference for centroid, check against configurable thresholds
- [ ] T017 [US1] Implement event creation and callback in EnvironmentListener._detect_events(): create AcousticEvent objects for VOLUME_INCREASE, VOLUME_DECREASE, FREQUENCY_SHIFT with timestamps and magnitude
- [ ] T018 [US1] Implement optional event recording in EnvironmentListener._save_event_clip(): save 2-second WAV clips to output directory when recording_enabled=True
- [ ] T019 [US1] Implement session summary generation in EnvironmentListener.stop_session(): aggregate events by type, save session JSON summary with all session metadata
- [ ] T020 [US1] Implement listen command in audio_intelligence/cli/**init**.py: parse CLI arguments (duration, output-dir, record-events, volume-threshold, frequency-threshold, chunk-size, device, list-devices), create EnvironmentListener, display live updates using rich console
- [ ] T021 [US1] Add error handling for missing microphone permissions (FR-019): check device availability before starting session, display actionable error message with OS-specific instructions
- [ ] T022 [US1] Add memory management in EnvironmentListener._audio_callback(): explicitly release chunk buffers after processing to prevent memory accumulation (FR-021)
- [ ] T023 [US1] Update test_sanity.py with test_listener_basic_workflow(): mock sounddevice, create listener, simulate baseline and event detection with synthetic audio chunks

**Checkpoint**: At this point, User Story 1 should be fully functional - engineer can start listening session and see real-time event detection

---

## Phase 4: User Story 2 - File Analysis Without Upload (Priority: P2)

**Goal**: Analyze existing audio files for features and anomalies entirely on local machine

**Independent Test**: Provide test WAV file, run analysis command, verify results displayed within 30 seconds without network activity

### Sanity Test for User Story 2

- [ ] T024 [P] [US2] Add test_analyzer_imports() to test_sanity.py to verify AudioAnalyzer module loads
- [ ] T025 [P] [US2] Add test_analyzer_basic_workflow() to test_sanity.py: create test WAV file (1s sine wave using scipy.io.wavfile), run analyzer, verify AudioAnalysisResult returned with basic features

### Implementation for User Story 2

- [ ] T026 [P] [US2] Create audio_intelligence/analyzer.py with AudioAnalyzer class skeleton: **init**, analyze_file, _extract_basic_features,_extract_advanced_features, _detect_anomalies methods
- [ ] T027 [US2] Implement file validation in AudioAnalyzer.analyze_file(): check file exists, check file size < 2GB (FR-022), validate format (WAV/MP3/FLAC) using librosa, display clear error for unsupported formats (FR-020)
- [ ] T028 [US2] Implement basic feature extraction in AudioAnalyzer._extract_basic_features(): load audio with librosa.load(sr=None), compute RMS energy, peak amplitude, frequency spectrum (FFT), spectral centroid, zero crossing rate
- [ ] T029 [US2] Implement advanced feature extraction in AudioAnalyzer._extract_advanced_features(): compute MFCCs (13 coefficients), chroma features (12 pitch classes), spectral contrast (7 bands), spectral rolloff, spectral bandwidth using librosa.feature.*
- [ ] T030 [US2] Implement anomaly detection in AudioAnalyzer._detect_anomalies(): detect CLIPPING (samples > 0.99), DC_OFFSET (non-zero mean), SILENCE (extended low RMS periods), DYNAMIC_RANGE_LOW/HIGH, create Anomaly objects with type, severity, time range, description
- [ ] T031 [US2] Implement memory-efficient processing in AudioAnalyzer.analyze_file(): use process-and-release pattern for large files, avoid storing entire audio in memory after processing
- [ ] T032 [US2] Implement analyze command in audio_intelligence/cli/**init**.py: parse CLI arguments (file, output, format, ai/no-ai, interactive), create AudioAnalyzer, display results using rich tables for text format or JSON export
- [ ] T033 [US2] Implement batch command in audio_intelligence/cli/**init**.py: parse file pattern/glob, iterate files, call analyzer for each, handle corrupted files with continue-on-error (FR-020), display aggregated summary
- [ ] T034 [US2] Add test_feature_extraction() to test_sanity.py: verify basic features present in output (rms_energy, spectral_centroid, peak_amplitude)
- [ ] T035 [US2] Add test_anomaly_detection() to test_sanity.py: create test file with clipping (samples at 1.0), run analyzer, verify CLIPPING anomaly detected

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - engineer can analyze files OR monitor real-time

---

## Phase 5: User Story 3 - AI-Powered Insights (Priority: P3)

**Goal**: Provide natural language insights about audio characteristics using AI agent (optional, graceful degradation)

**Independent Test**: Analyze audio file, ask "What frequency ranges show the most energy?", verify AI provides relevant answer OR system continues working if AI unavailable

### Sanity Test for User Story 3

- [ ] T036 [US3] Add test_agent_loads_without_token() to test_sanity.py: verify AI agent module imports and gracefully handles missing GITHUB_TOKEN (FR-015, FR-023)

### Implementation for User Story 3

- [ ] T037 [P] [US3] Create audio_intelligence/agent.py with AudioAgent class skeleton: **init**, analyze_features, interactive_session,_create_feature_vector methods
- [ ] T038 [US3] Implement feature vector creation in AudioAgent._create_feature_vector(): compress AudioAnalysisResult or ListeningSession to FeatureVector with SummaryStats, 8 frequency bands, TemporalPattern, ensure size < 1KB (FR-014)
- [ ] T039 [US3] Implement AI integration in AudioAgent.**init**(): conditional import of agent-framework-azure-ai with try/except for graceful degradation, initialize with GITHUB_TOKEN from environment, use phi-4-mini-instruct model via GitHub Models endpoint
- [ ] T040 [US3] Implement AI analysis in AudioAgent.analyze_features(): create FeatureVector from analysis result, send to AI agent with prompt "Analyze these audio features and provide insights", handle API errors (invalid token, quota exceeded) with warning message (FR-023), return insights string or None
- [ ] T041 [US3] Implement interactive mode in AudioAgent.interactive_session(): create REPL loop, accept user questions, query AI agent with context (analysis results + question), display AI responses, support commands (help, summary, export, exit/quit)
- [ ] T042 [US3] Integrate AI insights into analyze command: call AudioAgent.analyze_features() after analysis, display AI insights section in terminal output, handle graceful degradation when AI unavailable
- [ ] T043 [US3] Implement --interactive flag in analyze command: enter AudioAgent.interactive_session() after displaying results, allow Q&A about the analyzed audio
- [ ] T044 [US3] Add AI summary to listen command: after session ends, create FeatureVector from session events, call AudioAgent for summary, display "Acoustic Activity Summary" if AI available
- [ ] T045 [US3] Add error handling for AI token issues: detect AuthenticationError or rate limit errors, display warning with remediation steps (token generation URL, export GITHUB_TOKEN command), continue with raw analysis

**Checkpoint**: All user stories should now be independently functional - full POC complete with optional AI enhancement

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T046 [P] Add global CLI options in audio_intelligence/cli/**init**.py: --help, --version (display version + Python + librosa + sounddevice versions), --quiet (suppress non-essential output), --verbose (enable DEBUG logging)
- [ ] T047 [P] Implement rich terminal formatting across all CLI commands: use rich.console for progress indicators, use rich.table for structured output, use rich.panel for sections, add emoji icons for event types
- [ ] T048 [P] Add comprehensive error messages for all failure modes: format_error_message utility for consistent styling, include remediation steps for common issues (permissions, file size, AI token, corrupted files)
- [ ] T049 [P] Create demo_listening.py at repository root: simple script demonstrating listening session with event detection, can be run for quick demo (< 1 minute)
- [ ] T050 [P] Create run_sanity_tests.py at repository root: convenience script to run pytest audio_intelligence/test_sanity.py with timing validation
- [ ] T051 Finalize test_sanity.py: ensure 7 tests total (test_listener_imports, test_listener_basic_workflow, test_analyzer_imports, test_analyzer_basic_workflow, test_feature_extraction, test_anomaly_detection, test_agent_loads_without_token), verify <10s total runtime, add docstrings explaining happy path coverage
- [ ] T052 Add JSON export functionality: implement --output flag for analyze and batch commands, include schema version in JSON, ensure ISO 8601 timestamps, validate JSON structure
- [ ] T053 Add logging configuration in audio_intelligence/config.py: use standard logging module, respect AUDIO_INTELLIGENCE_LOG_LEVEL env var, log to stderr for errors, log to stdout for results
- [ ] T054 Validate quickstart.md by running through all examples: installation via pip install -e ., first listening session, first file analysis, interactive mode, batch processing, verify all examples work
- [ ] T055 Add exit codes to CLI commands: 0=success, 1=user error (file not found, invalid args), 2=system error (no device, permission denied), 3=data error (file too large, corrupted), 4=AI error (token invalid)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion
  - User stories CAN proceed in parallel (if team capacity allows)
  - Or sequentially in priority order: US1 (P1) → US2 (P2) → US3 (P3)
- **Polish (Phase 6)**: Depends on desired user stories being complete (at minimum US1 for MVP)

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - **No dependencies on other stories** - This is the MVP
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - **No dependencies on US1** - Independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - **Integrates with US1 and US2** but degrades gracefully if they're not present

### Within Each User Story

- Sanity tests MUST be written FIRST and FAIL before implementation
- Models/data structures (from Phase 2) before services
- Core implementation before CLI integration
- Error handling and validation throughout
- Story complete before moving to next priority

### Parallel Opportunities

**Phase 1 (Setup)**: Can run in parallel:

- T004 (README.md), T005 (GETTING_STARTED.md), T006 (.gitignore)

**Phase 2 (Foundational)**: Can run in parallel:

- T009 (models.py) and T010 (utils.py) - different files

**Phase 3 (User Story 1)**: Within the story:

- T013 (listener.py skeleton) must complete first
- Then T014-T019 have some dependencies (baseline before detection, detection before recording)
- T020-T022 (CLI integration and error handling) can start once core listener works
- T012 (test) and T023 (test update) can be written anytime

**Phase 4 (User Story 2)**: Can run in parallel:

- T024, T025 (tests) - independent
- T026 (analyzer.py skeleton) must complete first
- T027-T031 (analysis implementation) have some sequential dependencies
- T032-T033 (CLI commands) once analyzer works
- T034-T035 (more tests) anytime

**Phase 5 (User Story 3)**: Can run in parallel:

- T036 (test) - independent
- T037 (agent.py skeleton) must complete first
- T038-T041 (agent implementation) mostly sequential
- T042-T045 (integration) once agent works

**Phase 6 (Polish)**: Most tasks can run in parallel:

- T046, T047, T048, T049, T050, T052, T053 - all different concerns
- T051 (finalize tests), T054 (validate quickstart), T055 (exit codes) - slightly dependent on earlier work

**User Story Parallelization**: If multiple developers available:

- Developer A: Complete US1 (T012-T023) - Real-time monitoring MVP
- Developer B: Complete US2 (T024-T035) - File analysis (can start after Phase 2)
- Developer C: Complete US3 (T036-T045) - AI insights (can start after Phase 2)

---

## Parallel Example: User Story 1

```bash
# After T013 (listener skeleton) completes:

# Launch these in parallel (different concerns within listener.py):
T014: "Implement baseline calibration in EnvironmentListener._establish_baseline()"
T016: "Implement event detection in EnvironmentListener._audio_callback()" (needs T014 baseline for comparison)

# After core detection works (T014-T017):

# Launch these in parallel:
T018: "Implement optional event recording in EnvironmentListener._save_event_clip()"
T019: "Implement session summary generation in EnvironmentListener.stop_session()"
T020: "Implement listen command in audio_intelligence/cli/__init__.py"
```

---

## Parallel Example: User Story 2

```bash
# After T026 (analyzer skeleton) completes:

# Launch these sequentially (but different from US1):
T027: "Implement file validation in AudioAnalyzer.analyze_file()"
T028: "Implement basic feature extraction" (needs T027 for loaded audio)
T029: "Implement advanced feature extraction" (parallel to T028 conceptually, but uses same audio)
T030: "Implement anomaly detection" (can use basic features from T028)

# Meanwhile, tests can run independently:
T024: "Add test_analyzer_imports()" - can write anytime
T025: "Add test_analyzer_basic_workflow()" - can write anytime, will fail until analyzer works
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

**Goal**: Deliver working real-time monitoring in shortest time

1. **Phase 1**: Setup (T001-T006) - ~30 minutes
2. **Phase 2**: Foundational (T007-T011) - ~1-2 hours
3. **Phase 3**: User Story 1 (T012-T023) - ~4-6 hours
4. **STOP and VALIDATE**: Run `audio-intelligence listen --duration 30`, generate test sounds, verify events detected
5. **Demo ready**: Engineer can monitor live audio environment with event detection

**Estimated MVP Time**: 1 day for experienced developer

### Incremental Delivery

1. **Foundation** (Phase 1-2) → Project structure + data models ready
2. **+ User Story 1** (Phase 3) → **MVP**: Real-time monitoring works → Deploy/Demo 🎯
3. **+ User Story 2** (Phase 4) → File analysis works → Deploy/Demo
4. **+ User Story 3** (Phase 5) → AI insights work (optional) → Deploy/Demo
5. **+ Polish** (Phase 6) → Production-ready POC → Final Deploy

**Each increment adds value without breaking previous functionality**

### Parallel Team Strategy

With 3 developers:

1. **Together**: Complete Phase 1 (Setup) and Phase 2 (Foundational) - ~2-3 hours
2. **Split after foundation complete**:
   - **Developer A**: User Story 1 (T012-T023) - Real-time monitoring
   - **Developer B**: User Story 2 (T024-T035) - File analysis
   - **Developer C**: User Story 3 (T036-T045) - AI insights
3. **Merge**: Each story independently testable, minimal conflicts (different files)
4. **Together**: Phase 6 (Polish) - ~2-3 hours

**Estimated Total Time with 3 developers**: 1.5-2 days

### Testing Strategy (Sanity Tests Only)

Per Constitution Principle III, tests focus on happy path only:

- **7 total tests** in single `test_sanity.py` file
- **<10 seconds** total runtime
- **No mocking complexity** except for AI token (optional dependency)
- **Synthetic audio generation** for test files (scipy.io.wavfile)
- **Run before commit**: `pytest audio_intelligence/test_sanity.py -v`

**Test Coverage by Story**:

- US1 (Real-time): 2 tests (imports, basic workflow)
- US2 (File analysis): 4 tests (imports, workflow, features, anomalies)
- US3 (AI): 1 test (graceful degradation)

---

## Success Criteria Mapping

Tasks mapped to success criteria from spec.md:

- **SC-001** (5-minute setup): T001-T006 (setup.py, README.md, pip install)
- **SC-002** (<2s latency): T015-T017 (chunk processing, event detection)
- **SC-003** (<30s analysis): T028-T030 (feature extraction optimized)
- **SC-004** (1GB files, <2GB RAM): T031 (memory management)
- **SC-005** (no audio upload): T038-T040 (feature vectors only)
- **SC-006** (80% time reduction): T013-T023 (real-time monitoring vs post-hoc review)
- **SC-007** (graceful degradation): T039, T045 (AI optional)
- **SC-008** (90% first session success): T020 (clear CLI), T004 (README)
- **SC-009** (<10s sanity tests): T051 (test suite validation)
- **SC-010** (<5s AI response): T040 (AI query with timeout)

---

## Task Count Summary

- **Phase 1 (Setup)**: 6 tasks
- **Phase 2 (Foundational)**: 5 tasks (BLOCKING)
- **Phase 3 (US1 - Real-time)**: 12 tasks (MVP)
- **Phase 4 (US2 - File analysis)**: 12 tasks
- **Phase 5 (US3 - AI insights)**: 10 tasks (OPTIONAL)
- **Phase 6 (Polish)**: 10 tasks

**Total**: 55 tasks

**Parallel opportunities**: ~15 tasks marked [P] can run concurrently

**MVP scope**: Phase 1-3 = 23 tasks = Minimum viable product

**Full POC scope**: All phases = 55 tasks = Complete feature with AI

---

## Notes

- **[P] tasks**: Different files, no dependencies - safe to parallelize
- **[Story] label**: Maps task to user story (US1/US2/US3) for traceability
- **Constitution compliance**: Sanity tests only (<10s), POC-first approach, local processing enforced
- **File paths included**: Every implementation task specifies exact file location
- **Independent stories**: Each user story can be tested and demoed independently
- **Graceful degradation**: AI features optional, system works without AI (US3)
- **Memory safety**: Explicit buffer release, file size checks before loading
- **Error handling**: Actionable error messages with remediation steps throughout

---

## Getting Started

**To begin implementation**:

1. Start with Phase 1 (Setup) - T001 to T006
2. Complete Phase 2 (Foundational) - T007 to T011 - **MUST FINISH BEFORE USER STORIES**
3. Choose MVP path (US1 only) or parallel path (all stories at once)
4. For MVP: Implement Phase 3 (US1) tasks T012-T023 sequentially
5. Validate: Run `audio-intelligence listen --duration 30` and verify event detection
6. If MVP working: Add US2, then US3, then Polish

**First task to start**: T001 - Create audio_intelligence/ package directory structure

**First validation point**: After T011 (Foundational complete) - verify imports work:

```python
from audio_intelligence.models import ListeningSession, AcousticEvent
from audio_intelligence.config import get_config
```

**MVP validation point**: After T023 (US1 complete) - verify listening session works:

```bash
audio-intelligence listen --duration 30 --record-events
# Generate test sounds (clap, whistle)
# Verify events detected and displayed within 2 seconds
```
