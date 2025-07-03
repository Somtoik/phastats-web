"""
Command-line interface for phastats.

This module handles argument parsing and provides the main entry point
for the phastats command-line tool.
"""

import argparse
import sys
from pathlib import Path

from .core import analyze_fastq, get_analysis_summary
from .reports import generate_report


def create_parser():
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description='Phastats: Advanced FASTQ Quality Control Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.fastq                           # Basic analysis
  %(prog)s input.fastq.gz --output-dir results  # Custom output directory
  %(prog)s input.fq --no-html --csv             # CSV output only
  %(prog)s input.fq --plots gc,quality          # Only GC and quality plots
  %(prog)s input.fq --quality-threshold 25      # Custom quality threshold
  %(prog)s input.fq --chunk-size 5000 --quiet  # Large file, minimal output
        """)
    
    # Required arguments
    parser.add_argument('input_file', type=str, 
                       help='Path to the input FASTQ file (supports .fastq, .fq, .fastq.gz, .fq.gz)')
    
    # Output options
    output_group = parser.add_argument_group('Output Options')
    output_group.add_argument('--output-dir', type=str, 
                             help='Custom output directory name (default: auto-generated with timestamp)')
    output_group.add_argument('--output-prefix', type=str, default='phastats',
                             help='Prefix for output files (default: phastats)')
    output_group.add_argument('--no-html', action='store_true',
                             help='Skip HTML report generation')
    output_group.add_argument('--csv', action='store_true',
                             help='Generate CSV output with statistics')
    output_group.add_argument('--json', action='store_true',
                             help='Generate JSON output with statistics')
    output_group.add_argument('--tsv', action='store_true',
                             help='Generate TSV output with statistics')
    
    # Plot selection options
    plot_group = parser.add_argument_group('Plot Options')
    plot_group.add_argument('--plots', type=str, 
                           help='Comma-separated list of plots to generate (gc,length,quality,perbase,all) (default: all)')
    plot_group.add_argument('--no-plots', action='store_true',
                           help='Skip all plot generation')
    plot_group.add_argument('--plot-format', choices=['png', 'pdf', 'svg'], default='png',
                           help='Output format for plots (default: png)')
    plot_group.add_argument('--plot-dpi', type=int, default=300,
                           help='DPI for plot images (default: 300)')
    plot_group.add_argument('--plot-size', type=str, default='10x6',
                           help='Plot size in inches (WxH, default: 10x6)')
    plot_group.add_argument('--show-plots', action='store_true',
                           help='Display plots interactively (requires GUI backend)')
    
    # Quality analysis options
    quality_group = parser.add_argument_group('Quality Analysis Options')
    quality_group.add_argument('--quality-threshold', type=int, default=20,
                              help='Quality threshold for low-quality base detection (default: 20)')
    quality_group.add_argument('--high-quality-threshold', type=int, default=30,
                              help='High quality threshold for statistics (default: 30)')
    quality_group.add_argument('--min-length', type=int, default=0,
                              help='Minimum sequence length to include in analysis (default: 0)')
    quality_group.add_argument('--max-length', type=int,
                              help='Maximum sequence length to include in analysis (default: no limit)')
    
    # Performance options
    perf_group = parser.add_argument_group('Performance Options')
    perf_group.add_argument('--chunk-size', type=int, default=10000,
                           help='Chunk size for processing large files (default: 10000)')
    perf_group.add_argument('--memory-limit', type=str,
                           help='Memory limit for processing (e.g., 1GB, 500MB)')
    perf_group.add_argument('--threads', type=int, default=1,
                           help='Number of threads for parallel processing (default: 1)')
    
    # Advanced options
    advanced_group = parser.add_argument_group('Advanced Options')
    advanced_group.add_argument('--subsample', type=int,
                               help='Subsample N sequences for analysis (useful for very large files)')
    advanced_group.add_argument('--skip-n50', action='store_true',
                               help='Skip N50 calculation (faster for very large datasets)')
    advanced_group.add_argument('--skip-perbase', action='store_true',
                               help='Skip per-base content analysis (faster for very large datasets)')
    advanced_group.add_argument('--encoding', choices=['phred33', 'phred64'], default='phred33',
                               help='Quality score encoding (default: phred33)')
    
    # Verbosity options
    verbose_group = parser.add_argument_group('Verbosity Options')
    verbose_group.add_argument('--quiet', '-q', action='store_true',
                              help='Suppress progress messages')
    verbose_group.add_argument('--verbose', '-v', action='store_true',
                              help='Enable verbose output')
    verbose_group.add_argument('--debug', action='store_true',
                              help='Enable debug output')
    
    # Version
    parser.add_argument('--version', action='version', version='Phastats v2.1.0')
    
    return parser


def validate_arguments(args):
    """Validate command-line arguments."""
    # Validate arguments
    if args.quality_threshold >= args.high_quality_threshold:
        raise ValueError("--quality-threshold must be less than --high-quality-threshold")
    
    if args.min_length < 0:
        raise ValueError("--min-length must be non-negative")
    
    if args.max_length and args.max_length <= args.min_length:
        raise ValueError("--max-length must be greater than --min-length")
    
    # Parse plot size
    try:
        plot_width, plot_height = map(float, args.plot_size.split('x'))
        plot_size = (plot_width, plot_height)
    except ValueError:
        raise ValueError("--plot-size must be in format WxH (e.g., 10x6)")
    
    # Determine which plots to generate
    if args.no_plots:
        enabled_plots = set()
    elif args.plots:
        plot_options = args.plots.lower().split(',')
        if 'all' in plot_options:
            enabled_plots = {'gc', 'length', 'quality', 'perbase'}
        else:
            valid_plots = {'gc', 'length', 'quality', 'perbase'}
            enabled_plots = set()
            for plot in plot_options:
                plot = plot.strip()
                if plot in valid_plots:
                    enabled_plots.add(plot)
                else:
                    raise ValueError(f"Invalid plot option: {plot}. Valid options: {', '.join(valid_plots)}")
    else:
        enabled_plots = {'gc', 'length', 'quality', 'perbase'}  # Default: all plots
    
    # Configure verbosity
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    elif args.debug:
        verbosity = 3
    else:
        verbosity = 1  # Normal
    
    return enabled_plots, plot_size, verbosity


def main():
    """Main entry point for the CLI."""
    verbosity = 1  # Default verbosity
    try:
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args()
        
        # Validate arguments
        enabled_plots, plot_size, verbosity = validate_arguments(args)
        
        # Check if input file exists
        if not Path(args.input_file).exists():
            print(f"Error: Input file '{args.input_file}' not found.")
            sys.exit(1)
        
        # Run analysis
        stats = analyze_fastq(
            input_file=args.input_file,
            output_dir=args.output_dir,
            output_prefix=args.output_prefix,
            enabled_plots=enabled_plots,
            quality_threshold=args.quality_threshold,
            high_quality_threshold=args.high_quality_threshold,
            min_length=args.min_length,
            max_length=args.max_length,
            chunk_size=args.chunk_size,
            skip_n50=args.skip_n50,
            skip_perbase=args.skip_perbase,
            encoding=args.encoding,
            subsample=args.subsample,
            verbosity=verbosity,
            show_plots=args.show_plots,
            plot_format=args.plot_format,
            plot_dpi=args.plot_dpi,
            plot_size=plot_size
        )
        
        # Generate reports
        output_formats = {
            'html': not args.no_html,
            'csv': args.csv,
            'json': args.json,
            'tsv': args.tsv
        }
        
        output_files = generate_report(
            stats=stats,
            output_formats=output_formats,
            output_dir=stats['output_dir'],
            output_prefix=args.output_prefix,
            verbosity=verbosity
        )
        
        # Final summary
        if verbosity >= 1:
            print(f"Analysis complete!")
            print(f"Results saved to: {stats['output_dir']}")
            if output_files:
                for output_file in output_files:
                    print(f"   {output_file}")
            if enabled_plots:
                print(f"Plots saved in: {Path(stats['output_dir']) / 'plots'}")
            
            if verbosity >= 2:
                print(get_analysis_summary(stats))
        
        return 0
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if verbosity >= 3:  # Debug mode
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main()) 