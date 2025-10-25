import pytest
from playwright.async_api import Page, expect

class TestVoiceRecording:
    async def test_recording_button_states(self, page: Page):
        """Test recording button state transitions"""
        # Click record button
        await page.click("#voice-record-button")
        
        # Verify recording state
        recording_btn = page.locator("#voice-record-button")
        style = await recording_btn.get_attribute("style")
        assert "#ff4d4f" in style  # Red color for recording
        
        # Verify other buttons disabled
        await expect(page.locator("#ai-chat-x-send-btn")).to_be_disabled()
        await expect(page.locator("#voice-call-btn")).to_be_disabled()
        
        # Simulate recording duration
        await page.wait_for_timeout(2000)
        
        # Stop recording
        await page.click("#voice-record-button")
        
        # Wait for STT processing
        await page.wait_for_timeout(3000)
        
        # Verify buttons return to idle
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
    
    async def test_microphone_permission_denied(self, page: Page):
        """Test error handling when mic permission denied"""
        # Deny permissions in context setup
        context = page.context
        await context.grant_permissions([])  # No permissions
        
        # Attempt recording
        await page.click("#voice-record-button")
        
        # Wait for error message
        await page.wait_for_timeout(1000)
        
        # Check console for error logs
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg) if msg.type == "error" else None)
        
        assert len(console_errors) > 0
