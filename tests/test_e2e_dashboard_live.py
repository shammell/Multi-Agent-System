import os

import pytest
from playwright.sync_api import sync_playwright

from tests.test_e2e_dashboard import streamlit_server


@pytest.mark.skipif(os.getenv("RUN_LIVE_E2E", "0") != "1", reason="Set RUN_LIVE_E2E=1 to run live E2E")
def test_dashboard_e2e_live(streamlit_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = browser.new_context(service_workers="block", bypass_csp=True)
        page = context.new_page()

        page.goto("http://localhost:8501", wait_until="domcontentloaded", timeout=60000)
        page.locator('[data-testid="stMainBlockContainer"]').wait_for(timeout=30000)

        for _ in range(60):
            if "E2E_READY" in page.content():
                break
            page.wait_for_timeout(300)

        textbox = page.get_by_role("textbox")
        textbox.first.fill("Analyze market trends for solar energy in Karachi")
        page.get_by_role("button", name="Run").click()

        ok = False
        for _ in range(80):
            html = page.content()
            if "Final Output" in html and "DraftPayload" in html:
                ok = True
                break
            page.wait_for_timeout(500)

        assert ok
        browser.close()
