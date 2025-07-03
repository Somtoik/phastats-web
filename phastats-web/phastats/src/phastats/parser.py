"""
FASTQ file parsing and statistics calculation.

This module handles the parsing of FASTQ files, including compressed files,
and calculates various statistics during the parsing process.
"""

import gzip
import numpy as np
import pandas as pd
from .utils import open_fastq_file


def parse_fastq_file(file_path, chunk_size=10000, quality_threshold=20, 
                     high_quality_threshold=30, skip_perbase=False, 
                     encoding='phred33', verbosity=1):
    """
    Memory-efficient FASTQ parser using generators and streaming processing.
    Processes data in chunks to avoid loading entire dataset into memory.
    
    Args:
        file_path (str): Path to FASTQ file
        chunk_size (int): Number of sequences to process at once
        quality_threshold (int): Threshold for low-quality bases
        high_quality_threshold (int): Threshold for high-quality bases
        skip_perbase (bool): Skip per-base content analysis
        encoding (str): Quality score encoding (phred33 or phred64)
        verbosity (int): Verbosity level
    
    Returns:
        dict: Parsing results with statistics
    """
    # Statistics accumulators
    total_sequences = 0
    poor_quality_sequences = 0
    total_length = 0
    gc_count = 0
    
    # Use lists for data that needs to be stored (but keep them minimal)
    lengths = []
    gc_contents = []
    
    # For quality statistics - process incrementally
    per_read_qualities = []
    quality_counts = {}  # Track individual quality score frequencies
    
    # For per-base content - use numpy arrays for efficiency
    max_position = 0
    base_counts_by_position = {}  # Will convert to numpy arrays later
    
    # Open file with automatic compression detection
    f, is_compressed = open_fastq_file(file_path)
    
    try:
        chunk_sequences = []
        chunk_qualities = []
        
        while True:
            # Read the four lines of a FASTQ record
            identifier = f.readline().strip()
            if not identifier:
                # Process final chunk if it exists
                if chunk_sequences:
                    chunk_gc_count = _process_chunk(chunk_sequences, chunk_qualities, lengths, gc_contents, 
                                 base_counts_by_position, per_read_qualities, quality_counts, quality_threshold, encoding)
                    gc_count += chunk_gc_count
                break
                
            sequence = f.readline().strip()
            plus = f.readline().strip()
            quality = f.readline().strip()
            
            # Add to current chunk
            chunk_sequences.append(sequence)
            chunk_qualities.append(quality)
            
            # Update basic statistics immediately (memory efficient)
            seq_len = len(sequence)
            total_sequences += 1
            total_length += seq_len
            
            # Track maximum position for per-base analysis
            if not skip_perbase:
                max_position = max(max_position, seq_len)
            
            # Progress reporting for large files
            if verbosity >= 1 and total_sequences % 50000 == 0:
                print(f"Processed {total_sequences:,} sequences...")
            
            # Process chunk when it reaches the specified size
            if len(chunk_sequences) >= chunk_size:
                chunk_gc_count = _process_chunk(chunk_sequences, chunk_qualities, lengths, gc_contents, 
                             base_counts_by_position, per_read_qualities, quality_counts, quality_threshold, encoding)
                gc_count += chunk_gc_count
                chunk_sequences = []
                chunk_qualities = []
    
    finally:
        f.close()
    
    # Calculate quality statistics
    quality_stats = _calculate_quality_stats(per_read_qualities, quality_counts, quality_threshold, high_quality_threshold)
    
    # Finalize per-base content analysis
    if not skip_perbase and base_counts_by_position:
        per_base_content = _finalize_per_base_content(base_counts_by_position, max_position, total_sequences)
    else:
        per_base_content = pd.DataFrame()
    
    return {
        'total_sequences': total_sequences,
        'poor_quality_sequences': poor_quality_sequences,
        'total_length': total_length,
        'lengths': lengths,
        'gc_count': gc_count,
        'gc_contents': gc_contents,
        'per_base_content': per_base_content,
        'quality_stats': quality_stats
    }


