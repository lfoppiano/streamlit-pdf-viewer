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
    Provide browser launch arguments with Firefox PDF handling enabled.
    
    Parameters:
        browser_type_launch_args (dict): Existing browser launch arguments to merge into the returned mapping.
    
    Returns:
        dict: The merged browser launch arguments with the Firefox preference `pdfjs.disabled` set to `False`.
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
    Start the example Streamlit application and provide a StreamlitRunner for tests.
    
    Returns:
        runner (StreamlitRunner): Runner for interacting with the launched app. The app is stopped and the runner cleaned up when the fixture completes.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the provided Streamlit app URL and wait until the app indicates it has finished loading.
    
    Parameters:
        page (Page): Playwright page used for navigation and interaction.
        streamlit_app (StreamlitRunner): Runner providing the Streamlit app server URL.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.compatibility
def test_basic_pdf_viewer_compatibility(page: Page):
    """
    Verify the PDF viewer iframe, its container, and rendered canvas are present and visible.
    
    Asserts the page shows the test heading, a single iframe titled "streamlit_pdf_viewer.streamlit_pdf_viewer" exists, the iframe contains visible elements with ids "pdfContainer" and "pdfViewer", and the first canvas inside "pdfViewer" is visible.
    """
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that the basic PDF viewer iframe is present
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)  # Just one PDF viewer
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements (rendered PDF content)
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()


@pytest.mark.compatibility
def test_pdf_viewer_renders_correctly(page: Page):
    """Test that PDF viewer renders correctly across browsers."""
    # Wait for content to load
    page.wait_for_timeout(3000)
    
    # Check that the PDF viewer is present
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
    
    # Verify canvas has reasonable dimensions
    canvas_box = canvas.bounding_box()
    assert canvas_box['width'] > 0, "Canvas should have positive width"
    assert canvas_box['height'] > 0, "Canvas should have positive height"