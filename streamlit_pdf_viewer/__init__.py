import streamlit as st
import streamlit.components.v1 as components
import os
import base64

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "pdf_viewer",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "pdf_viewer", path=build_dir)


def pdf_viewer(input: str, width="100%", height="700", key=None):
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    base64_pdf = base64.b64encode(input).decode('utf-8')
    component_value = _component_func(binary=base64_pdf, width=width, height=height, key=key, default=0)
    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


with open("resources/test.pdf", 'rb') as fo:
    binary = fo.read()

viewer = pdf_viewer(binary, height="700", width="700")
st.write(viewer)