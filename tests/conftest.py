import pytest
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from tests.config.test_config import TestConfig

@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=TestConfig.HEADLESS)
        yield browser
        await browser.close()

@pytest.fixture(scope="function")
async def context(browser: Browser):
    context = await browser.new_context(
        permissions=["microphone"],
        viewport={"width": 1920, "height": 1080}
    )
    yield context
    await context.close()

@pytest.fixture(scope="function")
async def page(context: BrowserContext):
    page = await context.new_page()
    await page.goto(f"{TestConfig.BASE_URL}/core/chat")
    yield page
    await page.close()