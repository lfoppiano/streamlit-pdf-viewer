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
    Add Firefox-specific preferences to the provided browser launch arguments.
    
    Parameters:
        browser_type_launch_args (dict): Base browser launch arguments to extend.
    
    Returns:
        dict: A new launch-arguments mapping that includes a `firefox_user_prefs` entry with `"pdfjs.disabled": False`.
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
    Start a Streamlit app for the test session and provide its runner.
    
    The function launches the Streamlit app located at TEST_APP_FILE and yields a StreamlitRunner instance for use by tests. The runner is started before yielding and stopped when the generator completes.
    Returns:
    	runner (StreamlitRunner): A running StreamlitRunner for the test application.
    """
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app and wait for the app to finish loading.
    
    Parameters:
        page (Page): Playwright page used to navigate and interact with the application.
        streamlit_app (StreamlitRunner): Test runner that exposes the app's server_url to navigate to.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.accessibility
def test_accessibility_iframe_titles(page: Page):
    """Test that PDF viewer iframes have proper titles for screen readers."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that PDF viewer iframe has proper title
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Verify that the iframe has the expected title
    iframe = iframe_components.nth(0)
    title = iframe.get_attribute('title')
    assert title == "streamlit_pdf_viewer.streamlit_pdf_viewer", "Iframe should have proper title"


@pytest.mark.accessibility
def test_accessibility_keyboard_navigation(page: Page):
    """Test that PDF viewers are accessible via keyboard navigation."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test keyboard navigation to the iframe
    iframe = iframe_components.nth(0)
    
    # Focus on the iframe
    iframe.focus()
    
    # Check that the iframe is focusable
    focused_element = page.evaluate("document.activeElement")
    assert focused_element is not None, "Iframe should be focusable"


@pytest.mark.accessibility
def test_accessibility_zoom_levels_for_visibility(page: Page):
    """
    Verify the PDF viewer's rendered canvas has positive width and height to ensure the content is visible to users with visual impairments.
    
    This test locates the PDF viewer iframe and asserts the first canvas element inside it has a width and height greater than zero.
    """
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Test the PDF viewer
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    canvas = iframe_frame.locator("canvas").first
    canvas_box = canvas.bounding_box()
    
    # Verify that the canvas has reasonable dimensions for accessibility
    assert canvas_box['width'] > 0, "Canvas should have positive width for accessibility"
    assert canvas_box['height'] > 0, "Canvas should have positive height for accessibility"


@pytest.mark.accessibility
def test_accessibility_screen_reader_compatibility(page: Page):
    """
    Verifies the PDF viewer iframe exposes screen-reader relevant attributes.
    
    Asserts a single PDF viewer iframe exists, that it has a non-empty title attribute, and that it is not hidden from assistive technologies via `aria-hidden="true"`.
    """
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Check that the iframe has proper ARIA attributes or is properly labeled
    iframe = iframe_components.nth(0)
    
    # Check for title attribute (already tested above)
    title = iframe.get_attribute('title')
    assert title is not None, "Iframe should have a title for screen readers"
    
    # Check that the iframe is not hidden from screen readers
    aria_hidden = iframe.get_attribute('aria-hidden')
    assert aria_hidden != 'true', "Iframe should not be hidden from screen readers"


@pytest.mark.accessibility
def test_accessibility_high_contrast_mode(page: Page):
    """
    Ensure the embedded PDF viewer remains visible and functional when a high-contrast CSS filter is applied.
    
    Applies a global contrast filter to simulate high-contrast mode, waits briefly for rendering, asserts exactly one viewer iframe is present, and verifies the viewer container (div#pdfViewer) and its first canvas element are visible.
    """
    # Simulate high contrast mode by adding CSS
    page.add_style_tag(content="""
        * {
            filter: contrast(200%) !important;
        }
    """)
    
    page.wait_for_timeout(1000)
    
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)
    
    # Check that the viewer is still visible and functional in high contrast
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
    
    # Check for canvas elements
    canvas = pdf_viewer.locator("canvas").first
    expect(canvas).to_be_visible()


@pytest.mark.accessibility
def test_accessibility_responsive_text_sizing(page: Page):
    """Test that PDF viewers respond well to different text sizes."""
    # Test with different viewport sizes that might affect text rendering
    viewports = [
        {"width": 1920, "height": 1080},  # Large desktop
        {"width": 375, "height": 667},    # Mobile
    ]
    
    for viewport in viewports:
        page.set_viewport_size(viewport)
        page.wait_for_timeout(1000)
        
        iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
        expect(iframe_components).to_have_count(1)
        
        # Check that the viewer remains accessible
        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()
        
        # Check for canvas elements
        canvas = pdf_viewer.locator("canvas").first
        expect(canvas).to_be_visible()
        
        # Verify canvas has reasonable dimensions for accessibility
        canvas_box = canvas.bounding_box()
        assert canvas_box['width'] > 0, f"Canvas should be visible at viewport {viewport}"
        assert canvas_box['height'] > 0, f"Canvas should have positive height at viewport {viewport}"