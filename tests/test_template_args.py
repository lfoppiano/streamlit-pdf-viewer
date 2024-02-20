import os
from pathlib import Path

import pytest

from playwright.sync_api import Page, expect

from tests.e2e_utils import StreamlitRunner

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()
BASIC_EXAMPLE_FILE = os.path.join(ROOT_DIRECTORY, "tests", "example_args.py")


@pytest.fixture(autouse=True, scope="module")
def streamlit_app():
    with StreamlitRunner(Path(BASIC_EXAMPLE_FILE)) as runner:
        yield runner


@pytest.fixture(autouse=True, scope="function")
def go_to_app(page: Page, streamlit_app: StreamlitRunner):
    page.goto(streamlit_app.server_url)
    # Wait for app to load
    page.get_by_role("img", name="Running...").is_hidden()


def test_should_render_template(page: Page):
    expect(page.get_by_text("Test PDF Viewer with arguments")).to_be_visible()

    locator = page.locator('iframe[title="streamlit_pdf_viewer.streamlit_pdf_viewer"]').nth(0)
    expect(locator).to_be_visible()

    width = locator.bounding_box()['width']
    height = locator.bounding_box()['height']
    assert width > 0
    # assert height > 0
    # The height and width are not uniform against different python and node versions


def test_should_render_template_check_container_size(page: Page):
    expect(page.get_by_text("Test PDF Viewer with arguments")).to_be_visible()
    container_locator = page.locator('div[id="pdfContainer"]').nth(0)

    expect(container_locator.is_visible())
    b_box = container_locator.bounding_box()
    expect(b_box['width'] == 400)
    expect(b_box['height'] == 300)
