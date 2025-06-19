import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
import os

st.set_page_config(layout="wide")

st.title("Streamlit PDF Viewer - New Features Demo")

pdf_file = os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'test.pdf')

with open(pdf_file, "rb") as f:
    binary_pdf = f.read()

st.sidebar.header("Viewer Controls")

# Zoom control
zoom_level = None if st.sidebar.checkbox("Fit to Width", value=True) else st.sidebar.slider("Initial Zoom Level", min_value=0.1, max_value=4.0, value=1.0, step=0.1)

# Alignment control
align = st.sidebar.selectbox("Viewer Alignment", options=["center", "left", "right"], index=0)

# Page separator control
show_separator = st.sidebar.checkbox("Show Page Separator", value=True)


st.markdown("### PDF Viewer with Controls")
st.info("💡 **New Feature**: Hover over the zoom button in the bottom-right corner of the PDF viewer to access zoom controls including preset levels, fit-to-width, fit-to-height, and actual size options!")

pdf_viewer(
    binary_pdf,
    width="100%",
    height=800,
    zoom_level=zoom_level,
    viewer_align=align,
    show_page_separator=show_separator,
    render_text=True,
)

st.markdown("---")
st.markdown("### Pre-set examples")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Zoomed-in View (Zoom Level 2.0)")
    pdf_viewer(
        binary_pdf,
        height=500,
        zoom_level=2.0,
        key="zoomed"
    )

with col2:
    st.subheader("Fit to Container Width")
    pdf_viewer(
        binary_pdf,
        width="100%",
        height=500,
        key="fit_width"
    )

st.subheader("Right-aligned View")
pdf_viewer(
    binary_pdf,
    width=700,
    height=500,
    viewer_align="right",
    key="right_aligned"
)
st.subheader("Left-aligned View")
pdf_viewer(
    binary_pdf,
    width=800,
    height=500,
    viewer_align="left",
    key="left_aligned"
)

st.subheader("Without Page Separator")
pdf_viewer(
    binary_pdf,
    height=500,
    show_page_separator=False,
    key="no_separator"
) 