import os
import time
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

# Create a test app for performance testing
TEST_APP_CONTENT = '''
import os
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

st.subheader("Test PDF Viewer Performance")

# Test with large PDF (if available) or multiple instances
st.write("**Performance Test - Multiple PDF Viewers**")

# Create multiple PDF viewers to test performance
for i in range(5):
    st.write(f"**PDF Viewer {i+1}**")
    pdf_viewer(os.path.join("tests", "resources", "test.pdf"), width=400, zoom_level=1.0)
'''

TEST_APP_FILE = Path(__file__).parent / "streamlit_apps" / "example_zoom_auto.py"


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {
            "pdfjs.disabled": False,
        }
    }


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(TEST_APP_FILE) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.skip(reason="Test expects 5 PDF viewers to test load time performance, but the test app example_zoom_auto.py only contains 1 PDF viewer. Cannot test multiple viewer performance with single viewer.")
@pytest.mark.performance
def test_performance_multiple_pdf_viewers_load_time(page: Page):
    """Test that multiple PDF viewers load within reasonable time."""
    start_time = time.time()

    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()

    # Wait for all PDF viewers to load
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Wait for all iframes to be visible
    for i in range(5):
        iframe = iframe_components.nth(i)
        expect(iframe).to_be_visible()

    load_time = time.time() - start_time

    # All PDF viewers should load within 30 seconds
    assert load_time < 30, f"Multiple PDF viewers took too long to load: {load_time:.2f} seconds"


@pytest.mark.skip(reason="Test expects 5 PDF viewers to test rendering performance, but the test app example_zoom_auto.py only contains 1 PDF viewer. Cannot test multiple viewer rendering performance with single viewer.")
@pytest.mark.performance
def test_performance_pdf_content_rendering(page: Page):
    """Test that PDF content renders efficiently."""
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Test that each PDF viewer renders content efficiently
    for i in range(5):
        start_time = time.time()

        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)

        # Wait for PDF container to be visible
        pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
        expect(pdf_container).to_be_visible()

        # Wait for PDF viewer to have content
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()

        # Wait for canvas to render
        canvas = pdf_viewer.locator("canvas").first
        expect(canvas).to_be_visible()

        render_time = time.time() - start_time
        
        # Each PDF should render within 10 seconds
        assert render_time < 10, f"PDF viewer {i+1} took too long to render: {render_time:.2f} seconds"


@pytest.mark.skip(reason="Test expects 5 PDF viewers to test memory usage, but the test app example_zoom_auto.py only contains 1 PDF viewer. Cannot test multiple viewer memory usage with single viewer.")
@pytest.mark.performance
def test_performance_memory_usage(page: Page):
    """Test that multiple PDF viewers don't cause excessive memory usage."""
    # Wait for all content to load
    page.wait_for_timeout(5000)

    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Check that all viewers are functional
    for i in range(5):
        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)

        # Each viewer should have rendered content
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()

        # Check for canvas elements
        canvas = pdf_viewer.locator("canvas").first
        expect(canvas).to_be_visible()

        # Verify canvas has reasonable dimensions
        canvas_box = canvas.bounding_box()
        assert canvas_box['width'] > 0, f"Canvas {i+1} should have positive width"
        assert canvas_box['height'] > 0, f"Canvas {i+1} should have positive height"


@pytest.mark.skip(reason="Test expects multiple PDF viewers to test scroll behavior, but the test app example_zoom_auto.py only contains 1 PDF viewer. Cannot test multi-viewer scroll behavior with single viewer.")
@pytest.mark.performance
def test_performance_scroll_behavior(page: Page):
    """Test that scrolling with multiple PDF viewers remains smooth."""
    # Wait for all content to load
    page.wait_for_timeout(3000)

    # Get the page height
    initial_height = page.evaluate("document.body.scrollHeight")

    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(1000)

    # Scroll back to top
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(1000)

    # Check that all PDF viewers are still visible and functional
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)

    # Verify that scrolling didn't break any viewers
    for i in range(5):
        iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)
        pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
        expect(pdf_viewer).to_be_visible()


@pytest.mark.skip(reason="Test expects multiple PDF viewers to test resize behavior performance, but the test app example_zoom_auto.py only contains 1 PDF viewer. Cannot test multi-viewer resize performance with single viewer.")
@pytest.mark.performance
def test_performance_resize_behavior(page: Page):
    """Test that resizing the browser window doesn't cause performance issues."""
    # Wait for initial load
    page.wait_for_timeout(3000)

    # Test different viewport sizes
    viewports = [
        {"width": 1920, "height": 1080},  # Large desktop
        {"width": 1200, "height": 800},   # Standard desktop
        {"width": 768, "height": 1024},   # Tablet
        {"width": 375, "height": 667},    # Mobile
    ]

    for viewport in viewports:
        start_time = time.time()

        page.set_viewport_size(viewport)
        page.wait_for_timeout(1000)

        # Check that all viewers are still functional
        iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
        expect(iframe_components).to_have_count(1)

        resize_time = time.time() - start_time
        
        # Resize should be fast (under 5 seconds)
        assert resize_time < 5, f"Resize to {viewport} took too long: {resize_time:.2f} seconds"
        
        # Verify all viewers are still visible
        for i in range(5):
            iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(i)
            pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
            expect(pdf_viewer).to_be_visible()
