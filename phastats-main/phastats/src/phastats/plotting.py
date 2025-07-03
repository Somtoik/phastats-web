"""
Plotting and visualization functions for phastats.

This module contains all the functions for creating quality control plots
including GC distribution, length distribution, quality distribution,
and per-base sequence content plots.
"""

import os
import matplotlib
# Use non-interactive backend to prevent GUI issues in web environments
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import scipy.stats as stats
from .utils import get_plot_path

# Suppress matplotlib warnings
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

def safe_legend(loc='upper right', **kwargs):
    """Safely add legend only if there are labeled artists."""
    try:
        handles, labels = plt.gca().get_legend_handles_labels()
        if handles:
            plt.legend(loc=loc, frameon=True, fancybox=True, shadow=True, 
                      fontsize=11, framealpha=0.9, **kwargs)
    except Exception:
        pass  # Ignore legend errors


def create_plots(lengths, gc_contents, quality_stats, per_base_content, output_dir,
                 enabled_plots, skip_perbase=False, plot_format='png', 
                 plot_dpi=300, plot_size=(10, 6), show_plots=False):
    """
    Create all requested plots for the analysis.
    
    Args:
        lengths (list): Sequence lengths
        gc_contents (list): GC content percentages
        quality_stats (dict): Quality statistics
        per_base_content (pd.DataFrame): Per-base content data
        output_dir (str): Output directory path
        enabled_plots (set): Set of plots to generate
        skip_perbase (bool): Skip per-base content plot
        plot_format (str): Output format for plots
        plot_dpi (int): DPI for plots
        plot_size (tuple): Plot size in inches
        show_plots (bool): Whether to display plots interactively
    
    Returns:
        dict: Dictionary of generated plot file paths
    """
    plot_files = {}
    
    if 'length' in enabled_plots:
        plot_files['length'] = plot_length_distribution(lengths, output_dir, plot_format, plot_dpi, plot_size, show_plots)
    
    if 'quality' in enabled_plots:
        plot_files['quality'] = plot_quality_distribution_from_stats(quality_stats, output_dir, plot_format, plot_dpi, plot_size, show_plots)
    
    if 'gc' in enabled_plots:
        plot_files['gc'] = plot_gc_distribution(gc_contents, output_dir, plot_format, plot_dpi, plot_size, show_plots)
    
    if 'perbase' in enabled_plots and not skip_perbase:
        plot_files['perbase'] = plot_per_base_content(per_base_content, output_dir, plot_format, plot_dpi, plot_size, show_plots)
    
    return plot_files


def setup_plot(title, xlabel, ylabel, figsize=(10, 6)):
    """
    Set up a professional-looking plot with consistent styling.
    
    Args:
        title (str): Plot title
        xlabel (str): X-axis label
        ylabel (str): Y-axis label
        figsize (tuple): Figure size in inches
    
    Returns:
        tuple: (fig, ax) matplotlib figure and axes objects
    """
    fig = plt.figure(figsize=figsize, facecolor='white', dpi=100)
    ax = plt.gca()
    
    # Set background colors
    ax.set_facecolor('#f8f9fa')
    
    # Set title with improved styling
    plt.title(title, fontsize=18, fontweight='bold', color='#2c3e50', pad=20)
    
    # Set axis labels with improved styling
    plt.xlabel(xlabel, fontsize=14, fontweight='medium', color='#34495e')
    plt.ylabel(ylabel, fontsize=14, fontweight='medium', color='#34495e')
    
    # Improve tick styling
    plt.xticks(fontsize=11, color='#34495e')
    plt.yticks(fontsize=11, color='#34495e')
    
    # Add subtle grid
    plt.grid(True, linestyle='-', alpha=0.3, color='#bdc3c7', linewidth=0.5)
    
    # Improve spines (borders)
    for spine in ax.spines.values():
        spine.set_color('#7f8c8d')
        spine.set_linewidth(1)
    
    # Add some padding
    plt.tight_layout(pad=2.0)
    
    return fig, ax


