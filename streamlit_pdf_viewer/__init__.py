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


def pdf_viewer(input: Union[str, Path, bytes], width="700", height="800", key=None, annotations=[]):
    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(binary=base64_pdf, width=width, height=height, key=key, default=0,
                                      annotations=annotations)
    return component_value


if not _RELEASE:
    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    with open("resources/annotations.json", 'rb') as fo:
        annotations = json.loads(fo.read())

    viewer = pdf_viewer(binary, height="700", width="800", annotations=annotations)
