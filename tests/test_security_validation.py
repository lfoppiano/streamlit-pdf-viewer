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
    Merge additional launch arguments enabling Firefox's built-in PDF viewer into existing Playwright browser launch options.
    
    Parameters:
        browser_type_launch_args (dict): Existing browser launch arguments to extend.
    
    Returns:
        dict: A new launch arguments mapping with `firefox_user_prefs` set so the Firefox PDF viewer (`pdfjs.disabled`) is disabled (PDF viewer enabled).
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
    Start the Streamlit example app defined by TEST_APP_FILE and yield the running StreamlitRunner for tests; the app is stopped when the fixture finishes.
    
    Returns:
        StreamlitRunner: A runner instance controlling the started Streamlit app.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the given Playwright page to the Streamlit app URL and wait until the app's "Running..." indicator is hidden.
    
    Parameters:
        page (Page): Playwright page instance to navigate.
        streamlit_app (StreamlitRunner): Streamlit runner exposing the app's server_url.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.security
def test_valid_pdf_file_security(page: Page):
    """Test that valid PDF files are handled securely."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that the valid PDF viewer iframe is present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Verify that the PDF viewer is secure (sandboxed iframe)
    iframe = iframe_components.first
    sandbox_attr = iframe.get_attribute('sandbox')
    assert sandbox_attr is not None, "PDF viewer iframe should have sandbox attribute for security"
    
    # Check that the iframe has proper security attributes
    src_attr = iframe.get_attribute('src')
    assert src_attr is not None, "PDF viewer iframe should have src attribute"
    assert 'streamlit_pdf_viewer' in src_attr, "PDF viewer iframe should have correct src"