def _finalize_plot(plot_path, plot_dpi, plot_format, show_plots=False, plot_title="Plot"):
    """
    Helper function to finalize plot - save and optionally show.
    
    Args:
        plot_path (str): Path to save the plot
        plot_dpi (int): DPI for saving
        plot_format (str): Format for saving
        show_plots (bool): Whether to show plot interactively
        plot_title (str): Title for interactive display
    
    Returns:
        str: Path to saved plot
    """
    try:
        # Ensure we have a current figure
        fig = plt.gcf()
        if fig is None:
            raise ValueError("No current figure to save")
            
        # Save the plot
        plt.savefig(plot_path, dpi=plot_dpi, bbox_inches='tight', format=plot_format)
        
        # Show interactively if requested (only in interactive environments)
        if show_plots and hasattr(plt, 'show'):
            try:
                plt.suptitle(f"{plot_title} - Interactive View", fontsize=16, y=0.98)
                plt.show(block=False)
                plt.pause(0.1)  # Brief pause to ensure plot displays
            except Exception:
                pass  # Ignore display errors in headless environments
        
        # Clear the figure
        plt.clf()
        plt.close(fig)  # Explicitly close to free memory
        
        return plot_path
        
    except Exception as e:
        # Clear any remaining plots and return None to indicate failure
        try:
            plt.clf()
            plt.close('all')
        except:
            pass
        raise Exception(f"Failed to finalize plot: {str(e)}")
    
    return plot_path


def plot_gc_distribution(gc_contents, output_dir, plot_format='png', plot_dpi=300, plot_size=(10, 6), show_plots=False):
    """
    Create GC content distribution plot.
    
    Args:
        gc_contents (list): List of GC content percentages
        output_dir (str): Output directory
        plot_format (str): Plot format
        plot_dpi (int): Plot DPI
        plot_size (tuple): Plot size
        show_plots (bool): Whether to display plot interactively
    
    Returns:
        str: Path to generated plot file
    """
    fig, ax = setup_plot('GC Content Distribution', 'GC Content (%)', 'Density', plot_size)

    # Create histogram with improved styling
    count, bins, ignored = plt.hist(gc_contents, bins=50, density=True, alpha=0.7, 
                                   color='#3498db', edgecolor='#2980b9', linewidth=1.2, 
                                   label='Observed GC content')

    # Fit a normal distribution to the data
    if len(gc_contents) > 1:
        mu, std = np.mean(gc_contents), np.std(gc_contents)
        x = np.linspace(min(gc_contents), max(gc_contents), 100)
        p = stats.norm.pdf(x, mu, std)
        
        # Plot the theoretical normal distribution
        plt.plot(x, p, linewidth=3, label=f'Normal distribution (μ={mu:.1f}%, σ={std:.1f}%)', 
                color='#e74c3c', linestyle='--')
        
        # Add vertical line for mean
        plt.axvline(mu, color='#e74c3c', linestyle='-', alpha=0.8, linewidth=2, 
                   label=f'Mean GC content: {mu:.1f}%')

    # Add legend only if there are labeled artists
    handles, labels = plt.gca().get_legend_handles_labels()
    if handles:
        plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, framealpha=0.9)
    
    # Add statistics text box
    if len(gc_contents) > 0:
        stats_text = f'Sequences: {len(gc_contents)}\nMin: {min(gc_contents):.1f}%\nMax: {max(gc_contents):.1f}%'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
                facecolor='white', alpha=0.8, edgecolor='#bdc3c7'))
    
    plot_path = get_plot_path(output_dir, f"gc-distribution.{plot_format}")
    return _finalize_plot(plot_path, plot_dpi, plot_format, show_plots, "GC Content Distribution")