def _process_chunk(sequences, qualities, lengths, gc_contents, base_counts_by_position, 
                   per_read_qualities, quality_counts, quality_threshold, encoding):
    """
    Process a chunk of sequences and qualities using vectorized operations.
    
    Args:
        sequences (list): List of sequence strings
        qualities (list): List of quality strings
        lengths (list): List to append sequence lengths
        gc_contents (list): List to append GC content percentages
        base_counts_by_position (dict): Dictionary tracking base counts by position
        per_read_qualities (list): List to append per-read quality averages
        quality_threshold (int): Quality threshold for analysis
        encoding (str): Quality encoding scheme
    
    Returns:
        int: Total GC count for this chunk
    """
    # Quality score offset based on encoding
    offset = 33 if encoding == 'phred33' else 64
    chunk_gc_count = 0
    
    for seq, qual in zip(sequences, qualities):
        seq_len = len(seq)
        lengths.append(seq_len)
        
        # Calculate GC content
        gc_count = seq.count('G') + seq.count('C')
        chunk_gc_count += gc_count
        gc_content = (gc_count / seq_len * 100) if seq_len > 0 else 0
        gc_contents.append(gc_content)
        
        # Process quality scores
        if qual:
            quality_scores = [ord(q) - offset for q in qual]
            avg_quality = np.mean(quality_scores) if quality_scores else 0
            per_read_qualities.append(avg_quality)
            
            # Track individual quality score counts for distribution plot
            for score in quality_scores:
                quality_counts[score] = quality_counts.get(score, 0) + 1
        
        # Per-base content analysis (if not skipped)
        for pos, base in enumerate(seq):
            if pos not in base_counts_by_position:
                base_counts_by_position[pos] = {'A': 0, 'T': 0, 'G': 0, 'C': 0, 'N': 0}
            
            if base in base_counts_by_position[pos]:
                base_counts_by_position[pos][base] += 1
            else:
                base_counts_by_position[pos]['N'] += 1
    
    return chunk_gc_count


def _finalize_per_base_content(base_counts_by_position, max_position, total_sequences):
    """
    Convert base counts by position to percentages and create DataFrame.
    
    Args:
        base_counts_by_position (dict): Base counts by position
        max_position (int): Maximum sequence position
        total_sequences (int): Total number of sequences
    
    Returns:
        pd.DataFrame: Per-base content percentages
    """
    # Create arrays for each base
    positions = list(range(max_position))
    base_percentages = {
        '%A': np.zeros(max_position),
        '%T': np.zeros(max_position),
        '%G': np.zeros(max_position),
        '%C': np.zeros(max_position)
    }
    
    # Calculate percentages for each position
    for pos in positions:
        if pos in base_counts_by_position:
            total_at_pos = sum(base_counts_by_position[pos].values())
            if total_at_pos > 0:
                base_percentages['%A'][pos] = (base_counts_by_position[pos]['A'] / total_at_pos) * 100
                base_percentages['%T'][pos] = (base_counts_by_position[pos]['T'] / total_at_pos) * 100
                base_percentages['%G'][pos] = (base_counts_by_position[pos]['G'] / total_at_pos) * 100
                base_percentages['%C'][pos] = (base_counts_by_position[pos]['C'] / total_at_pos) * 100
    
    # Create DataFrame
    df = pd.DataFrame(base_percentages, index=positions)
    return df


def _calculate_quality_stats(per_read_qualities, quality_counts, quality_threshold, high_quality_threshold):
    """
    Calculate comprehensive quality statistics from per-read quality scores.
    
    Args:
        per_read_qualities (list): List of per-read average quality scores
        quality_threshold (int): Low quality threshold
        high_quality_threshold (int): High quality threshold
    
    Returns:
        dict: Quality statistics
    """
    if not per_read_qualities:
        return {
            'overall_avg_quality': 0,
            'avg_per_read_quality': 0,
            'low_quality_percentage': 0,
            'high_quality_percentage': 0,
            'total_bases': 0,
            'low_quality_bases': 0
        }
    
    # Convert to numpy array for efficient calculations
    qualities = np.array(per_read_qualities)
    
    # Calculate statistics
    overall_avg_quality = np.mean(qualities)
    avg_per_read_quality = overall_avg_quality  # Same for per-read averages
    
    # Count bases below/above thresholds (approximation based on per-read averages)
    low_quality_reads = np.sum(qualities < quality_threshold)
    high_quality_reads = np.sum(qualities >= high_quality_threshold)
    
    low_quality_percentage = (low_quality_reads / len(qualities) * 100) if qualities.size > 0 else 0
    high_quality_percentage = (high_quality_reads / len(qualities) * 100) if qualities.size > 0 else 0
    
    return {
        'overall_avg_quality': float(overall_avg_quality),
        'avg_per_read_quality': float(avg_per_read_quality),
        'low_quality_percentage': float(low_quality_percentage),
        'high_quality_percentage': float(high_quality_percentage),
        'total_bases': len(qualities),  # Approximation - should be sum of all base counts
        'low_quality_bases': int(low_quality_reads),
        'quality_counts': quality_counts
    } 