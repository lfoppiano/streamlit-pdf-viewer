import os

import streamlit as st
from streamlit import markdown

from streamlit_pdf_viewer import pdf_viewer
from tests import ROOT_DIRECTORY

st.subheader("Test PDF Viewer with different resolution boosts")

pdf_path = os.path.join(ROOT_DIRECTORY, "resources/test.pdf")

tabs = st.tabs(["tab 1", "tab 2"])

resolution_boost_values = list(range(1, 10, 3))
labels = [f"tab {resolution_boost_value}" for resolution_boost_value in resolution_boost_values]
with tabs[0]:
    for id, column in enumerate(st.columns(len(labels))):
        with column:
            markdown(f"Resolution boost: {resolution_boost_values[id]}")
            pdf_viewer(pdf_path, width=200, render_text=False, resolution_boost=resolution_boost_values[id])

with tabs[1]:
    for id, column in enumerate(st.columns(len(labels))):
        with column:
            markdown(f"Resolution boost: {resolution_boost_values[id]}")
            pdf_viewer(pdf_path, width=200, render_text=True, resolution_boost=resolution_boost_values[id])