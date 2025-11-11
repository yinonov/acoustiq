<!--
═══════════════════════════════════════════════════════════════════════════════
SYNC IMPACT REPORT
Generated: 2025-11-11
Operation: Constitution Validation & Consistency Check
═══════════════════════════════════════════════════════════════════════════════

VERSION INFORMATION
───────────────────
Previous Version: 1.0.0 (Initial - 2025-11-11)
Current Version:  1.0.1 (Patch - 2025-11-11)
Bump Rationale:   PATCH increment - Clarification refinements and template 
                  consistency validation. No semantic changes to principles.

CONSTITUTION STATUS
───────────────────
✅ All principles fully defined (no placeholder tokens)
✅ Version information complete
✅ Project-specific content (Audio Intelligence Tool)
✅ 5 Core Principles validated
✅ Governance section complete

PRINCIPLES SUMMARY
──────────────────
No modifications to principles. All 5 principles remain unchanged:
  I.   POC-First Development (NON-NEGOTIABLE)
  II.  Local Processing Only
  III. Sanity Tests Only (REQUIRED)
  IV.  Real-Time First
  V.   AI Agent as Assistant, Not Controller

SECTIONS ANALYZED
─────────────────
✅ Core Principles (complete)
✅ Development Constraints (complete)
✅ Quality Gates (complete)
✅ Anti-Patterns (complete)
✅ Speckit Integration (complete)
✅ Success Metrics (complete)
✅ Governance (complete)
✅ Quick Decision Guide (complete)

TEMPLATE CONSISTENCY VALIDATION
────────────────────────────────

⚠ CRITICAL MISALIGNMENT DETECTED:

File: .specify/templates/tasks-template.md
Issue: Template includes comprehensive test categories (contract tests, 
       integration tests, unit tests) that conflict with Constitution 
       Principle III: "Sanity Tests Only"
       
Lines of Concern:
  - Line 82-87: "Tests for User Story 1 (OPTIONAL - only if tests requested)"
    → Includes contract tests, integration tests
  - Line 108-110: Similar pattern for User Story 2
  - Line 124-126: Similar pattern for User Story 3
  - Multiple references to tests/contract/, tests/integration/, tests/unit/

Recommendation: Update tasks-template.md to reflect sanity-test-only approach:
  - Replace "Tests for User Story X" sections with "Sanity Test for Story X"
  - Remove references to contract/integration/unit test directories
  - Emphasize: ONE sanity test per feature, happy path only, <2 seconds each
  - Update to: tests/test_sanity.py (single file approach per constitution)

⚠ MINOR MISALIGNMENT:

File: .specify/templates/plan-template.md
Issue: "Constitution Check" section exists but doesn't provide specific gates
       aligned with the 5 principles defined in this constitution.
       
Line 30-34: "## Constitution Check" with placeholder "[Gates determined 
            based on constitution file]"

Recommendation: Update plan-template.md Constitution Check section with 
                concrete gates:
  ✅ POC-First: Feature can be demoed in <1 hour?
  ✅ Local Processing: No cloud dependencies?
  ✅ Sanity Tests: Only 1 test per feature planned?
  ✅ Real-Time First: Chunk-based if applicable?
  ✅ AI Optional: Degrades gracefully if AI unavailable?

⚠ MINOR MISALIGNMENT:

File: .specify/templates/spec-template.md
Issue: "User Scenarios & Testing" section emphasizes "INDEPENDENTLY TESTABLE"
       with acceptance scenarios, but doesn't clarify that testing means
       sanity tests only, not comprehensive test suites.

Recommendation: Add clarifying note in spec-template.md:
  "Note: 'Testable' means ONE sanity test per story (<2 seconds), not 
   comprehensive test coverage. See Constitution Principle III."

✅ ALIGNED FILES:

File: .specify/templates/checklist-template.md
Status: Not analyzed (checklist template, no testing implications)

File: .specify/templates/agent-file-template.md  
Status: Not analyzed (agent template, no testing implications)

