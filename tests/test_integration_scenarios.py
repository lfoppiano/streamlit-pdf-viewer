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
    Add a Firefox preference to the provided browser launch arguments to enable built-in PDF rendering.
    
    Parameters:
        browser_type_launch_args (dict): Base browser launch options to augment.
    
    Returns:
        dict: A new launch-arguments dictionary merging the input with `firefox_user_prefs` where `"pdfjs.disabled"` is set to `False`.
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
    Start the example Streamlit app for the test module and provide its runner.
    
    This module-scoped, autouse pytest fixture launches the Streamlit app defined by TEST_APP_FILE and yields a StreamlitRunner instance for tests to interact with. The runner is stopped and cleaned up when the fixture's context exits.
    Returns:
        StreamlitRunner: A running StreamlitRunner for the test app, providing access to the app's server URL and lifecycle controls.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app URL and wait until the app's loading indicator is hidden.
    
    Parameters:
        page (Page): Playwright page instance used for navigation and checks.
        streamlit_app (StreamlitRunner): Runner that exposes the app's `server_url`.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.integration
def test_pdf_viewer_integration(page: Page):
    """
    Verify a Streamlit-embedded PDF viewer renders and is accessible via its iframe.
    
    Asserts that the page displays the PDF viewer title text, that exactly one iframe with the viewer is present, that the iframe contains visible `pdfContainer` and `pdfViewer` elements, and that at least one `canvas` element (rendered PDF content) is visible.
    
    Parameters:
        page (Page): Playwright Page instance pointed at the running Streamlit app.
    """
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