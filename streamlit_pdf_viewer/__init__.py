import base64
import os
from pathlib import Path
from typing import Union, List, Optional

import streamlit.components.v1 as components
import json

_RELEASE = True
RENDERING_EMBED = "legacy_embed"
RENDERING_IFRAME = "legacy_iframe"
RENDERING_UNWRAP = "unwrap"

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/dist")
    _component_func = components.declare_component(
        "streamlit_pdf_viewer",
        path=build_dir
    )


def pdf_viewer(
        input: Union[str, Path, bytes],
        width: int = None,
        height: int = None,
        key=None,
        annotations: list = (),
        pages_vertical_spacing: int = 2,
        annotation_outline_size: int = 1,
        rendering: str = RENDERING_UNWRAP,
        pages_to_render: List[int] = (),
        render_text: bool = False,
        resolution_boost: int = 1,
        scroll_to_page: int = None,
        scroll_to_annotation: int = None,
):
    """
    pdf_viewer function to display a PDF file in a Streamlit app.

    :param input: The source of the PDF file. Accepts a file path, URL, or binary data.
    :param width: Width of the PDF viewer in pixels. Defaults to 700 pixels.
    :param height: Height of the PDF viewer in pixels. If not provided, the viewer show the whole content.
    :param key: An optional key that uniquely identifies this component. Used to preserve state in Streamlit apps.
    :param annotations: A list of annotations to be overlaid on the PDF. Each annotation should be a dictionary.
    :param pages_vertical_spacing: The vertical space (in pixels) between each page of the PDF. Defaults to 2 pixels.
    :param annotation_outline_size: Size of the outline around each annotation in pixels. Defaults to 1 pixel.
    :param rendering: Type of rendering. The default is "unwrap", which unwrap the PDF. Other values are
    :param pages_to_render: Optional list of page numbers to render. If None, all pages are rendered. This allows for selective rendering of pages in the PDF.
    "legacy_iframe" and "legacy_embed" which uses the legacy approach for showing PDF document with streamlit.
    These methods enable the default pdf viewer of Firefox/Chrome/Edge that contains additional features we are still
    working to implement for the "unwrap" method.
    :param render_text: Whether to enable selection of text in the PDF viewer. Defaults to False.
    :param resolution_boost: Boost the resolution by a factor from 2 to 10. Defaults to 1.
    :param scroll_to_page: Scroll to a specific page in the PDF. The parameter is an integer, which represent the positional value of the page. E.g. 1, will be the first page. Defaults to None.
    :param scroll_to_annotation: Scroll to a specific annotation in the PDF. The parameter is an integer, which represent the positional value of the annotation. E.g. 1, will be the first annotation. Defaults to None.

    The function reads the PDF file (from a file path, URL, or binary data), encodes it in base64,
    and uses a Streamlit component to render it in the app. It supports optional annotations and adjustable margins.

    Returns the value of the selected component (if any).
    """

    # Validate width and height parameters
    if width is not None and not isinstance(width, int):
        raise TypeError("Width must be an integer")
    if height is not None and not isinstance(height, int):
        raise TypeError("Height must be an integer or None")
    if not all(isinstance(page, int) for page in pages_to_render):
        raise TypeError("pages_to_render must be a list of integers")

    if resolution_boost < 1:
        raise ValueError("ratio_boost must be greater than 1")
    elif resolution_boost > 10:
        raise ValueError("ratio_boost must be lower than 10")

    if scroll_to_page is not None:
        if scroll_to_annotation is not None:
            raise ValueError("scroll_to_page and scroll_to_annotation cannot be used together")
        if scroll_to_page is not None and scroll_to_page < 1:
            scroll_to_page = None

    else:
        if scroll_to_annotation is not None and scroll_to_annotation < 1:
            scroll_to_annotation = None

    if type(input) is not bytes:
        with open(input, 'rb') as fo:
            binary = fo.read()
    else:
        binary = input

    if rendering == RENDERING_IFRAME or rendering == RENDERING_EMBED:
        print(f"{RENDERING_IFRAME} and {RENDERING_EMBED} may not work consistently on all browsers "
              f"they might disapper in future releases.")
        if height is None:
            height = "100%"

    base64_pdf = base64.b64encode(binary).decode('utf-8')
    component_value = _component_func(
        binary=base64_pdf,
        width=width,
        height=height,
        key=key,
        default=0,
        annotations=annotations,
        pages_vertical_spacing=pages_vertical_spacing,
        annotation_outline_size=annotation_outline_size,
        rendering=rendering,
        pages_to_render=pages_to_render,
        render_text=render_text,
        resolution_boost=resolution_boost,
        scroll_to_page=scroll_to_page,
        scroll_to_annotation=scroll_to_annotation
    )
    return component_value


