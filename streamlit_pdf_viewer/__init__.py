import base64
import os
from pathlib import Path
from typing import Union

import streamlit.components.v1 as components
import json

_RELEASE = True

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


def pdf_viewer(input: Union[str, Path, bytes], width="700", height=None, key=None, annotations=[], page_margin=2,
               annotation_outline_size=1):
    """
    pdf_viewer function to display a PDF file in a Streamlit app.

    :param input: The source of the PDF file. Accepts a file path, URL, or binary data.
    :param width: Width of the PDF viewer in pixels. Defaults to 700 pixels.
    :param height: Height of the PDF viewer in pixels. If not provided, the viewer show the whole content.
    :param key: An optional key that uniquely identifies this component. Used to preserve state in Streamlit apps.
    :param annotations: A list of annotations to be overlaid on the PDF. Each annotation should be a dictionary.
    :param page_margin: The margin (in pixels) between each page of the PDF. It adjusts the spacing between pages.
                        Defaults to 2 pixels.
    :param annotation_outline_size: Size of the outline around each annotation in pixels.
                        Defaults to 1 pixel.

    The function reads the PDF file (from a file path, URL, or binary data), encodes it in base64,
    and uses a Streamlit component to render it in the app. It supports optional annotations and adjustable margins.

    Returns the value of the selected component (if any).
    """
    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(binary=base64_pdf, width=width, height=height, key=key, default=0,
                                      annotations=annotations, page_margin=page_margin,
                                      annotation_outline_size=annotation_outline_size)
    return component_value


if not _RELEASE:
    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    with open("resources/annotations.json", 'rb') as fo:
        annotations = json.loads(fo.read())

    viewer = pdf_viewer(binary, height="700", width="800", annotations=annotations)
