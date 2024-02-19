import os

import streamlit as st

from e2e.test_template import ROOT_DIRECTORY
from streamlit_pdf_viewer import pdf_viewer

# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`

st.subheader("Test PDF Viewer")

# Create an instance of our component with a constant `name` arg, and
# print its output value.
pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), key="viewer")