import streamlit as st
import streamlit.components.v1 as components
import os
import base64

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component(
        "my_component",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "my_component", path=build_dir)

# def my_component(file_content, key=None):
#     return _component_func(file_content=file_content, key=key)
#
# uploaded_file = st.file_uploader("Upload an article", type=("pdf", "txt"),
#                                  help="The full-text is extracted using Grobid.")
#
# if uploaded_file is not None:
#     # Read the file appropriately based on its type
#     if uploaded_file.type == "text/plain":
#         # If it's a text file, read it as string
#         file_content = uploaded_file.getvalue().decode("utf-8")
#     elif uploaded_file.type == "application/pdf":
#         # If it's a PDF, read and encode it in base64
#         file_content = base64.b64encode(uploaded_file.read()).decode("utf-8")
#     else:
#         st.error("Unsupported file type!")
#         file_content = None
#
#     if file_content:
#         result = my_component(file_content)
#         # Handle the result from your component
#         if result:
#             st.write("Component returned:", result)

def my_component(input: str, width="100%", height="700", key=None):
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

my_component(binary)
