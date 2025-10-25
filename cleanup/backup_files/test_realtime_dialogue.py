import pytest
from playwright.async_api import Page, expect

class TestRealtimeDialogue:
    async def test_realtime_dialog_initialization(self, page: Page):
        """Test real-time dialogue startup"""
        # Click start button
        await page.click("#realtime-start-btn")
        
        # Verify button state change
        await expect(page.locator("#realtime-start-btn")).to_be_disabled()
        await expect(page.locator("#realtime-stop-btn")).not_to_be_disabled()
        
        # Verify status indicator
        status = page.locator("#realtime-status")
        await expect(status).to_be_visible()
        
        # Verify audio visualizer canvas
        canvas = page.locator("#audio-visualizer")
        await expect(canvas).to_be_visible()
    
    async def test_realtime_control_buttons(self, page: Page):
        """Test mute and stop functionality"""
        # Start dialogue
        await page.click("#realtime-start-btn")
        await page.wait_for_timeout(1000)
        
        # Test mute
        await page.click("#realtime-mute-btn")
        mute_btn_text = await page.locator("#realtime-mute-btn").text_content()
        assert "取消静音" in mute_btn_text or "Unmute" in mute_btn_text
        
        # Test stop
        await page.click("#realtime-stop-btn")
        await expect(page.locator("#realtime-start-btn")).not_to_be_disabled()
