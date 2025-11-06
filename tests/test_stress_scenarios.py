import time
import pytest
from playwright.sync_api import Page, expect


@pytest.mark.stress
def test_pdf_viewer_load_performance(page: Page):
    """Test basic PDF viewer load performance."""
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


