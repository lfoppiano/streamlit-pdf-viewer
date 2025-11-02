import os
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
    Extend Playwright browser launch arguments to enable Firefox's built-in PDF viewer.
    
    Parameters:
        browser_type_launch_args (dict): Original browser launch arguments provided by Playwright/pytest-playwright.
    
    Returns:
        dict: A copy of the original launch arguments with `firefox_user_prefs` set so `"pdfjs.disabled": False`.
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
    Run the example Streamlit app and provide its StreamlitRunner instance to tests.
    
    The fixture starts the app before tests use it and stops the runner when the fixture context exits.
    
    Returns:
        StreamlitRunner: A StreamlitRunner instance representing the running test app.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app and wait until the app finishes loading.
    
    Parameters:
        page (Page): Playwright page used to navigate and query the app.
        streamlit_app (StreamlitRunner): Test runner providing the app's server_url.
    
    Behavior:
        Navigates to the runner's server_url and waits for the "Running..." status image to be hidden, indicating the app has finished loading.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.ui_interaction
def test_pdf_viewer_ui_interaction(page: Page):
    """Test basic PDF viewer UI interaction."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that the PDF viewer iframe is present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements (rendered PDF content)
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()