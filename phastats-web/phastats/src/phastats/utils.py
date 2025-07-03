"""
Utility functions for phastats.

This module contains helper functions for file operations, statistics calculations,
and other utility operations used throughout the package.
"""

import os
import gzip
import numpy as np
from pathlib import Path
from datetime import datetime


def open_fastq_file(filename):
    """
    Open a FASTQ file, automatically detecting if it's compressed (.gz) or not.
    Returns a file object and a boolean indicating if the file is compressed.
    """
    is_compressed = filename.lower().endswith('.gz')
    
    if is_compressed:
        # Open compressed file in text mode
        file_obj = gzip.open(filename, 'rt', encoding='utf-8')
    else:
        # Open regular text file
        file_obj = open(filename, 'r', encoding='utf-8')
    
    return file_obj, is_compressed


def detect_file_type(filename):
    """
    Detect the file type based on filename extension.
    Returns a string describing the file type.
    """
    filename_lower = filename.lower()
    
    if filename_lower.endswith('.fastq.gz') or filename_lower.endswith('.fq.gz'):
        return 'FASTQ (gzip compressed)'
    elif filename_lower.endswith('.fastq') or filename_lower.endswith('.fq'):
        return 'FASTQ'
    else:
        # Default assumption
        return 'FASTQ (assumed)'


def create_output_directory(input_filename):
    """
    Create a unique output directory based on input filename and timestamp.
    Returns the output directory path and a base name for files.
    """
    # Extract base name from input file (without path and extension)
    input_path = Path(input_filename)
    base_name = input_path.stem
    
    # Remove .gz extension if present
    if base_name.endswith('.gz'):
        base_name = base_name[:-3]
    
    # Remove common FASTQ extensions
    if base_name.endswith('.fastq') or base_name.endswith('.fq'):
        base_name = base_name.rsplit('.', 1)[0]
    
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory name
    output_dir = f"phastats_output_{base_name}_{timestamp}"
    
    # Create the directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create plots subdirectory
    plots_dir = Path(output_dir) / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    
    return output_dir, base_name


def get_plot_path(output_dir, plot_name):
    """
    Generate the full path for a plot file within the output directory.
    """
    return os.path.join(output_dir, "plots", plot_name)


def calculate_gc_content(gc_count, total_length):
    """
    Calculate GC content percentage.
    """
    return (gc_count / total_length * 100) if total_length > 0 else 0


def compute_n50(lengths):
    """
    Compute N50 value from a list of sequence lengths.
    
    Args:
        lengths (list): List of sequence lengths
    
    Returns:
        int: N50 value
    """
    if not lengths:
        return 0
    
    sorted_lengths = sorted(lengths, reverse=True)
    total_length = sum(sorted_lengths)
    target_length = total_length / 2
    
    cumulative_length = 0
    for length in sorted_lengths:
        cumulative_length += length
        if cumulative_length >= target_length:
            return length
    
    return sorted_lengths[-1]


def compute_n50_optimized(lengths):
    """
    Optimized N50 calculation using NumPy for better performance.
    
    Args:
        lengths (list): List of sequence lengths
    
    Returns:
        int: N50 value
    """
    if not lengths:
        return 0
    
    # Convert to numpy array and sort in descending order
    lengths_array = np.array(lengths)
    sorted_lengths = np.sort(lengths_array)[::-1]
    
    # Calculate cumulative sum
    cumsum = np.cumsum(sorted_lengths)
    total_length = cumsum[-1]
    
    # Find N50
    target = total_length / 2
    n50_index = np.where(cumsum >= target)[0]
    
    if len(n50_index) > 0:
        return int(sorted_lengths[n50_index[0]])
    else:
        return int(sorted_lengths[-1])


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes (int): Size in bytes
    
    Returns:
        str: Formatted file size
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def validate_fastq_record(identifier, sequence, plus, quality):
    """
    Validate a FASTQ record for basic format compliance.
    
    Args:
        identifier (str): Sequence identifier line
        sequence (str): Sequence line
        plus (str): Plus line
        quality (str): Quality line
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Check identifier starts with @
    if not identifier.startswith('@'):
        return False
    
    # Check plus line starts with +
    if not plus.startswith('+'):
        return False
    
    # Check sequence and quality have same length
    if len(sequence) != len(quality):
        return False
    
    # Check sequence contains only valid nucleotides
    valid_bases = set('ATCGNRYSWKMBDHV')  # Include ambiguous bases
    if not set(sequence.upper()).issubset(valid_bases):
        return False
    
    return True


def get_quality_encoding(quality_string, sample_size=1000):
    """
    Attempt to detect quality score encoding (Phred+33 vs Phred+64).
    
    Args:
        quality_string (str): Quality score string
        sample_size (int): Number of characters to sample
    
    Returns:
        str: 'phred33' or 'phred64'
    """
    if not quality_string:
        return 'phred33'  # Default
    
    # Sample characters for analysis
    sample = quality_string[:sample_size]
    
    # Convert to ASCII values
    ascii_values = [ord(c) for c in sample]
    min_ascii = min(ascii_values)
    max_ascii = max(ascii_values)
    
    # Phred+33 typically ranges from 33-126
    # Phred+64 typically ranges from 64-126
    
    if min_ascii < 58:  # ASCII 58 is ':'
        return 'phred33'
    elif min_ascii >= 64:
        return 'phred64'
    else:
        # Ambiguous case, default to phred33
        return 'phred33' 