def plot_length_distribution(lengths, output_dir, plot_format='png', plot_dpi=300, plot_size=(10, 6), show_plots=False):
    """
    Create sequence length distribution plot.
    
    Args:
        lengths (list): List of sequence lengths
        output_dir (str): Output directory
        plot_format (str): Plot format
        plot_dpi (int): Plot DPI
        plot_size (tuple): Plot size
        show_plots (bool): Whether to display plot interactively
    
    Returns:
        str: Path to generated plot file
    """
    fig, ax = setup_plot('Sequence Length Distribution', 'Sequence Length (bp)', 'Frequency', plot_size)
    
    # Create histogram with improved styling
    n, bins, patches = plt.hist(lengths, bins=50, alpha=0.8, color='#27ae60', 
                               edgecolor='#229954', linewidth=1.2, label='Sequence lengths')
    
    # Add statistics
    if len(lengths) > 0:
        mean_length = np.mean(lengths)
        median_length = np.median(lengths)
        
        # Add vertical lines for mean and median
        plt.axvline(mean_length, color='#e74c3c', linestyle='--', linewidth=2, 
                   alpha=0.8, label=f'Mean: {mean_length:.1f} bp')
        plt.axvline(median_length, color='#f39c12', linestyle=':', linewidth=2, 
                   alpha=0.8, label=f'Median: {median_length:.1f} bp')
        
        # Add statistics text box
        stats_text = f'Total sequences: {len(lengths)}\nMin length: {min(lengths)} bp\nMax length: {max(lengths)} bp\nStd dev: {np.std(lengths):.1f} bp'
        plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, 
                         edgecolor='#bdc3c7'))
    
    # Add legend only if there are labeled artists
    handles, labels = plt.gca().get_legend_handles_labels()
    if handles:
        plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, framealpha=0.9)
    
    plot_path = get_plot_path(output_dir, f"length_distribution.{plot_format}")
    return _finalize_plot(plot_path, plot_dpi, plot_format, show_plots, "Sequence Length Distribution")


def plot_quality_distribution_from_stats(quality_stats, output_dir, plot_format='png', plot_dpi=300, plot_size=(10, 6), show_plots=False):
    """
    Create quality distribution plot from pre-computed statistics.
    
    Args:
        quality_stats (dict): Dictionary containing quality statistics
        output_dir (str): Output directory
        plot_format (str): Plot format
        plot_dpi (int): Plot DPI
        plot_size (tuple): Plot size
        show_plots (bool): Whether to display plot interactively
    
    Returns:
        str: Path to generated plot file
    """
    fig, ax = setup_plot('Quality Score Distribution', 'Quality Score', 'Frequency', plot_size)
    
    # Extract quality score counts
    quality_counts = quality_stats.get('quality_counts', {})
    
    if quality_counts:
        scores = sorted(quality_counts.keys())
        counts = [quality_counts[score] for score in scores]
        
        # Create bar plot
        plt.bar(scores, counts, alpha=0.8, color='#9b59b6', edgecolor='#8e44ad', 
                linewidth=1.2, label='Quality score frequency')
        
        # Add mean quality line
        mean_quality = quality_stats.get('mean_quality', 0)
        if mean_quality > 0:
            plt.axvline(mean_quality, color='#e74c3c', linestyle='--', linewidth=2, 
                       alpha=0.8, label=f'Mean quality: {mean_quality:.1f}')
        
        # Add statistics text box
        total_bases = sum(counts)
        stats_text = f'Total bases: {total_bases:,}\nMean quality: {mean_quality:.1f}'
        if 'q25' in quality_stats and 'q75' in quality_stats:
            stats_text += f'\nQ25: {quality_stats["q25"]:.1f}\nQ75: {quality_stats["q75"]:.1f}'
        
        plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, 
                         edgecolor='#bdc3c7'))
        
        # Add legend
        plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, framealpha=0.9)
    
    plot_path = get_plot_path(output_dir, f"quality-distribution.{plot_format}")
    return _finalize_plot(plot_path, plot_dpi, plot_format, show_plots, "Quality Score Distribution")


