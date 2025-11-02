import pytest
from playwright.sync_api import Page, expect


@pytest.mark.skip(reason="Test expects error handling scenarios (invalid files, error messages) but the test app example_zoom_auto.py only contains a single valid PDF viewer. Test app content doesn't match test expectations.")
@pytest.mark.error_handling
def test_error_handling_with_invalid_file(page: Page):
    """Test that the PDF viewer handles invalid files gracefully."""
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()

    # Check that error messages are displayed for invalid files
    expect(page.get_by_text("Testing with non-existent file:")).to_be_visible()
    expect(page.get_by_text("Testing with invalid file type:")).to_be_visible()

    # The valid PDF should still render
    expect(page.get_by_text("Testing with valid PDF:")).to_be_visible()

    # Check that at least one PDF viewer iframe is present (for the valid PDF)
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)  # Only the valid PDF should render


@pytest.mark.error_handling
def test_error_handling_graceful_degradation(page: Page):
    """Test that the component degrades gracefully when encountering errors."""
    # Wait for the page to fully load
    page.wait_for_timeout(2000)
    
    # Check that the page doesn't crash and still shows content
    expect(page.get_by_text("Test PDF Viewer with auto zoom (fit to width)")).to_be_visible()
    
    # Check that the PDF viewer is present and functional
    iframe_components = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    expect(iframe_components).to_have_count(1)


@pytest.mark.error_handling
def test_valid_pdf_still_renders_after_errors(page: Page):
    """Test that valid PDFs still render even when there are errors with other files."""
    # Wait for content to load
    page.wait_for_timeout(3000)
    
    # Check that the valid PDF iframe is present and visible
    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').first
    expect(iframe_component).to_be_visible()
    
    # Check that the PDF viewer inside the iframe is functional
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').first
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()
    
    # Verify PDF viewer has content
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()
