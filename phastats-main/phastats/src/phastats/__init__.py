"""
Phastats: Advanced FASTQ Quality Control Analysis Tool

A comprehensive tool for analyzing FASTQ files with detailed quality control metrics,
visualizations, and multiple output formats.
"""

__version__ = "2.1.0"
__author__ = "Phastats Development Team"
__email__ = "phastats@example.com"
__description__ = "Advanced FASTQ Quality Control Analysis Tool"

# Import main functionality
from .core import analyze_fastq
from .parser import parse_fastq_file
from .plotting import create_plots
from .reports import generate_report
from .cli import main

# Define what gets imported with "from phastats import *"
__all__ = [
    'analyze_fastq',
    'parse_fastq_file', 
    'create_plots',
    'generate_report',
    'main',
    '__version__'
]