def plot_quality_distribution(qualities, output_dir, plot_format='png', plot_dpi=300, plot_size=(10, 6), show_plots=False):
    """
    Create quality distribution plot from raw quality scores.
    
    Args:
        qualities (list): List of quality scores
        output_dir (str): Output directory
        plot_format (str): Plot format
        plot_dpi (int): Plot DPI
        plot_size (tuple): Plot size
        show_plots (bool): Whether to display plot interactively
    
    Returns:
        str: Path to generated plot file
    """
    fig, ax = setup_plot('Quality Score Distribution', 'Quality Score', 'Frequency', plot_size)
    
    if qualities:
        # Create histogram
        plt.hist(qualities, bins=50, alpha=0.8, color='#9b59b6', edgecolor='#8e44ad', 
                linewidth=1.2, label='Quality scores')
        
        # Add mean quality line
        mean_quality = np.mean(qualities)
        plt.axvline(mean_quality, color='#e74c3c', linestyle='--', linewidth=2, 
                   alpha=0.8, label=f'Mean quality: {mean_quality:.1f}')
        
        # Add statistics text box
        stats_text = f'Total scores: {len(qualities):,}\nMean: {mean_quality:.1f}\nMin: {min(qualities)}\nMax: {max(qualities)}'
        plt.text(0.98, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.8, 
                         edgecolor='#bdc3c7'))
        
        # Add legend
        plt.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, framealpha=0.9)
    
    plot_path = get_plot_path(output_dir, f"quality-distribution.{plot_format}")
    return _finalize_plot(plot_path, plot_dpi, plot_format, show_plots, "Quality Score Distribution")


def plot_per_base_content(per_base_content_df, output_dir, plot_format='png', plot_dpi=300, plot_size=(12, 6), show_plots=False):
    """
    Create per-base sequence content plot.
    
    Args:
        per_base_content_df (pd.DataFrame): Per-base content data
        output_dir (str): Output directory
        plot_format (str): Plot format
        plot_dpi (int): Plot DPI
        plot_size (tuple): Plot size
        show_plots (bool): Whether to display plot interactively
    
    Returns:
        str: Path to generated plot file
    """
    fig, ax = setup_plot('Per-base Sequence Content', 'Position in read (bp)', 'Percentage (%)', plot_size)
    
    if per_base_content_df is not None and not per_base_content_df.empty:
        # Plot each nucleotide
        positions = per_base_content_df.index
        
        plt.plot(positions, per_base_content_df['%A'], linewidth=2.5, alpha=0.9, 
                color='#e74c3c', label='A', marker='o', markersize=3)
        plt.plot(positions, per_base_content_df['%T'], linewidth=2.5, alpha=0.9, 
                color='#3498db', label='T', marker='s', markersize=3)
        plt.plot(positions, per_base_content_df['%G'], linewidth=2.5, alpha=0.9, 
                color='#f39c12', label='G', marker='^', markersize=3)
        plt.plot(positions, per_base_content_df['%C'], linewidth=2.5, alpha=0.9, 
                color='#27ae60', label='C', marker='d', markersize=3)
        
        # Add 25% reference line
        plt.axhline(y=25, color='#95a5a6', linestyle='--', alpha=0.7, linewidth=1.5, 
                   label='Expected (25%)')
        
        # Improve legend
        plt.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, 
                  fontsize=11, framealpha=0.9, ncol=2)
        
        # Set y-axis limits
        plt.ylim(0, max(50, per_base_content_df.max().max() * 1.1))
        
        # Add statistics text box
        max_pos = len(positions)
        avg_content = per_base_content_df.mean()
        stats_text = f'Read length: {max_pos} bp\nAvg A: {avg_content["%A"]:.1f}%\nAvg T: {avg_content["%T"]:.1f}%\nAvg G: {avg_content["%G"]:.1f}%\nAvg C: {avg_content["%C"]:.1f}%'
        plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', 
                facecolor='white', alpha=0.8, edgecolor='#bdc3c7'))
    
    plot_path = get_plot_path(output_dir, f"Per-base_sequence_content.{plot_format}")
    return _finalize_plot(plot_path, plot_dpi, plot_format, show_plots, "Per-base Sequence Content") 