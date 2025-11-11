"""
Setup configuration for audio_intelligence package
"""

from setuptools import setup, find_packages

setup(
    name="audio-intelligence",
    version="0.1.0",
    description="Smart audio analysis tool for acoustic measurement engineers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "librosa>=0.10.0",
        "soundfile>=0.12.0",
        "sounddevice>=0.4.6",
        "agent-framework-azure-ai",
        "openai>=1.30.0",
        "pandas>=2.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.15.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "jupyter": ["jupyter>=1.0.0", "ipywidgets>=8.0.0"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=5.0.0"],
    },
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "audio-intelligence=audio_intelligence.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)