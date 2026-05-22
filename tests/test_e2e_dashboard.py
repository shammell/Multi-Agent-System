import os
import subprocess
import time
from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright


LOG_DIR = Path(__file__).resolve().parents[1] / "test-artifacts"
LOG_DIR.mkdir(exist_ok=True)
STREAMLIT_STDOUT = LOG_DIR / "streamlit-e2e-stdout.log"
STREAMLIT_STDERR = LOG_DIR / "streamlit-e2e-stderr.log"


@pytest.fixture(scope="module")
def streamlit_server():
    project_root = Path(__file__).resolve().parents[1]
    app_rel_path = "src/ui/dashboard.py"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    env["APP_MODE"] = "mock"

    stdout_fp = open(STREAMLIT_STDOUT, "w", encoding="utf-8")
    stderr_fp = open(STREAMLIT_STDERR, "w", encoding="utf-8")

    proc = subprocess.Popen(
        [
            "python",
            "-m",
            "streamlit",
            "run",
            app_rel_path,
            "--server.port=8501",
            "--server.headless=true",
            "--server.enableCORS=false",
            "--server.enableXsrfProtection=false",
        ],
        cwd=str(project_root),
        env=env,
        stdout=stdout_fp,
        stderr=stderr_fp,
        text=True,
    )

    deadline = time.time() + 30
    started = False
    while time.time() < deadline:
        if proc.poll() is not None:
            raise RuntimeError("Streamlit exited early")
        try:
            import urllib.request

            with urllib.request.urlopen("http://localhost:8501", timeout=1):
                started = True
                break
        except Exception:
            time.sleep(0.5)

    if not started:
        proc.terminate()
        stdout_fp.close()
        stderr_fp.close()
        raise RuntimeError("Streamlit did not start in time")

    yield

    proc.terminate()
    try:
        proc.wait(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    finally:
        stdout_fp.close()
        stderr_fp.close()


@pytest.mark.skipif(os.getenv("RUN_STREAMLIT_E2E", "0") != "1", reason="Set RUN_STREAMLIT_E2E=1 to run Streamlit DOM E2E")
def test_dashboard_e2e(streamlit_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
        context = browser.new_context(service_workers="block", bypass_csp=True)
        page = context.new_page()
        ws_ready = {"ok": False}

        def _on_ws(_ws):
            ws_ready["ok"] = True

        page.on("websocket", _on_ws)
        page.goto("http://localhost:8501", wait_until="domcontentloaded", timeout=60000)

        for _ in range(40):
            if ws_ready["ok"]:
                break
            page.wait_for_timeout(250)
        assert ws_ready["ok"], f"WebSocket handshake not observed. Check logs: {STREAMLIT_STDERR}"

        page.locator('[data-testid="stMainBlockContainer"]').wait_for(timeout=30000)

        sentinel_ready = False
        for _ in range(50):
            if "E2E_READY" in page.content():
                sentinel_ready = True
                break
            page.wait_for_timeout(300)
        assert sentinel_ready, f"Sentinel not rendered. Check logs: {STREAMLIT_STDERR}"

        textbox = page.get_by_role("textbox")
        textbox.first.fill("Analyze market trends for solar energy in Karachi")

        run_button = page.get_by_role("button", name="Run")
        run_button.click()

        started = False
        for _ in range(30):
            html = page.content()
            if "RUN_TRIGGERED" in html or "PIPELINE_RUNNING" in html or "PIPELINE_OK" in html:
                started = True
                break
            page.wait_for_timeout(300)
        assert started, f"Submit not triggered. Check logs: {STREAMLIT_STDERR}"

        result_ready = False
        last_html = ""
        for _ in range(180):
            html = page.content()
            last_html = html
            if "PIPELINE_OK" in html and "Final Output" in html and "DraftPayload" in html and "Routing Graph" in html:
                result_ready = True
                break
            if "PIPELINE_ERR" in html:
                break
            page.wait_for_timeout(400)

        assert "PIPELINE_ERR" not in last_html, f"Pipeline runtime error in UI. Check logs: {STREAMLIT_STDERR}"
        assert result_ready, f"Pipeline output not rendered. Check logs: {STREAMLIT_STDERR}"
        assert "Routing Graph" in page.content()
        assert "Final Output" in page.content()

        browser.close()
