import pytest
from playwright.async_api import Page, expect
from tests.config.test_config import TestConfig

class TestTextChat:
    async def test_basic_text_input(self, page: Page):
        """Test basic text chat flow with button states"""
        # Input text
        await page.fill("#ai-chat-x-input", "你好，请介绍一下自己")
        
        # Click send
        await page.click("#ai-chat-x-send-btn")
        
        # Verify send button loading state
        await expect(page.locator("#ai-chat-x-send-btn")).to_have_attribute("loading", "true")
        
        # Verify record/call buttons disabled
        await expect(page.locator("#voice-record-button")).to_be_disabled()
        await expect(page.locator("#voice-call-btn")).to_be_disabled()
        
        # Wait for SSE completion (max 30s)
        await page.wait_for_selector(".message-content", timeout=TestConfig.TIMEOUT)
        
        # Wait for TTS completion
        await page.wait_for_timeout(2000)
        
        # Verify all buttons return to idle
        await expect(page.locator("#ai-chat-x-send-btn")).not_to_have_attribute("loading", "true")
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
        await expect(page.locator("#voice-call-btn")).not_to_be_disabled()
    
    async def test_empty_input_validation(self, page: Page):
        """Test empty input shows warning"""
        await page.click("#ai-chat-x-send-btn")
        
        # Verify warning message appears
        await page.wait_for_selector("#global-message", timeout=3000)
        message = await page.locator("#global-message").text_content()
        assert "请输入消息内容" in message
    
    async def test_long_text_processing(self, page: Page):
        """Test long text with TTS segmentation"""
        long_text = "测试长文本处理能力。" * 100  # >500 chars
        await page.fill("#ai-chat-x-input", long_text)
        await page.click("#ai-chat-x-send-btn")
        
        # Verify processing completes
        await page.wait_for_selector(".message-content", timeout=TestConfig.TIMEOUT)
        
        # Check console for TTS segmentation logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg.text))
        await page.wait_for_timeout(5000)
        
        # Verify segmentation occurred
        assert any("TTS segment" in log for log in console_logs)