if not _RELEASE:
    import streamlit as st
    from streamlit import markdown

    # from glob import glob

    # paths = glob("/Users/lfoppiano/kDrive/library/articles/materials informatics/polymers/*.pdf")
    # path = "/Users/lfoppiano/development/projects/alirahelth/data/articles/Basso Dias RAD 2022.pdf"
    # values = list(range(1, 10))
    # for id, tab in enumerate(st.tabs([f"tab {val}" for val in values])):
    #     with tab:
    #         with st.container(height=600):
    #             pdf_viewer(path, width=800, render_text=True, resolution_boost=values[id])
    #
    # def scroll_to_page(page):
        # st.markdown(
        #     """
        #     function(){
        #         document.getElementById(""" + page + """).scrollIntoView({behavior: 'smooth'})
        #     };
        #
        #     function()
        #     """, unsafe_allow_html=True)

        # print(page)
        # st.components.v1.html(
        #     """
        #     <script>
        #         function scrollDown(){
        #             page_canvas = document.getElementById('""" + page + """')
        #             console.log(page_canvas)
        #             page_canvas.scrollIntoView({behavior: 'smooth'})
        #         }
        #         scrollDown()
        #     </script>
        #     """
        # )

    with open("resources/test.pdf", 'rb') as fo:
        binary = fo.read()

    with open("resources/test.pdf", 'rb') as fo:
        binary2 = fo.read()

    with open("resources/annotations.sample.json", 'rb') as fo:
        annotations = json.loads(fo.read())

    tab1, tab2 = st.tabs(["tab1", "tab2"])

    # st.markdown("""
    #     <style>
    #     * {
    #     overflow-anchor: none !important;
    #     }
    #     </style>""", unsafe_allow_html=True)
    # @st.fragment
    # def show_buttons_scrolling(pages_id: List):
    #     for page in pages_id:
    #         print(page)
    #         st.button(f"Page {page}", key=f"page_{page}", on_click=scroll_to_page, args=(page,))

    with tab1:
        st.markdown("tab 1")
        with st.container(height=400):
            viewer = pdf_viewer(
                binary,
                annotations=annotations,
                render_text=True,
                key="bao",
                scroll_to_page=3
            )
        # st.markdown(viewer)
        # st.markdown(type(viewer))
        # if type(viewer) == dict:
        #     annotations_id = viewer['annotations']
        #     pages_id = viewer['pages']
        #     show_buttons_scrolling(pages_id)

    with tab2:
        st.markdown("tab 2")
        viewer2 = pdf_viewer(
            binary2,
            height=500,
            annotations=annotations,
            render_text=True,
            key="miao",
            resolution_boost=4,
            scroll_to_annotation=2
        )


## Issue with Chrome

    # from glob import glob
    #
    # # paths = glob("/Users/lfoppiano/kDrive/library/articles/materials informatics/polymers/*.pdf")
    # paths = glob("/Users/lfoppiano/development/projects/alirahelth/data/articles/*.pdf")
    # for id, (tab, path) in enumerate(zip(st.tabs(paths),paths)):
    #     with tab:
    #         with st.container(height=600):
    #             if id == 0:
    #                 pdf_viewer(path, width=500, render_text=True)
    #             else:
    #                 pdf_viewer(path, width=1000, render_text=True)