from configs.app_config import app_config

class TestConfig:
    BASE_URL = app_config.TEST_BASE_URL
    BACKEND_URL = app_config.TEST_BACKEND_URL
    TIMEOUT = 30000  # 30 seconds
    HEADLESS = False  # Set True for CI
    AUDIO_SAMPLE_FILE = "tests/fixtures/test_audio.wav"
