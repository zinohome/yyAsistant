class TestConfig:
    BASE_URL = "http://192.168.32.156:8050"
    BACKEND_URL = "http://192.168.32.156:9800"
    TIMEOUT = 30000  # 30 seconds
    HEADLESS = False  # Set True for CI
    AUDIO_SAMPLE_FILE = "tests/fixtures/test_audio.wav"
