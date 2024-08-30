[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)
[![PyPI version](https://badge.fury.io/py/streamlit-pdf-viewer.svg)](https://badge.fury.io/py/streamlit-pdf-viewer)
[![Build](https://github.com/lfoppiano/streamlit-pdf-viewer/actions/workflows/ci-build.yml/badge.svg)](https://github.com/lfoppiano/streamlit-pdf-viewer/actions/workflows/ci-build.yml)
[![Coverage Status](https://coveralls.io/repos/github/lfoppiano/streamlit-pdf-viewer/badge.svg)](https://coveralls.io/github/lfoppiano/streamlit-pdf-viewer)

# streamlit-pdf-viewer

Streamlit component that allows the visualisation and enrichment of PDF documents.
You can see an [application](https://github.com/lfoppiano/structure-vision) in action [here](https://structure-vision.streamlit.app/).

<img src="https://github.com/lfoppiano/streamlit-pdf-viewer/raw/main/docs/screenshot.png" width=500 align="right" />

## Features
- Show PDF files in a Streamlit application with a simple command
- Based on the pdf.js library
- Support showing the PDF with the native pdf.js browser's viewer: "legacy" (with limitations, no annotations, no scrolling, etc..) 
- Visualize annotations on top of the PDF documents
- Render text on top of the PDF document, allowing copy-paste
- Allow to render specific pages of the PDF document
- Scroll to a specific page
- Scroll to a specific annotation

## Limitations
- Tested and developed to support Firefox and Chrome.
- The legacy visualization works only on Firefox and does not support annotations 
- Our Javascript skills are limited, so all troubleshooting may take time 
- The component is still in development, so expect some bugs and limitations
- The streamlit reload at each action may render slowly for complex PDF documents


## Getting started

```sh
pip install streamlit-pdf-viewer
```

In your streamlit application, you can use it as:

```python
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

pdf_viewer("str, path or bytes")
```

### Caveats 

Here some caveats to be aware of: 
- Is mandatory to specify a `width` to show PDF document on tabs and expanders, otherwise, the viewer will not be displayed on tabs not immediately visible.  
- The `legacy` rendering is not supported on Chrome, due to security reasons.


### Params

In the following table the list of parameters that can be provided to the `pdf_viewer` function:

| name                    | description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
|-------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| input                   | The source of the PDF file. Accepts a file path, URL, or binary data.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| width                   | Width of the PDF viewer in pixels. It defaults to 700 pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| height                  | Height of the PDF viewer in pixels. If not provided, the viewer shows the whole content.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| annotations             | A list of annotations to be overlaid on the PDF. Format is described here.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| pages_vertical_spacing  | The vertical space (in pixels) between each page of the PDF. Defaults to 2 pixels.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| annotation_outline_size | Size of the outline around each annotation in pixels. Defaults to 1 pixel.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| rendering               | Type of rendering: `unwrap` (default), `legacy_iframe`, or `legacy_embed`. The default value, `unwrap` shows the PDF document using pdf.js, and supports the visualisation of annotations. Other values are `legacy_iframe` and `legacy_embed` which use the legacy approach of injecting the document into an `<embed>` or `<iframe>`. They allow viewing the PDF using the viewer of the browser that contains additional features we are still working to implement in this component. **IMPORTANT**: :warning: The "legacy" methods **work only with Firefox**, and **do not support annotations**. :warning: |
| pages_to_render         | Filter the rendering to a specific set of pages. By default, all pages are rendered.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| render_text             | Enable a layer of text on top of the PDF document. The text may be selected and copied. **NOTE** to avoid breaking existing deployments, we made this optional at first, also considering that having many annotations might interfere with the copy-paste.                                                                                                                                                                                                                                                                                                                                                       
| scroll_to_page          | Scroll to a specific page when the component is rendered. Default is None. Require ints and ignores the parameters below zero.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| scroll_to_annotation    | Scroll to a specific annotation when the component is rendered. Default is None. Mutually exclusive with `scroll_to_page`. Raise an exception if used with `scroll_to_page`                                                                                                                                                                                                                                                                                                                                                                                                                                        |   


### Annotation format 
The annotations format has been derived from the [Grobid's coordinate formats](https://grobid.readthedocs.io/en/latest/Coordinates-in-PDF/), which are described as a list of "bounding boxes".
The annotations are expressed as a dictionary of six elements, the page, x and y indicate the top left point. The color can be expressed following the html CSS convention. 

Here an example: 

```json
[
   {
      "page": 1,
      "x": 220,
      "y": 155,
      "height": 22,
      "width": 65,
      "color": "red"
   },
[...]
```

The example shown in our screenshot can be found [here](resources/annotations.json).

## Developers notes

### Environment

- Python >= 3.8
- Node.js >= 16
- Streamlit >= 1.28.2

### Configure environment for development

First, make sure that _RELEASE = False in `streamlit_pdf_viewer/__init__.py`. To run the component in development mode, use the following commands:

```shell
streamlit run streamlit_pdf_viewer/__init__.py

cd frontend
npm run serve
```

These commands will start the Streamlit application and serve the Node.js component. Please make sure you're in the correct directory before running these commands.

### Integrate into a streamlit application

1. Build the frontend part:

    ```shell
    cd frontend
    export NODE_OPTIONS=--openssl-legacy-provider
    npm run build 
    ```

1. Make sure that _RELEASE = True in `streamlit_pdf_viewer/__init__.py`.

2. move to the streamlit_application and run

    ```shell
    pip install -e {path of component}
    ```

### Release

```shell 
bump-my-version bump patch | minor | major
```

```shell
git push
git push --tags 
```

## Acknowledgement

The project was initiated at the [National Institute for Materials Science](https://www.nims.go.jp) (NIMS) in Japan.
Currently, the development is possible thanks to [ScienciLAB](https://www.sciencialab.com).
Main collaborator: [Tomoya Mato](https://github.com/t29mato) very helpful to attenuate the pain of Javascript. 
