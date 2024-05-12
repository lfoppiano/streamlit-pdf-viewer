import os

import streamlit as st

from streamlit_pdf_viewer import pdf_viewer
from tests import ROOT_DIRECTORY

st.subheader("Test PDF Viewer using legacy embed with specified height")

pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), rendering='unwrap', height='500')
pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), rendering='unwrap', width='500')
pdf_viewer(os.path.join(ROOT_DIRECTORY, "resources/test.pdf"), rendering='unwrap', width='500', height='500')
