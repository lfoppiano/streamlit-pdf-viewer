import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_tab_2.py")


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
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    """
    Navigate the browser to the running Streamlit app and wait until the app signals it has finished loading.
    
    This autouse fixture directs the Playwright page to the StreamlitRunner's server URL and waits for the "Running..." image indicator to become hidden, indicating the app has loaded and is ready for interaction.
    """
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


@pytest.mark.skip("Needs investigation")
def test_should_render_template_check_container_size(page: Page):
    """
    Verify the PDF viewer renders correctly across two tabs and that the PDF container sizes and visibility update when switching tabs.
    
    Detailed behavior:
    - Confirms the test page text is visible and locates the PDF viewer iframe.
    - Asserts the iframe has non-zero width and height.
    - For tab 1: waits for the PDF container and viewer to be visible, checks the container height > 0 and that its width equals the iframe width, and confirms the first annotations element is hidden.
    - For tab 2 (initial state): verifies the PDF container and viewer are not visible and the second annotations element is hidden; verifies both tab labels are visible.
    - Clicks the second tab, waits for its PDF container to become visible, asserts the container height is approximately 300px, and checks that the resized PDF width is constrained relative to the iframe width (preserving proportions); finally confirms the PDF viewer in tab 2 is visible.
    
    This test uses a Playwright Page fixture and performs UI assertions and size checks; it does not return a value.
    """
    expect(page.get_by_text("Test PDF Viewer with the PDF in a tab")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    iframe_component.wait_for(timeout=5000, state='visible')
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    # Tab 1
    iframe_frame_0 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container_0 = iframe_frame_0.locator('div[id="pdfContainer"]')
    pdf_container_0.wait_for(timeout=5000, state='visible')
    expect(pdf_container_0).to_be_visible()

    b_box_0 = pdf_container_0.bounding_box()
    assert round(b_box_0['height']) > 0
    assert b_box_0['width'] == iframe_box['width']

    pdf_viewer_0 = iframe_frame_0.locator('div[id="pdfViewer"]')
    pdf_viewer_0.wait_for(timeout=5000, state='visible')
    expect(pdf_viewer_0).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    annotations_locator.wait_for(timeout=5000, state='hidden')
    expect(annotations_locator).to_be_hidden()

    # Tab 2
    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    expect(pdf_container_1).not_to_be_visible()

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_1).not_to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(1)
    expect(annotations_locator).to_be_hidden()

    tab0 = page.get_by_text('tab1')
    expect(tab0).to_be_visible()

    tab1 = page.get_by_text('tab2')
    expect(tab1).to_be_visible()

    # click on the second tab and verify that the PDF is visible
    tab1.click()

    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    pdf_container_1.wait_for(timeout=5000, state='visible')
    expect(pdf_container_1).to_be_visible()

    b_box_1 = pdf_container_1.bounding_box()
    assert 299 <= b_box_1['height'] <= 301
    # The second part of the If tests that the width < height, which indicate that we have resized
    # the PDF to keep the proportions
    assert round(b_box_1['width']) <= iframe_box['width'] and round(b_box_1['height']) <= round(b_box_1['height'])

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_1).to_be_visible()
