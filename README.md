# streamlit-pdf-viewer

Component allowing the visualisation and manipulation of PDF documents in streamlit 

## Installation instructions

```sh
pip install streamlit-pdf-viewer
```

## Usage instructions

```python
import streamlit as st
from streamlit_pdf_viewer import pdf_viewer

value = st.pdf_viewer(file="file or path")

st.write(value)
```


## For Developers

### Environment 
- Python >= 3.8
- Node.js >= 16
- Streamlit 1.28.2

### Configure environment for development

First make sure that _RELEASE = False in `streamlit_pdf_viewer/__init__.py`. 
To run the component in development mode, use the following commands:

```shell
streamlit run my_component/__init__.py

cd frontend
npm run serve
```

These commands will start the Streamlit application and serve the Node.js component, respectively. 
Ensure you're in the correct directory before running these commands.

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