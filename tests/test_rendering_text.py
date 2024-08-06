import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_text_layers.py")


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
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_template_check_container_size(page: Page):
    expect(page.get_by_text("Test PDF Viewer with the PDF in a tab and rendering text")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    tab0 = page.get_by_text('tab1')
    expect(tab0).to_be_visible()

    tab1 = page.get_by_text('tab2')
    expect(tab1).to_be_visible()

    # Tab 1
    iframe_frame_0 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container_0 = iframe_frame_0.locator('div[id="pdfContainer"]')
    expect(pdf_container_0).to_be_visible()

    b_box_0 = pdf_container_0.bounding_box()
    assert round(b_box_0['height']) > iframe_box['height']
    assert b_box_0['width'] == iframe_box['width']

    pdf_viewer_0 = iframe_frame_0.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_0).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()

    # Tab 2
    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    expect(pdf_container_1).not_to_be_visible()

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_1).not_to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(1)
    expect(annotations_locator).to_be_hidden()

    text_in_pdf = pdf_viewer_1.get_by_text("from LaH10 to room–temperature").nth(0)
    expect(text_in_pdf).to_be_hidden()

    # click on the second tab and verify that the PDF is visible
    tab1.click()

    iframe_frame_1 = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(1)
    pdf_container_1 = iframe_frame_1.locator('div[id="pdfContainer"]')
    expect(pdf_container_1).to_be_visible()

    b_box_1 = pdf_container_1.bounding_box()
    assert b_box_1['height'] == 300
    # The second part of the If tests that the width < height, which indicate that we have resized
    # the PDF to keep the proportions
    assert round(b_box_1['width']) < iframe_box['width'] and round(b_box_1['width']) < round(b_box_1['height'])

    pdf_viewer_1 = iframe_frame_1.locator('div[id="pdfViewer"]')
    expect(pdf_viewer_1).to_be_visible()

    text_in_pdf = pdf_viewer_1.get_by_text("from LaH10 to room–temperature").nth(0)
    expect(text_in_pdf).to_be_visible()
