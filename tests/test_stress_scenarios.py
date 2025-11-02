import os
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

# Use existing example file
TEST_APP_FILE = Path(__file__).parent / "streamlit_apps" / "example_zoom_auto.py"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Merge Firefox-specific preferences into the provided browser launch arguments.
    
    Parameters:
        browser_type_launch_args (dict): Base browser launch arguments to extend.
    
    Returns:
        dict: A new launch-arguments dictionary that preserves the input keys and adds or replaces
        the "firefox_user_prefs" entry so that "pdfjs.disabled" is set to False.
    """
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {
            "pdfjs.disabled": False,
        }
    }


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    """
    Provide a running Streamlit application for the test session.
    
    This pytest fixture starts the Streamlit app defined by TEST_APP_FILE and yields a
    StreamlitRunner that manages the app process. The runner remains active for the
    duration of the test session and is stopped when the fixture finalizes. The
    fixture is intended for session scope and autouse usage in tests.
    
    Returns:
        StreamlitRunner: An active runner that manages the launched Streamlit app.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit application's server URL and wait until the app's "Running..." indicator is hidden.
    
    Parameters:
        page (Page): Playwright page used to navigate.
        streamlit_app (StreamlitRunner): Runner providing the app's server_url.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.stress
def test_pdf_viewer_load_performance(page: Page):
    """
    Verifies the Streamlit PDF viewer loads and displays content within 30 seconds.
    
    Checks that the page contains the expected PDF viewer header text, that exactly one viewer iframe is present and visible, that the viewer finishes loading in under 30 seconds, and that the iframe contains a visible PDF viewer element.
    """
    start_time = time.time()
    
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Wait for PDF viewer to load
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Wait for iframe to be visible
    iframe = iframe_components.nth(0)
    expect(iframe).to_be_visible()
    
    load_time = time.time() - start_time
    
    # PDF viewer should load within 30 seconds
    assert load_time < 30, f"PDF viewer took too long to load: {load_time:.2f} seconds"
    
    # Verify that PDF viewer has content
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

