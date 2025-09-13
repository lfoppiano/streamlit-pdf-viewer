import os

import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from tests import ROOT_DIRECTORY

st.subheader("Test PDF Viewer with the PDF in a tab")

tab1, tab2 = st.tabs(["tab1", "tab2"])

with tab1:
    pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"))

with tab2:
    pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), width=300)
