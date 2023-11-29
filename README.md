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


## Development Environment

- Python 3.8
- Node.js 16
- Streamlit 1.28.2

## Starting Development

To initialise the development environment, use the following commands:

```shell
streamlit run my_component/__init__.py

cd frontend
npm run serve
```

These commands will start the Streamlit application and serve the Node.js component, respectively. Ensure you're in the correct directory before running these commands.