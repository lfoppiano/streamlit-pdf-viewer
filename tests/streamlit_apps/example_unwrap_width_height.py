import os

import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from tests import ROOT_DIRECTORY

st.subheader("Test PDF Viewer with specified width and height")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), width=400, height=300)
