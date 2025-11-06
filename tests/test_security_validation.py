import pytest
from playwright.sync_api import Page, expect


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


