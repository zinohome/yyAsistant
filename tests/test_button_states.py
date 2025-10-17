import pytest
from playwright.async_api import Page, expect

class TestButtonStates:
    async def test_idle_to_text_processing(self, page: Page):
        """Test IDLE → TEXT_PROCESSING transition"""
        # Verify initial idle state
        await expect(page.locator("#ai-chat-x-send-btn")).not_to_be_disabled()
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
        await expect(page.locator("#voice-call-btn")).not_to_be_disabled()
        
        # Trigger text processing
        await page.fill("#ai-chat-x-input", "测试")
        await page.click("#ai-chat-x-send-btn")
        
        # Verify text processing state
        await expect(page.locator("#ai-chat-x-send-btn")).to_have_attribute("loading", "true")
        await expect(page.locator("#voice-record-button")).to_be_disabled()
        await expect(page.locator("#voice-call-btn")).to_be_disabled()
        
        # Wait for return to idle
        await page.wait_for_timeout(10000)
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
    
    async def test_concurrent_operation_blocking(self, page: Page):
        """Test that concurrent operations are blocked"""
        # Start text processing
        await page.fill("#ai-chat-x-input", "测试")
        await page.click("#ai-chat-x-send-btn")
        
        # Attempt to click record while processing
        await page.wait_for_timeout(500)
        is_disabled = await page.locator("#voice-record-button").is_disabled()
        assert is_disabled, "Record button should be disabled during text processing"
    
    async def test_rapid_button_clicks(self, page: Page):
        """Test rapid clicking doesn't break state"""
        # Rapid clicks on send button
        for _ in range(5):
            await page.fill("#ai-chat-x-input", "快速测试")
            await page.click("#ai-chat-x-send-btn", timeout=100)
            await page.wait_for_timeout(50)
        
        # Wait for all processing to complete
        await page.wait_for_timeout(15000)
        
        # Verify final state is idle
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
