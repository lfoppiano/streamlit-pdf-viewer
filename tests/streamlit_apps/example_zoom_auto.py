import os

import streamlit as st
from tests import ROOT_DIRECTORY

from streamlit_pdf_viewer import pdf_viewer

st.subheader("Test PDF Viewer with auto zoom (fit to width)")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), width=600, zoom_level=None)