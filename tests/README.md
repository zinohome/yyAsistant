# Voice Chat Testing Framework

This directory contains the comprehensive testing framework for the real-time voice chat functionality in YYAssistant.

## Overview

The testing framework covers three main scenarios:
1. **Text Chat** - Text input, SSE streaming, TTS playback
2. **Voice Recording** - Microphone recording, STT conversion, AI processing
3. **Real-time Dialogue** - Continuous voice conversation with VAD

## Test Structure

```
tests/
├── config/
│   └── test_config.py          # Test configuration
├── fixtures/                   # Test data and audio samples
├── conftest.py                 # Pytest fixtures
├── test_text_chat.py           # Text chat scenario tests
├── test_voice_recording.py     # Voice recording scenario tests
├── test_realtime_dialogue.py   # Real-time dialogue tests
├── test_button_states.py       # Button state matrix tests
├── test_error_handling.py      # Error handling tests
├── test_performance.py         # Performance and load tests
├── run_tests.py               # Test execution script
└── requirements.txt           # Test dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
cd yyAsistant
pip install -r tests/requirements.txt
python -m playwright install chromium
```

### 2. Run All Tests

```bash
# Execute the complete test plan
./scripts/execute_voice_tests.sh

# Or run specific test suites
python -m pytest tests/test_text_chat.py -v
python -m pytest tests/test_voice_recording.py -v
python -m pytest tests/test_realtime_dialogue.py -v
```

### 3. Generate Reports

```bash
# Run with HTML report and coverage
python -m pytest tests/ -v \
    --html=reports/test_report.html \
    --self-contained-html \
    --cov=yyAsistant \
    --cov-report=html \
    --cov-report=term
```

## Test Scenarios

### Text Chat Tests (`test_text_chat.py`)

- **Basic text input flow** - Complete text chat with button state validation
- **Empty input validation** - Warning message for empty inputs
- **Long text processing** - TTS segmentation for long texts
- **Edge cases** - Special characters, emojis, very long texts

### Voice Recording Tests (`test_voice_recording.py`)

- **Recording button states** - State transitions during recording
- **Microphone permissions** - Error handling for denied permissions
- **STT conversion** - Speech-to-text accuracy
- **Audio quality** - Different recording conditions

### Real-time Dialogue Tests (`test_realtime_dialogue.py`)

- **Dialogue initialization** - Starting real-time conversation
- **Control buttons** - Mute/unmute, start/stop functionality
- **Continuous conversation** - Multi-turn dialogue flow
- **VAD detection** - Voice activity detection accuracy

### Button State Tests (`test_button_states.py`)

- **State transitions** - IDLE → PROCESSING → IDLE
- **Concurrent operations** - Blocking during processing
- **Rapid clicking** - State stability under stress
- **State matrix validation** - All possible state combinations

### Error Handling Tests (`test_error_handling.py`)

- **Network failures** - Connection loss and recovery
- **SSE timeouts** - Server timeout handling
- **Audio device errors** - Microphone/speaker issues
- **Permission errors** - Browser permission handling

### Performance Tests (`test_performance.py`)

- **Response time** - Text response < 3 seconds
- **TTS latency** - Audio generation < 2 seconds
- **Memory usage** - Long-running stability
- **Concurrent users** - Multi-user performance

## Configuration

### Test Configuration (`config/test_config.py`)

```python
class TestConfig:
    BASE_URL = "http://192.168.32.156:8050"
    BACKEND_URL = "http://192.168.32.156:9800"
    TIMEOUT = 30000  # 30 seconds
    HEADLESS = False  # Set True for CI
    AUDIO_SAMPLE_FILE = "tests/fixtures/test_audio.wav"
```

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = --html=reports/test_report.html --self-contained-html --cov=yyAsistant --cov-report=html --cov-report=term
```

## Manual Testing

### Environment Setup

1. **Backend Service**: Ensure running on http://192.168.32.156:9800
2. **Frontend Service**: Ensure running on http://192.168.32.156:8050
3. **Browser Permissions**: Grant microphone access
4. **Audio Devices**: Test speakers/headphones

### Manual Test Checklist

Follow the detailed checklist in `docs/QUICK_TEST_CHECKLIST.md`:

1. **Text Chat Scenario**
   - Basic text input and button states
   - Empty input validation
   - Long text processing with TTS segmentation

2. **Voice Recording Scenario**
   - Recording button state transitions
   - Microphone permission handling
   - STT conversion and SSE triggering

3. **Real-time Dialogue Scenario**
   - Dialogue initialization
   - Control buttons (mute/stop)
   - Continuous conversation

4. **Button State Matrix**
   - All state transitions
   - Concurrent operation blocking
   - Rapid button clicking

5. **Error Handling**
   - Network disconnect recovery
   - SSE timeout handling
   - Audio device errors

## Test Reports

### HTML Report
- **Location**: `reports/test_report.html`
- **Content**: Test results, screenshots, console logs
- **Format**: Self-contained HTML file

### Coverage Report
- **Location**: `htmlcov/index.html`
- **Content**: Code coverage analysis
- **Metrics**: Line coverage, branch coverage, function coverage

### Execution Report
- **Location**: `docs/TEST_EXECUTION_REPORT.md`
- **Content**: Manual test results, issues found, recommendations
- **Format**: Markdown document

## Success Criteria

### Functional Requirements
- ✅ All three scenarios (text, recording, realtime) fully functional
- ✅ Button state transitions 100% correct
- ✅ Error handling covers all edge cases
- ✅ User experience smooth and responsive

### Performance Requirements
- ✅ Text response time < 3 seconds
- ✅ Recording processing time < 5 seconds
- ✅ Real-time dialogue latency < 2 seconds
- ✅ Audio quality clarity > 90%

### Stability Requirements
- ✅ Continuous usage for 30+ minutes without crashes
- ✅ Multiple recordings without conflicts
- ✅ Long-duration real-time dialogue without interruption
- ✅ No memory leaks detected

### Automated Test Coverage
- ✅ 80%+ code coverage for voice-related components
- ✅ All critical user paths automated
- ✅ Performance tests pass consistently
- ✅ Error recovery scenarios validated

## Troubleshooting

### Common Issues

1. **Playwright Installation**
   ```bash
   python -m playwright install chromium
   ```

2. **Microphone Permissions**
   - Ensure browser has microphone access
   - Test in incognito mode if needed

3. **Audio Device Issues**
   - Check system audio settings
   - Test with different browsers

4. **Network Connectivity**
   - Verify backend/frontend services are running
   - Check firewall settings

### Debug Mode

Run tests with debug output:
   ```bash
python -m pytest tests/ -v -s --tb=long
```

### Headless Mode

Run tests in headless mode for CI:
```bash
HEADLESS=true python -m pytest tests/
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Voice Chat Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
          python-version: 3.11
    - name: Install dependencies
      run: |
          pip install -r tests/requirements.txt
          python -m playwright install chromium
    - name: Run tests
        run: python -m pytest tests/ --html=reports/test_report.html
```

## Contributing

### Adding New Tests

1. Create test file following naming convention: `test_*.py`
2. Use appropriate test class: `Test*`
3. Follow async/await pattern for Playwright tests
4. Add proper error handling and timeouts
5. Update documentation

### Test Data

- Add audio samples to `tests/fixtures/`
- Use realistic test data
- Include edge cases and error scenarios

### Documentation

- Update this README for new test scenarios
- Add troubleshooting steps for new issues
- Keep configuration examples current

## Support

For issues with the testing framework:
1. Check the test reports for specific failures
2. Review browser console logs
3. Verify environment setup
4. Check network connectivity
5. Review test configuration