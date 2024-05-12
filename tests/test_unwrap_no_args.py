import os
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect

from tests import ROOT_DIRECTORY
from tests.e2e_utils import StreamlitRunner

BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "streamlit_apps", "example_unwrap_no_args.py")


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
    expect(page.get_by_text("Test PDF Viewer with no args")).to_be_visible()

    iframe_component = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    expect(iframe_component).to_be_visible()

    iframe_box = iframe_component.bounding_box()
    assert iframe_box['width'] > 0
    assert iframe_box['height'] > 0

    iframe_frame = page.frame_locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]')
    pdf_container = iframe_frame.locator('div[id="pdfContainer"]')
    expect(pdf_container).to_be_visible()

    b_box = pdf_container.bounding_box()
    # Since we do not specify the width, we occupy all the available space, which should correspond to the
    # parent element's width of the pdfContainer.
    assert b_box['width'] == iframe_box['width']
    assert b_box['height'] > 0

    pdf_viewer = iframe_frame.locator('div[id="pdfViewer"]')
    expect(pdf_viewer).to_be_visible()

    canvas_list = pdf_viewer.locator("canvas").all()
    assert len(canvas_list) == 8
    for canvas in canvas_list:
        expect(canvas).to_be_visible()

    annotations_locator = page.locator('div[id="pdfAnnotations"]').nth(0)
    expect(annotations_locator).to_be_hidden()

# def test_should_render_template(page: Page):
#     frame_0 = page.frame_locator(
#         'iframe[title="my_component\\.my_component"]'
#     ).nth(0)
#     frame_1 = page.frame_locator(
#         'iframe[title="my_component\\.my_component"]'
#     ).nth(1)
#
#     st_markdown_0 = page.get_by_role('paragraph').nth(0)
#     st_markdown_1 = page.get_by_role('paragraph').nth(1)
#
#     expect(st_markdown_0).to_contain_text("You've clicked 0 times!")
#
#     frame_0.get_by_role("button", name="Click me!").click()
#
#     expect(st_markdown_0).to_contain_text("You've clicked 1 times!")
#     expect(st_markdown_1).to_contain_text("You've clicked 0 times!")
#
#     frame_1.get_by_role("button", name="Click me!").click()
#     frame_1.get_by_role("button", name="Click me!").click()
#
#     expect(st_markdown_0).to_contain_text("You've clicked 1 times!")
#     expect(st_markdown_1).to_contain_text("You've clicked 2 times!")
#
#     page.get_by_label("Enter a name").click()
#     page.get_by_label("Enter a name").fill("World")
#     page.get_by_label("Enter a name").press("Enter")
#
#     expect(frame_1.get_by_text("Hello, World!")).to_be_visible()
#
#     frame_1.get_by_role("button", name="Click me!").click()
#
#     expect(st_markdown_0).to_contain_text("You've clicked 1 times!")
#     expect(st_markdown_1).to_contain_text("You've clicked 3 times!")
#
#
# def test_should_change_iframe_height(page: Page):
#     frame = page.frame_locator('iframe[title="my_component\\.my_component"]').nth(1)
#
#     expect(frame.get_by_text("Hello, Streamlit!")).to_be_visible()
#
#     locator = page.locator('iframe[title="my_component\\.my_component"]').nth(1)
#
#     init_frame_height = locator.bounding_box()['height']
#     assert init_frame_height != 0
#
#     page.get_by_label("Enter a name").click()
#
#     page.get_by_label("Enter a name").fill(35 * "Streamlit ")
#     page.get_by_label("Enter a name").press("Enter")
#
#     expect(frame.get_by_text("Streamlit Streamlit Streamlit")).to_be_visible()
#
#     frame_height = locator.bounding_box()['height']
#     assert frame_height > init_frame_height
#
#     page.set_viewport_size({"width": 150, "height": 150})
#
#     expect(frame.get_by_text("Streamlit Streamlit Streamlit")).not_to_be_in_viewport()
#
#     frame_height_after_viewport_change = locator.bounding_box()['height']
#     assert frame_height_after_viewport_change > frame_height
