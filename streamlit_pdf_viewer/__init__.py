import base64
import os
from pathlib import Path
from typing import Union, List, Optional

import streamlit.components.v1 as components
from streamlit_js_eval import streamlit_js_eval
import json

_RELEASE = True
RENDERING_EMBED = "legacy_embed"
RENDERING_IFRAME = "legacy_iframe"
RENDERING_UNWRAP = "unwrap"

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        path=build_dir
    )

def get_screen_size():
    """
    Returns the inner width and outer height of a window.
    Ideally, it should return the inner height, but JavaScript couldn't retrieve the height in an iframe.
    """
    async_js_code = """
    new Promise(resolve => {
        if (document.readyState === "complete") {
            resolve([window.innerWidth, window.outerHeight]);
        } else {
            window.addEventListener("load", () => resolve([window.innerWidth, window.outerHeight]));
        }
    })
    """
    return streamlit_js_eval(js_expressions=async_js_code)

def pdf_viewer(input: Union[str, Path, bytes],
               width: int = None,
               height: int = None, 
               key=None,
               annotations: list = (),
               pages_vertical_spacing: int = 2,
               annotation_outline_size: int = 1,
               rendering: str = RENDERING_UNWRAP,
               pages_to_render: List[int] = ()
               ):
    """
    pdf_viewer function to display a PDF file in a Streamlit app.

    :param input: The source of the PDF file. Accepts a file path, URL, or binary data.
    :param width: The width of the PDF viewer defaults to 100% of the layout. Specify in pixels with a numeric value, or as a percentage for relative sizing.
    :param height: Height of the PDF viewer in pixels. If not provided, the viewer show the whole content.
    :param key: An optional key that uniquely identifies this component. Used to preserve state in Streamlit apps.
    :param annotations: A list of annotations to be overlaid on the PDF. Each annotation should be a dictionary.
    :param pages_vertical_spacing: The vertical space (in pixels) between each page of the PDF. Defaults to 2 pixels.
    :param annotation_outline_size: Size of the outline around each annotation in pixels. Defaults to 1 pixel.
    :param rendering: Type of rendering. The default is "unwrap", which unwrap the PDF. Other values are
    :param pages_to_render: Optional list of page numbers to render. If None, all pages are rendered. This allows for selective rendering of pages in the PDF.
    "legacy_iframe" and "legacy_embed" which uses the legacy approach for showing PDF document with streamlit.
    These methods enable the default pdf viewer of Firefox/Chrome/Edge that contains additional features we are still
    working to implement for the "unwrap" method.

    The function reads the PDF file (from a file path, URL, or binary data), encodes it in base64,
    and uses a Streamlit component to render it in the app. It supports optional annotations and adjustable margins.

    Returns the value of the selected component (if any).
    """

    screen_width, screen_height = get_screen_size()

    if isinstance(width, str) and width.endswith('%'):
        percentage_width = float(width[:-1]) / 100
        width = int(screen_width * percentage_width)
    elif width is not None and not isinstance(width, int):
        raise TypeError("Width must be an integer or a percentage string (e.g., '70%' or 700) or None")

    if isinstance(height, str) and height.endswith('%'):
        percentage_height = float(height[:-1]) / 100
        height = int(screen_height * percentage_height)
    elif height is not None and not isinstance(height, int):
        raise TypeError("Height must be an integer, a percentage string (e.g., '70%'), or None")

    if not all(isinstance(page, int) for page in pages_to_render):
        raise TypeError("pages_to_render must be a list of integers")

    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    if rendering == RENDERING_IFRAME or rendering == RENDERING_EMBED:
        print(f"{RENDERING_IFRAME} and {RENDERING_EMBED} may not work consistently on all browsers "
                     f"they might disapper in future releases.")
        if height is None:
            height = "100%"

    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(
        binary=base64_pdf,
        width=width,
        height=height,
        key=key,
        default=0,
        annotations=annotations,
        pages_vertical_spacing=pages_vertical_spacing,
        annotation_outline_size=annotation_outline_size,
        rendering=rendering,
        pages_to_render=pages_to_render
    )
    return component_value


if not _RELEASE:
    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    with open("resources/annotations.json", 'rb') as fo:
        annotations = json.loads(fo.read())

    viewer = pdf_viewer(
        binary,
        # height=700,
        width=800,
        annotations=annotations
    )
