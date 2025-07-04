#!/usr/bin/env python3
"""
Setup script for Phastats - Advanced FASTQ Quality Analysis Tool
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure we're using the correct Python version
if sys.version_info < (3, 7):
    sys.exit("Python 3.7 or higher is required")

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read version from __init__.py
version_file = this_directory / "src" / "phastats" / "__init__.py"
version_content = version_file.read_text(encoding='utf-8')

# Extract version
version = None
for line in version_content.split('\n'):
    if line.startswith('__version__'):
        version = line.split('=')[1].strip().strip('"').strip("'")
        break

if not version:
    raise RuntimeError("Unable to find version string")

# Define requirements
install_requires = [
    'matplotlib>=3.3.0,<4.0.0',
    'numpy>=1.19.0,<2.0.0',
    'pandas>=1.1.0,<3.0.0',
    'scipy>=1.5.0,<2.0.0',
]

# Extra requirements for development
extras_require = {
    'dev': [
        'pytest>=6.0.0',
        'pytest-cov>=2.10.0',
        'black>=21.0.0',
        'flake8>=3.8.0',
        'mypy>=0.800',
        'sphinx>=4.0.0',
        'sphinx-rtd-theme>=0.5.0',
    ],
    'web': [
        'Flask>=2.0.0,<4.0.0',
        'Werkzeug>=2.0.0,<4.0.0',
    ],
}

# All extra requirements
extras_require['all'] = [
    req for extra in extras_require.values() for req in extra
]

setup(
    name="phastats",
    version=version,
    author="Your Name",
    author_email="your.email@example.com",
    description="Advanced FASTQ Quality Analysis Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/phastats",
    project_urls={
        "Bug Reports": "https://github.com/your-username/phastats/issues",
        "Source": "https://github.com/your-username/phastats",
        "Documentation": "https://your-username.github.io/phastats/",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "phastats=phastats.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "phastats": ["data/*", "templates/*"],
    },
    zip_safe=False,
    keywords="bioinformatics fastq quality-control sequencing genomics",
    license="MIT",
) 