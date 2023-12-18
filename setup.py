from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()
bump_version = (this_directory / ".bumpversion.toml").read_text()
current_version_line = [line for line in bump_version.split('\n') if 'current_version' in line][0]
version = current_version_line.split('=')[1].strip().strip('"')

setuptools.setup(
    name="streamlit-pdf-viewer",
    version=version,
    author="Luca Foppiano, Tomoya Mato",
    author_email="lucanoro@duck.com, tomoya.matou@gmail.com",
    description="Streamlit component for PDF visualisation and manipulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lfoppiano/streamlit-pdf-viewer",
    packages=setuptools.find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "streamlit >= 0.63"
    ],
    extras_require={
        "devel": [
            "wheel"
        ]
    }
)
