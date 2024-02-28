import os

import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from tests.test_template_args import ROOT_DIRECTORY

st.subheader("Test PDF Viewer with no arguments")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"))
