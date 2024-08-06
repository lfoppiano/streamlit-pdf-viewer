import os

import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from tests import ROOT_DIRECTORY

st.subheader("Test PDF Viewer with the PDF in a tab and rendering text")

tab1, tab2 = st.tabs(["tab1", "tab2"])

with tab1:
    pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), render_text=False)

with tab2:
    pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), height=300, render_text=True)
