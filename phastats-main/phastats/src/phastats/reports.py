"""
Report generation functions for phastats.

This module handles the creation of various output formats including
HTML reports, CSV data exports, JSON structured data, and TSV files.
"""

import os
import json
import csv
import base64
import io
from datetime import datetime
from .utils import detect_file_type


def generate_report(stats, output_formats, output_dir, output_prefix='phastats', verbosity=1):
    """
    Generate reports in requested formats.
    
    Args:
        stats (dict): Analysis statistics
        output_formats (dict): Dictionary of format flags
        output_dir (str): Output directory
        output_prefix (str): Output file prefix
        verbosity (int): Verbosity level
    
    Returns:
        list: List of generated report file paths
    """
    output_files = []
    
    # HTML Report
    if output_formats.get('html', True):
        if verbosity >= 1:
            print("Generating HTML report...")
        html_path = write_html_report(stats, output_dir, output_prefix)
        output_files.append(f"HTML report: {html_path}")
    
    # CSV Output
    if output_formats.get('csv', False):
        if verbosity >= 1:
            print("Generating CSV output...")
        csv_path = write_csv_output(stats, output_dir, output_prefix)
        output_files.append(f"CSV data: {csv_path}")
    
    # JSON Output
    if output_formats.get('json', False):
        if verbosity >= 1:
            print("Generating JSON output...")
        json_path = write_json_output(stats, output_dir, output_prefix)
        output_files.append(f"JSON data: {json_path}")
    
    # TSV Output
    if output_formats.get('tsv', False):
        if verbosity >= 1:
            print("Generating TSV output...")
        tsv_path = write_tsv_output(stats, output_dir, output_prefix)
        output_files.append(f"TSV data: {tsv_path}")
    
    return output_files


def write_html_report(stats, output_dir, output_prefix='phastats'):
    """
    Generate enhanced HTML report with embedded plots.
    
    Args:
        stats (dict): Analysis statistics
        output_dir (str): Output directory
        output_prefix (str): File prefix
    
    Returns:
        str: Path to HTML report
    """
    html_path = os.path.join(output_dir, f"{output_prefix}_report.html")
    
    # Get embedded plot data
    plot_data = {}
    for plot_type, plot_path in stats.get('plot_files', {}).items():
        if os.path.exists(plot_path):
            plot_data[plot_type] = plot_to_base64(plot_path)
        else:
            plot_data[plot_type] = ""
    
    # Generate HTML content
    html_content = create_enhanced_html_report(
        filename=stats['input_file'],
        total_sequences=stats['total_sequences'],
        poor_quality_sequences=stats['poor_quality_sequences'],
        total_length=stats['total_length'],
        gc_content=stats['gc_content'],
        n50_value=stats['n50_value'],
        quality_stats=stats['quality_stats'],
        output_dir=stats['output_dir'],
        plot_data=plot_data
    )
    
    # Write HTML file
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_path


def write_csv_output(stats, output_dir, output_prefix):
    """Write statistics to CSV format"""
    csv_path = os.path.join(output_dir, f"{output_prefix}_statistics.csv")
    
    # Prepare data for CSV
    data = []
    
    # Basic statistics
    data.append(['Metric', 'Value', 'Unit'])
    data.append(['Total Sequences', stats['total_sequences'], 'count'])
    data.append(['Poor Quality Sequences', stats['poor_quality_sequences'], 'count'])
    data.append(['Total Length', stats['total_length'], 'bp'])
    data.append(['Average Length', f"{stats['average_length']:.2f}", 'bp'])
    data.append(['GC Content', f"{stats['gc_content']:.2f}", '%'])
    data.append(['N50 Value', stats['n50_value'], 'bp'])
    
    # Quality statistics
    quality_stats = stats['quality_stats']
    data.append(['Overall Average Quality', f"{quality_stats['overall_avg_quality']:.2f}", 'Phred'])
    data.append(['Average Per-Read Quality', f"{quality_stats['avg_per_read_quality']:.2f}", 'Phred'])
    data.append(['Low Quality Percentage', f"{quality_stats['low_quality_percentage']:.2f}", '%'])
    data.append(['High Quality Percentage', f"{quality_stats.get('high_quality_percentage', 0):.2f}", '%'])
    data.append(['Total Bases Analyzed', quality_stats['total_bases'], 'count'])
    
    # Analysis parameters
    params = stats['analysis_parameters']
    data.append(['Quality Threshold', params['quality_threshold'], 'Phred'])
    data.append(['High Quality Threshold', params['high_quality_threshold'], 'Phred'])
    data.append(['Minimum Length Filter', params['min_length'], 'bp'])
    data.append(['Maximum Length Filter', params['max_length'] or 'None', 'bp'])
    data.append(['Chunk Size', params['chunk_size'], 'sequences'])
    data.append(['Quality Encoding', params['encoding'], 'format'])
    
    # Write CSV file
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)
    
    return csv_path


