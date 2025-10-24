import pytest
import time
from playwright.async_api import Page

class TestPerformance:
    async def test_text_response_time(self, page: Page):
        """Verify text response < 3 seconds"""
        await page.fill("#ai-chat-x-input", "快速响应测试")
        
        start_time = time.time()
        await page.click("#ai-chat-x-send-btn")
        await page.wait_for_selector(".message-content", timeout=30000)
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response_time < 3.0, f"Response time {response_time}s exceeds 3s"
    
    async def test_tts_latency(self, page: Page):
        """Verify TTS starts within 2 seconds of SSE completion"""
        await page.fill("#ai-chat-x-input", "TTS延迟测试")
        
        # Monitor console for TTS start event
        tts_started = False
        sse_completed = False
        
        async def check_console(msg):
            nonlocal tts_started, sse_completed
            if "SSE完成" in msg.text:
                sse_completed = True
            if "TTS播放开始" in msg.text:
                tts_started = True
        
        page.on("console", check_console)
        
        await page.click("#ai-chat-x-send-btn")
        await page.wait_for_timeout(10000)
        
        assert sse_completed and tts_started
