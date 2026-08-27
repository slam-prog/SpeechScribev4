"""
SpeechScribe V4 - Setup script.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Google AI (Gemini)

Usage:
    pip install -e .
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="speechscribe",
    version="4.0.0",
    author="NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL",
    author_email="walidddhony@gmail.com",
    description="Ultra-Fast Speech Transcription using NumPy Vectorization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/slam-prog/SpeechScribe",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "PyQt5>=5.15.0",
        "pydub>=0.25.0",
    ],
    entry_points={
        "console_scripts": [
            "speechscribe=run_cli:main",
            "speechscribe-gui=run_gui:main",
        ],
    },
    keywords="speech transcription audio numpy multi-language humanitarian",
    project_urls={
        "Bug Reports": "https://github.com/slam-prog/SpeechScribe/issues",
        "Source": "https://github.com/slam-prog/SpeechScribe",
    },
)