RUNTIME DOCUMENTATION CONSISTENCY
──────────────────────────────────

✅ README.md
   - References constitution ✓
   - Emphasizes POC-first philosophy ✓
   - Mentions minimal testing approach ✓
   - Aligned with principles

✅ PROJECT_SPEC.md
   - Explicitly states "Sanity Tests Only" ✓
   - Matches constitution principles ✓
   - Quality assurance section aligned ✓

✅ GETTING_STARTED.md
   - Setup instructions match constitution constraints ✓
   - No comprehensive testing references ✓

✅ CONSTITUTION_SUMMARY.md
   - Accurate summary of all principles ✓
   - References sanity-test-only approach ✓
   - Provides quick reference aligned with constitution ✓

FOLLOW-UP ACTIONS REQUIRED
───────────────────────────

Priority 1 (Critical):
  [ ] Update .specify/templates/tasks-template.md
      - Replace comprehensive test sections with sanity-test approach
      - Change test directory structure from tests/{contract,integration,unit}/
        to single tests/test_sanity.py file
      - Emphasize: ONE test per feature, <2 seconds, happy path only
      - Remove "OPTIONAL - only if tests requested" language (sanity tests 
        are REQUIRED per Principle III)

Priority 2 (Important):
  [ ] Update .specify/templates/plan-template.md
      - Fill "Constitution Check" section with concrete gates based on 
        5 principles
      - Provide actionable validation checklist

Priority 3 (Nice to Have):
  [ ] Update .specify/templates/spec-template.md
      - Add clarifying note about sanity-test-only approach
      - Prevent misinterpretation of "independently testable"

DEFERRED ITEMS
──────────────
None. No placeholder tokens intentionally left unfilled.

SUGGESTED COMMIT MESSAGE
────────────────────────
docs: validate constitution v1.0.1 (template consistency audit)

- Add Sync Impact Report to constitution
- Identify template misalignments with sanity-test-only principle
- Flag tasks-template.md for comprehensive→sanity test update
- Document runtime doc consistency (all aligned)
- Version bump: 1.0.0 → 1.0.1 (clarification patch)

═══════════════════════════════════════════════════════════════════════════════
-->

# Audio Intelligence Tool - Constitution

## Core Principles

### I. POC-First Development (NON-NEGOTIABLE)
**Ship working features fast, iterate based on real usage.**

- **Priority**: Working POC over perfect architecture
- **Speed**: Aim to see results in runtime within days, not weeks
- **Validation**: Real acoustic engineers must test features immediately
- **No Over-Engineering**: Reject complexity that doesn't serve immediate POC goals
- **Single Package**: Keep everything in one Python package - no microservices, no distributed systems

**Examples of YES:**
- ✅ Single Python module that works end-to-end
- ✅ Direct file processing without abstraction layers
- ✅ CLI that takes file path, outputs results immediately
- ✅ Simple functions over complex class hierarchies

**Examples of NO:**
- ❌ Abstract base classes "for future extensibility"
- ❌ Separate services for analysis, storage, and processing
- ❌ Complex configuration management systems
- ❌ "Framework" that supports "plugins" but has no actual plugins

### II. Local Processing Only
**All heavy computation stays on the user's machine.**

- **Privacy**: Audio files NEVER leave the user's machine
- **Performance**: No network latency for file processing
- **Efficiency**: Only tiny feature vectors (<1KB) sent to AI agents when needed
- **Storage**: No cloud storage, databases, or remote file systems
- **Libraries**: Use librosa, soundfile, numpy - all local processing

**What Goes Where:**
- ✅ Local: Raw audio loading, feature extraction, spectrogram generation, anomaly detection
- ✅ AI Agent: Pattern analysis, natural language Q&A, insight generation
- ❌ Never Upload: Raw audio data, full spectrograms, unprocessed recordings

### III. Sanity Tests Only (REQUIRED)
**No comprehensive test suites - just ensure no regressions.**

