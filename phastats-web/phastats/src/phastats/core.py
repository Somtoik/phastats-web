"""
Core analysis functions for phastats.

This module contains the main analysis logic that orchestrates
file parsing, statistics calculation, plotting, and report generation.
"""

import os
from pathlib import Path
from datetime import datetime

from .parser import parse_fastq_file
from .plotting import create_plots
from .reports import generate_report
from .utils import create_output_directory, calculate_gc_content, compute_n50_optimized


def analyze_fastq(input_file, output_dir=None, output_prefix='phastats', 
                  enabled_plots=None, quality_threshold=20, high_quality_threshold=30,
                  min_length=0, max_length=None, chunk_size=10000, 
                  skip_n50=False, skip_perbase=False, encoding='phred33',
                  subsample=None, verbosity=1, show_plots=False, **kwargs):
    """
    Main analysis function that orchestrates the entire FASTQ analysis pipeline.
    
    Args:
        input_file (str): Path to input FASTQ file
        output_dir (str, optional): Output directory path
        output_prefix (str): Prefix for output files
        enabled_plots (set): Set of plots to generate
        quality_threshold (int): Quality threshold for low-quality bases
        high_quality_threshold (int): High quality threshold
        min_length (int): Minimum sequence length filter
        max_length (int): Maximum sequence length filter
        chunk_size (int): Chunk size for processing
        skip_n50 (bool): Skip N50 calculation
        skip_perbase (bool): Skip per-base content analysis
        encoding (str): Quality score encoding
        subsample (int): Number of sequences to subsample
        verbosity (int): Verbosity level (0=quiet, 1=normal, 2=verbose, 3=debug)
        show_plots (bool): Whether to display plots interactively
        **kwargs: Additional arguments
    
    Returns:
        dict: Analysis results and statistics
    """
    # Set default plots if not specified
    if enabled_plots is None:
        enabled_plots = {'gc', 'length', 'quality', 'perbase'}
    
    # Create output directory
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        plots_dir = Path(output_dir) / "plots"
        plots_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir, _ = create_output_directory(input_file)
    
    # Progress reporting
    if verbosity >= 1:
        print(f"Phastats v2.1.0 - Advanced FASTQ Analysis")
        print(f"Input file: {input_file}")
        print(f"Output directory: {output_dir}")
        if verbosity >= 2:
            print(f"Chunk size: {chunk_size:,}")
            print(f"Quality threshold: Q{quality_threshold}")
            print(f"Enabled plots: {', '.join(sorted(enabled_plots)) if enabled_plots else 'none'}")
    
    # Parse FASTQ file
    if verbosity >= 1:
        print("Parsing FASTQ file with memory-efficient parser...")
    
    parse_results = parse_fastq_file(
        input_file, 
        chunk_size=chunk_size,
        quality_threshold=quality_threshold,
        high_quality_threshold=high_quality_threshold,
        skip_perbase=skip_perbase,
        encoding=encoding,
        verbosity=verbosity
    )
    
    # Extract results
    total_sequences = parse_results['total_sequences']
    poor_quality_sequences = parse_results['poor_quality_sequences']
    total_length = parse_results['total_length']
    lengths = parse_results['lengths']
    gc_count = parse_results['gc_count']
    gc_contents = parse_results['gc_contents']
    per_base_content = parse_results['per_base_content']
    quality_stats = parse_results['quality_stats']
    
    # Apply filtering if specified
    if min_length > 0 or max_length:
        original_count = len(lengths)
        if min_length > 0:
            lengths = [l for l in lengths if l >= min_length]
        if max_length:
            lengths = [l for l in lengths if l <= max_length]
        filtered_count = len(lengths)
        if verbosity >= 2 and filtered_count != original_count:
            print(f"Filtered sequences: {original_count:,} → {filtered_count:,}")
    
    # Apply subsampling if specified
    if subsample and subsample < len(lengths):
        import random
        random.seed(42)  # For reproducibility
        lengths = random.sample(lengths, subsample)
        if verbosity >= 2:
            print(f"Subsampled to {subsample:,} sequences")
    
    # Compute N50 if not skipped
    if skip_n50:
        n50_value = 0
    else:
        n50_value = compute_n50_optimized(lengths)
    
    if verbosity >= 1:
        print(f"Processed {total_sequences:,} sequences with {total_length:,} total bases")
        if verbosity >= 2:
            avg_length = total_length / total_sequences if total_sequences > 0 else 0
            gc_percentage = calculate_gc_content(gc_count, total_length)
            print(f"Average length: {avg_length:.1f} bp")
            print(f"GC content: {gc_percentage:.1f}%")
            print(f"N50: {n50_value}")
            print(f"Average quality: {quality_stats['overall_avg_quality']:.1f}")
    
    # Generate plots
    if enabled_plots and verbosity >= 1:
        print("Generating plots...")
    
    plot_files = create_plots(
        lengths=lengths,
        gc_contents=gc_contents,
        quality_stats=quality_stats,
        per_base_content=per_base_content,
        output_dir=output_dir,
        enabled_plots=enabled_plots,
        skip_perbase=skip_perbase,
        plot_format=kwargs.get('plot_format', 'png'),
        plot_dpi=kwargs.get('plot_dpi', 300),
        plot_size=kwargs.get('plot_size', (10, 6)),
        show_plots=show_plots
    )
    
    # Calculate final statistics
    final_stats = {
        'total_sequences': total_sequences,
        'poor_quality_sequences': poor_quality_sequences,
        'total_length': total_length,
        'average_length': total_length / total_sequences if total_sequences > 0 else 0,
        'gc_content': calculate_gc_content(gc_count, total_length),
        'n50_value': n50_value,
        'quality_stats': quality_stats,
        'enabled_plots': list(enabled_plots),
        'analysis_parameters': {
            'quality_threshold': quality_threshold,
            'high_quality_threshold': high_quality_threshold,
            'min_length': min_length,
            'max_length': max_length,
            'chunk_size': chunk_size,
            'encoding': encoding
        },
        'input_file': input_file,
        'output_dir': output_dir,
        'plot_files': plot_files
    }
    
    return final_stats


def get_analysis_summary(stats):
    """
    Generate a quick summary of analysis results.
    
    Args:
        stats (dict): Analysis statistics
    
    Returns:
        str: Formatted summary string
    """
    summary = f"""
Analysis Summary:
   Sequences: {stats['total_sequences']:,}
   Total bases: {stats['total_length']:,}
   Average length: {stats['average_length']:.1f} bp
   GC content: {stats['gc_content']:.1f}%
   Average quality: {stats['quality_stats']['overall_avg_quality']:.1f}
   Low quality bases: {stats['quality_stats']['low_quality_percentage']:.1f}%
"""
    return summary.strip() 