def write_json_output(stats, output_dir, output_prefix):
    """Write statistics to JSON format"""
    json_path = os.path.join(output_dir, f"{output_prefix}_statistics.json")
    
    # Prepare data for JSON (make sure all values are JSON serializable)
    json_data = {
        'metadata': {
            'generated_on': datetime.now().isoformat(),
            'phastats_version': '2.1.0',
            'enabled_plots': stats['enabled_plots']
        },
        'sequence_statistics': {
            'total_sequences': stats['total_sequences'],
            'poor_quality_sequences': stats['poor_quality_sequences'],
            'total_length': stats['total_length'],
            'average_length': round(stats['average_length'], 2),
            'gc_content': round(stats['gc_content'], 2),
            'n50_value': stats['n50_value']
        },
        'quality_statistics': {
            'overall_avg_quality': round(stats['quality_stats']['overall_avg_quality'], 2),
            'avg_per_read_quality': round(stats['quality_stats']['avg_per_read_quality'], 2),
            'low_quality_percentage': round(stats['quality_stats']['low_quality_percentage'], 2),
            'high_quality_percentage': round(stats['quality_stats'].get('high_quality_percentage', 0), 2),
            'total_bases': stats['quality_stats']['total_bases']
        },
        'analysis_parameters': stats['analysis_parameters']
    }
    
    # Write JSON file
    with open(json_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_data, jsonfile, indent=2, ensure_ascii=False)
    
    return json_path


def write_tsv_output(stats, output_dir, output_prefix):
    """Write statistics to TSV format"""
    tsv_path = os.path.join(output_dir, f"{output_prefix}_statistics.tsv")
    
    # Prepare data for TSV
    data = []
    
    # Basic statistics
    data.append(['Metric', 'Value', 'Unit', 'Category'])
    data.append(['Total Sequences', str(stats['total_sequences']), 'count', 'Basic'])
    data.append(['Poor Quality Sequences', str(stats['poor_quality_sequences']), 'count', 'Basic'])
    data.append(['Total Length', str(stats['total_length']), 'bp', 'Basic'])
    data.append(['Average Length', f"{stats['average_length']:.2f}", 'bp', 'Basic'])
    data.append(['GC Content', f"{stats['gc_content']:.2f}", '%', 'Composition'])
    data.append(['N50 Value', str(stats['n50_value']), 'bp', 'Assembly'])
    
    # Quality statistics
    quality_stats = stats['quality_stats']
    data.append(['Overall Average Quality', f"{quality_stats['overall_avg_quality']:.2f}", 'Phred', 'Quality'])
    data.append(['Average Per-Read Quality', f"{quality_stats['avg_per_read_quality']:.2f}", 'Phred', 'Quality'])
    data.append(['Low Quality Percentage', f"{quality_stats['low_quality_percentage']:.2f}", '%', 'Quality'])
    data.append(['High Quality Percentage', f"{quality_stats.get('high_quality_percentage', 0):.2f}", '%', 'Quality'])
    data.append(['Total Bases Analyzed', str(quality_stats['total_bases']), 'count', 'Quality'])
    
    # Analysis parameters
    params = stats['analysis_parameters']
    data.append(['Quality Threshold', str(params['quality_threshold']), 'Phred', 'Parameters'])
    data.append(['High Quality Threshold', str(params['high_quality_threshold']), 'Phred', 'Parameters'])
    data.append(['Minimum Length Filter', str(params['min_length']), 'bp', 'Parameters'])
    data.append(['Maximum Length Filter', str(params['max_length'] or 'None'), 'bp', 'Parameters'])
    data.append(['Chunk Size', str(params['chunk_size']), 'sequences', 'Parameters'])
    data.append(['Quality Encoding', params['encoding'], 'format', 'Parameters'])
    
    # Write TSV file
    with open(tsv_path, 'w', newline='', encoding='utf-8') as tsvfile:
        writer = csv.writer(tsvfile, delimiter='\t')
        writer.writerows(data)
    
    return tsv_path


