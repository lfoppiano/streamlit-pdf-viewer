from pathlib import Path
import os
import subprocess
import sys

import setuptools

def build_frontend():
    """Build the Vue frontend during installation."""
    frontend_dir = Path(__file__).parent / "streamlit_pdf_viewer" / "frontend"
    dist_dir = frontend_dir / "dist"
    
    if not frontend_dir.exists():
        print("Frontend directory not found, skipping build")
        return
    
    # Check if dist directory exists and contains built files
    if dist_dir.exists() and any(dist_dir.iterdir()):
        print("Frontend already built, skipping build step")
        return
    
    print("Building Vue frontend...")
    
    # Check if npm is available
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("npm not found. Please install Node.js and npm to build the frontend.")
        return
    
    # Install dependencies
    try:
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
        print("npm dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install npm dependencies: {e}")
        return
    
    # Build the frontend
    try:
        subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
        print("Vue frontend built successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build Vue frontend: {e}")
        return

# Build frontend during installation
build_frontend()

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
