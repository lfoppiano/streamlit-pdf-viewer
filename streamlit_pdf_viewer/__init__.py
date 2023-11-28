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
    """Create a new instance of "my_component".
    Parameters
    ----------
    name: str
        The name of the thing we're saying hello to. The component will display
        the text "Hello, {name}!"
    key: str or None
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.
    """
    # "default" is a special argument that specifies the initial return
    # value of the component before the user has interacted with it.
    base64_pdf = base64.b64encode(input).decode('utf-8')
    print(width)
    component_value = _component_func(binary=base64_pdf, width=width, height=height, key=key, default=0)
    # We could modify the value returned from the component if we wanted.
    # There's no need to do this in our simple example - but it's an option.
    return component_value


with open("resources/test.pdf", 'rb') as fo:
    binary = fo.read()

pdf_viewer(binary)
