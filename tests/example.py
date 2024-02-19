import os

import streamlit as st

from tests.test_template import ROOT_DIRECTORY
from streamlit_pdf_viewer import pdf_viewer

st.subheader("Test PDF Viewer")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"))

def click():
    pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), width=400, height=400)

st.button("Set size", on_click=click)
