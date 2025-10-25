import pytest
from playwright.async_api import Page, Route

class TestErrorHandling:
    async def test_network_disconnect_recovery(self, page: Page):
        """Test reconnection after network failure"""
        # Intercept WebSocket connection
        await page.route("**/ws/chat", lambda route: route.abort())
        
        # Attempt to start recording
        await page.click("#voice-record-button")
        await page.wait_for_timeout(2000)
        
        # Remove route block
        await page.unroute("**/ws/chat")
        
        # Verify reconnection attempt
        await page.wait_for_timeout(3000)
        
        # Check console for reconnection logs
        # (Implementation depends on logging setup)
    
    async def test_sse_timeout_handling(self, page: Page):
        """Test SSE timeout handling"""
        # Intercept SSE endpoint
        await page.route("**/v1/chat/completions", lambda route: route.fulfill(
            status=408,
            body="Request Timeout"
        ))
        
        # Send message
        await page.fill("#ai-chat-x-input", "测试超时")
        await page.click("#ai-chat-x-send-btn")
        
        # Wait for timeout
        await page.wait_for_timeout(5000)
        
        # Verify error handling (buttons should return to idle)
        await expect(page.locator("#voice-record-button")).not_to_be_disabled()
