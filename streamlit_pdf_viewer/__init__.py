import base64
import os
from pathlib import Path
from typing import Union

import streamlit.components.v1 as components

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


def pdf_viewer(input: Union[str, Path, bytes], width="100%", height="700", key=None, annotations=[]):
    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(binary=base64_pdf, width=width, height=height, key=key, default=0,
                                      annotations=annotations)
    return component_value


# viewer = pdf_viewer("resources/test.pdf", height="700", width="700")

if not _RELEASE:
    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    viewer = pdf_viewer(binary, height="700", width="500", annotations=[
        {
            "page": 1,
            "x": 220,
            "y": 155,
            "height": 22,
            "width": 65,
            "color": "red",
        },{
            "page": 2,
            "x": 198,
            "y": 280,
            "height": 7,
            "width": 30,
            "color": "orange",
        }])
