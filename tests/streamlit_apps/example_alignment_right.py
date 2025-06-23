import os

import streamlit as st
from tests import ROOT_DIRECTORY

from streamlit_pdf_viewer import pdf_viewer

st.subheader("Test PDF Viewer with right alignment")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), width=400, viewer_align="right")