def plot_to_base64(plot_path):
    """
    Convert a plot file to base64 encoded string for embedding in HTML.
    
    Args:
        plot_path (str): Path to plot file
    
    Returns:
        str: Base64 encoded image data URL
    """
    try:
        with open(plot_path, 'rb') as img_file:
            img_data = img_file.read()
            img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Determine image format from file extension
            if plot_path.lower().endswith('.png'):
                img_format = 'png'
            elif plot_path.lower().endswith('.jpg') or plot_path.lower().endswith('.jpeg'):
                img_format = 'jpeg'
            elif plot_path.lower().endswith('.svg'):
                img_format = 'svg+xml'
            else:
                img_format = 'png'  # Default
            
            return f"data:image/{img_format};base64,{img_base64}"
    except Exception as e:
        print(f"Warning: Could not encode plot {plot_path}: {e}")
        return ""


def create_enhanced_html_report(filename, total_sequences, poor_quality_sequences, total_length, 
                               gc_content, n50_value, quality_stats, output_dir, plot_data):
    """
    Create enhanced HTML report with embedded plots and responsive design.
    
    Args:
        filename (str): Input filename
        total_sequences (int): Total number of sequences
        poor_quality_sequences (int): Number of poor quality sequences
        total_length (int): Total sequence length
        gc_content (float): GC content percentage
        n50_value (int): N50 value
        quality_stats (dict): Quality statistics
        output_dir (str): Output directory
        plot_data (dict): Base64 encoded plot data
    
    Returns:
        str: HTML content
    """
    file_type = detect_file_type(filename)
    average_length = total_length / total_sequences if total_sequences > 0 else 0
    
    # Get plot data with fallbacks
    gc_plot_b64 = plot_data.get('gc', '')
    length_plot_b64 = plot_data.get('length', '')
    quality_plot_b64 = plot_data.get('quality', '')
    perbase_plot_b64 = plot_data.get('perbase', '')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phastats Analysis Report - {filename}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            min-height: 100vh;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .subtitle {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .nav-bar {{
            background: #34495e;
            padding: 15px 0;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .nav-bar ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        .nav-bar li {{
            margin: 0 15px;
        }}
        
        .nav-bar a {{
            color: #ecf0f1;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 5px;
            transition: all 0.3s ease;
            display: block;
        }}
        
        .nav-bar a:hover {{
            background: #3498db;
            transform: translateY(-2px);
        }}
        
        .metadata {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            border-left: 5px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        .metadata h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5rem;
        }}
        
        .metadata-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        
        .metadata-item {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .label {{
            font-weight: bold;
            color: #7f8c8d;
            font-size: 0.9rem;
            margin-bottom: 5px;
        }}
        
        .value {{
            color: #2c3e50;
            font-size: 1.1rem;
            word-break: break-all;
        }}
        
        .stats-section {{
            margin-bottom: 30px;
        }}
        
        .stats-section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8rem;
            text-align: center;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
        }}
        
        .stat-label {{
            font-size: 0.9rem;
            opacity: 0.9;
        }}
        
        .plots-section {{
            margin-bottom: 30px;
        }}
        
        .plots-section h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8rem;
            text-align: center;
        }}
        
        .plots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
        }}
        
        .plot-container {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .plot-container:hover {{
            transform: translateY(-3px);
        }}
        
        .plot-container h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-size: 1.2rem;
            text-align: center;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}
        
        .plot-container img {{
            width: 100%;
            height: auto;
            border-radius: 5px;
            opacity: 0;
            transform: scale(0.95);
            transition: all 0.3s ease;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px 0;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2rem;
            }}
            
            .nav-bar ul {{
                flex-direction: column;
                align-items: center;
            }}
            
            .plots-grid {{
                grid-template-columns: 1fr;
            }}
            
            .plot-container {{
                padding: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Phastats Analysis Report</h1>
            <div class="subtitle">Comprehensive FASTQ Quality Control Analysis</div>
        </header>
        
        <nav class="nav-bar">
            <ul>
                <li><a href="#metadata">File Info</a></li>
                <li><a href="#statistics">Statistics</a></li>
                <li><a href="#plots">Visualizations</a></li>
                <li><a href="#quality">Quality Metrics</a></li>
            </ul>
        </nav>
        
        <section id="metadata" class="metadata">
            <h2>Analysis Information</h2>
            <div class="metadata-grid">
                <div class="metadata-item">
                    <div class="label">Generated On</div>
                    <div class="value">{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Input File</div>
                    <div class="value">{filename}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">File Type</div>
                    <div class="value">{file_type}</div>
                </div>
                <div class="metadata-item">
                    <div class="label">Output Directory</div>
                    <div class="value">{output_dir}</div>
                </div>
            </div>
        </section>
        
        <section id="statistics" class="stats-section">
            <h2>Sequence Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{total_sequences:,}</div>
                    <div class="stat-label">Total Sequences</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{average_length:.1f}</div>
                    <div class="stat-label">Average Length (bp)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{gc_content:.1f}%</div>
                    <div class="stat-label">GC Content</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{n50_value:.0f}</div>
                    <div class="stat-label">N50 Value</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{quality_stats['overall_avg_quality']:.1f}</div>
                    <div class="stat-label">Average Quality</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{quality_stats['low_quality_percentage']:.1f}%</div>
                    <div class="stat-label">Low Quality Bases</div>
                </div>
            </div>
        </section>
        
        <section id="plots" class="plots-section">
            <h2>Quality Control Visualizations</h2>
            <div class="plots-grid">"""
    
    # Add plots if available
    if gc_plot_b64:
        html_content += f"""
                <div class="plot-container">
                    <h3>GC Content Distribution</h3>
                    <img src="{gc_plot_b64}" alt="GC Content Distribution" />
                </div>"""
    
    if length_plot_b64:
        html_content += f"""
                <div class="plot-container">
                    <h3>Sequence Length Distribution</h3>
                    <img src="{length_plot_b64}" alt="Sequence Length Distribution" />
                </div>"""
    
    if quality_plot_b64:
        html_content += f"""
                <div class="plot-container">
                    <h3>Base Quality Distribution</h3>
                    <img src="{quality_plot_b64}" alt="Base Quality Distribution" />
                </div>"""
    
    if perbase_plot_b64:
        html_content += f"""
                <div class="plot-container">
                    <h3>Per-Base Sequence Content</h3>
                    <img src="{perbase_plot_b64}" alt="Per-Base Sequence Content" />
                </div>"""
    
    html_content += f"""
            </div>
        </section>
        
        <footer class="footer">
            <p>Generated by Phastats v2.1.0 | Analysis completed in {datetime.now().strftime("%Y")}</p>
            <p>High-quality FASTQ analysis tool for genomics research</p>
        </footer>
    </div>
    
    <script>
        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});
        
        // Add loading animation for images
        document.querySelectorAll('img').forEach(img => {{
            img.addEventListener('load', function() {{
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            }});
        }});
    </script>
</body>
</html>"""
    
    return html_content 