import os
from math import ceil, floor
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_alignment_center.py")


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


def test_should_render_with_center_alignment(page: Page):
    expect(page.get_by_text("Test PDF Viewer with center alignment")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    expect(iframe_component).to_be_visible()

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    # Verify PDF viewer is present and has content
    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

    canvas_list = pdf_viewer.locator("canvas").all()
    assert len(canvas_list) > 0
    for canvas in canvas_list:
        expect(canvas).to_be_visible()


def test_center_alignment_positioning(page: Page):
    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    
    # Get the main container that should have alignment styles applied
    main_container = iframe_frame.locator('div.container-wrapper')
    expect(main_container).to_be_visible()
    
    # For center alignment, check that the margins are equal (indicating centering)
    margin_left = main_container.evaluate("el => getComputedStyle(el).marginLeft")
    margin_right = main_container.evaluate("el => getComputedStyle(el).marginRight")
    
    # Convert margin values to numbers for comparison
    left_value = float(margin_left.replace('px', ''))
    right_value = float(margin_right.replace('px', ''))
    
    # For center alignment: left and right margins should be approximately equal
    margin_diff = abs(left_value - right_value)
    assert margin_diff < 5, f"Expected left and right margins to be equal for center alignment. Left: {margin_left}, Right: {margin_right}, Difference: {margin_diff}px" 