- **Purpose**: Catch breaking changes, not validate every edge case
- **Coverage**: Each feature needs ONE sanity test that exercises the happy path
- **Speed**: All sanity tests must run in < 10 seconds total
- **Location**: Tests live next to the code they test
- **CI/CD**: Run sanity tests before any merge, fail fast on regression

**Sanity Test Structure:**
```python
# test_sanity.py
def test_analyzer_basic_workflow():
    """Sanity: Analyzer can load and analyze a test audio file."""
    analyzer = AudioAnalyzer(agent_enabled=False)
    results = asyncio.run(analyzer.analyze_file("test_sample.wav"))
    assert "basic_features" in results
    assert results["basic_features"]["duration"] > 0
    # That's it - just verify it works end-to-end
```

**NOT Allowed:**
- ❌ 100+ test cases covering edge cases
- ❌ Complex mocking frameworks
- ❌ Integration test environments
- ❌ Performance benchmarks (unless it's clearly broken)
- ❌ Tests that take minutes to run

### IV. Real-Time First
**Listening sessions are primary, file analysis is secondary.**

- **Design Priority**: Environmental monitoring is the core use case
- **Event-Driven**: System should react to acoustic events immediately
- **Feedback Loop**: Users see results as they happen, not after batch processing
- **Recording**: Only save interesting events, not continuous streams
- **Thresholds**: Make detection parameters easily configurable

**Features that Support Real-Time:**
- ✅ Chunk-based processing (0.5-2 second chunks)
- ✅ Event callbacks for immediate user feedback
- ✅ Adjustable sensitivity thresholds
- ✅ Real-time visualization (if simple to add)

**Anti-Patterns:**
- ❌ Requiring full file analysis before any results
- ❌ Batch processing as the only option
- ❌ Delayed event notifications
- ❌ Buffering that hides real-time nature

### V. AI Agent as Assistant, Not Controller
**AI provides insights, humans make decisions.**

- **Purpose**: Answer questions, identify patterns, generate reports
- **Input**: Extracted features and metadata, not raw audio
- **Optional**: All AI features must degrade gracefully if unavailable
- **Simple Integration**: Single agent, no orchestration, no workflows
- **Model**: Use GitHub Models (free tier) for accessibility

**AI Agent Responsibilities:**
- ✅ Analyze extracted audio features
- ✅ Answer questions about listening sessions
- ✅ Suggest analysis approaches
- ✅ Generate summaries and reports

**NOT AI Agent's Job:**
- ❌ Core audio processing (use librosa/speckit)
- ❌ Event detection logic (use rules and thresholds)
- ❌ File I/O operations
- ❌ Critical path operations that can't fail

## Development Constraints

### Technology Stack
**Keep dependencies minimal and focused.**

- **Language**: Python 3.8+ only
- **Audio Processing**: librosa, soundfile, sounddevice, numpy, scipy
- **AI Agent**: Microsoft Agent Framework + OpenAI client + GitHub Models
- **CLI**: click (simple) or argparse (simpler)
- **Visualization**: rich (terminal) or matplotlib (optional)
- **NO**: Django, Flask, FastAPI, SQLAlchemy, Redis, Docker, Kubernetes

### File Structure
**Flat is better than nested.**

```
audio_intelligence/
├── __init__.py           # Main exports
├── analyzer.py           # File analysis
├── listener.py           # Real-time listening
├── agent.py              # AI agent integration
├── cli/                  # Command-line interface
│   └── __init__.py
└── test_sanity.py        # All sanity tests in one file
```

**NO Complex Hierarchies:**
- ❌ `core/`, `utils/`, `helpers/`, `common/` directories
- ❌ Abstract base classes without concrete implementations
- ❌ Layers that just call other layers

### Configuration
**Environment variables and simple parameters only.**

- **API Keys**: Environment variables (GITHUB_TOKEN)
- **Thresholds**: Function parameters with sensible defaults
- **Paths**: Command-line arguments
- **NO**: YAML files, JSON config, .ini files, configuration classes

### Documentation
**Code comments + README + examples.**

- **Required**: README.md with quick start examples
- **Required**: Docstrings on public functions (1-2 lines)
- **Required**: Working example scripts
- **Optional**: Detailed API docs (YAGNI for POC)

## Quality Gates

### Before Merging ANY Code
1. ✅ Sanity test passes (< 10 seconds)
2. ✅ Feature works in demo/example
3. ✅ README updated if new feature
4. ✅ No new dependencies without justification

### Before Calling It "Done"
1. ✅ Acoustic engineer can run it immediately
2. ✅ No setup beyond `pip install -r requirements.txt`
3. ✅ Results visible in < 30 seconds
4. ✅ Fails with clear error messages

## Anti-Patterns to Avoid

### ❌ Premature Optimization
- "Let's add caching for performance" → NO, unless proven slow
- "We need connection pooling" → NO, we're local-only
- "Let's use async for everything" → Only where necessary (I/O, AI calls)

### ❌ Abstraction Layers
- "Let's create an AudioProcessor interface" → NO, just write the function
- "We need a strategy pattern here" → NO, if/else is fine for POC
- "Plugin architecture for extensibility" → NO, not until we have actual plugins

### ❌ Enterprise Patterns
- "Let's add a service layer" → NO, call functions directly
- "We need dependency injection" → NO, just import the module
- "Repository pattern for data access" → NO, we don't have a database

### ❌ Testing Theater
- "100% code coverage" → NO, sanity tests only
- "Let's mock everything" → NO, use real small test files
- "Integration tests for all paths" → NO, one happy path per feature

## Speckit Integration

### Using Speckit Workflow
**When building features, follow this process:**

1. `/speckit.specify` - Quick spec (2-3 paragraphs max for POC features)
2. `/speckit.plan` - Minimal plan, focus on file/function names
3. `/speckit.tasks` - Task list with clear deliverables
4. `/speckit.implement` - Build it and test it works
5. NO `/speckit.analyze` unless actually broken

### Speckit Constitution Alignment
- **Spec**: Focus on user outcome, not implementation
- **Plan**: Simplest implementation that works
- **Tasks**: Each task is < 2 hours of work
- **Implement**: Ship features, not frameworks

## Success Metrics

### POC is Successful When:
- ✅ Acoustic engineer can analyze a real audio file in < 5 minutes from clone to results
- ✅ Real-time listening detects events and displays them immediately
- ✅ AI agent answers basic questions about audio characteristics
- ✅ No audio files uploaded to cloud
- ✅ Setup is: clone + pip install + run

### Feature is Production-Ready When:
- ✅ Used by 3+ acoustic engineers successfully
- ✅ Handles files up to 1GB without crashing
- ✅ Clear error messages for common failure modes
- ✅ Can run for hours without memory leaks (for real-time listening)

## Governance

### Constitution Authority
- This constitution supersedes all "best practices" suggestions from LLMs or engineers
- When in doubt: **simplicity wins**
- POC features that work > comprehensive features that are "almost done"

### Amendment Process
- Constitution can be updated based on real user feedback
- Complexity must be justified by actual pain points, not hypothetical ones
- Any amendment must preserve POC-first philosophy

### Compliance
- Every PR must pass sanity tests
- Code reviews focus on: "Does it work?" and "Is it simple?"
- Reject PRs that add complexity without proven need

**Version**: 1.0.1 | **Ratified**: 2025-11-11 | **Last Amended**: 2025-11-11

---

## Quick Decision Guide

**Someone suggests adding X. Ask:**
1. Does it help acoustic engineers analyze audio faster? → YES = consider, NO = reject
2. Can we demo it working in < 1 hour? → NO = too complex
3. Does it require new infrastructure? → YES = reject for POC
4. Would it fail if AI/network is down? → YES = redesign
5. Do we need tests beyond basic sanity? → NO for POC

**When building a new feature:**
1. Write simplest possible version first
2. Add one sanity test
3. Demo it working with real audio
4. Ship it
5. Iterate based on user feedback

**Remember: Working POC > Perfect Architecture**
