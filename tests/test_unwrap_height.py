import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY, wait_for_canvases
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_unwrap_height.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the Playwright page to the Streamlit app and wait until the app's "Running..." indicator is hidden.
    
    Parameters:
        page (Page): Playwright Page used to navigate and query the app.
        streamlit_app (StreamlitRunner): Runner providing the app's server_url; navigation targets this URL.
    
    Detailed behavior:
        Navigates the page to streamlit_app.server_url and waits until the role="img" element with name "Running..." is no longer visible, indicating the app has finished loading.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_template_check_container_size(page: Page):
    """
    Verify the PDF viewer renders with the expected container size, canvases, and hidden annotations.
    
    Asserts that the example text is visible, the PDF viewer iframe is present and has a non-zero bounding box, the inner pdfContainer width does not exceed the iframe width and has a height of 300, the pdfViewer is visible, exactly 8 canvases (pages) are rendered and visible, and the pdfAnnotations element is hidden.
    """
    expect(page.get_by_text("Test PDF Viewer with specified height")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    b_box = pdf_container.bounding_box()
    # Since we do not specify the width, we occupy all the available space, which should correspond to the
    # parent element's width of the pdfContainer.
    # LF: This was changed with #58, where the proportions are maintained, or at least we try to
    assert b_box['width'] <= iframe_box['width']
    assert b_box['height'] == 300

    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    pdf_viewer.wait_for(timeout=5000, state='visible')
    expect(pdf_viewer).to_be_visible()

    # Wait for canvases to render
    page.wait_for_timeout(500)
    canvas_locator = pdf_viewer.locator("canvas")
    canvas_list = wait_for_canvases(canvas_locator)

    # Should have 8 pages total for the test PDF
    assert len(canvas_list) == 8
    for canvas in canvas_list:
        expect(canvas).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()