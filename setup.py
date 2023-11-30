from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit-pdf-viewer",
    version="0.0.1",
    author="Luca Foppiano",
    author_email="lucanoro@duck.com",
    description="Streamlit component for PDF visualisation and manipulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lfoppiano/streamlit-pdf-viewer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=["rag", "streamlit-component", "pdf-viewer", "documents"],
    python_requires=">=3.6",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
        ]
    }
)
