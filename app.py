"""
Flask web application for Phastats - FASTQ Quality Analysis Tool
"""

import os
import shutil
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from threading import Timer
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file, url_for, flash, redirect
import zipfile

# Import our phastats modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'phastats', 'src'))
from phastats.core import analyze_fastq

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size

# Configuration
UPLOAD_FOLDER = 'uploads'
TEMP_FOLDER = 'temp'
ALLOWED_EXTENSIONS = {'.fastq', '.fq', '.fastq.gz', '.fq.gz'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs('phastats', exist_ok=True)

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def cleanup_old_files():
    """Clean up files older than 2 hours."""
    cutoff_time = datetime.now() - timedelta(hours=2)
    
    for folder in [UPLOAD_FOLDER, TEMP_FOLDER]:
        if os.path.exists(folder):
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_time:
                        try:
                            os.remove(filepath)
                        except OSError:
                            pass
                elif os.path.isdir(filepath):
                    try:
                        shutil.rmtree(filepath)
                    except OSError:
                        pass

# Schedule cleanup every hour
def schedule_cleanup():
    cleanup_old_files()
    Timer(3600, schedule_cleanup).start()

schedule_cleanup()

@app.route('/')
def index():
    """Home page with file upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and process FASTQ analysis."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload FASTQ files (.fastq, .fq, .fastq.gz, .fq.gz)'}), 400
    
    try:
        # Generate unique identifier for this analysis
        analysis_id = str(uuid.uuid4())
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, f"{analysis_id}_{filename}")
        file.save(upload_path)
        
        # Create output directory
        output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Get analysis parameters from form
        quality_threshold = int(request.form.get('quality_threshold', 20))
        high_quality_threshold = int(request.form.get('high_quality_threshold', 30))
        skip_perbase = request.form.get('skip_perbase') == 'on'
        encoding = request.form.get('encoding', 'phred33')
        
        # Run analysis
        results = analyze_fastq(
            upload_path,
            output_dir=output_dir,
            quality_threshold=quality_threshold,
            high_quality_threshold=high_quality_threshold,
            skip_perbase=skip_perbase,
            encoding=encoding,
            verbosity=1
        )
        
        # Clean up uploaded file
        os.remove(upload_path)
        
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'message': 'Analysis completed successfully!',
            'redirect_url': url_for('results', analysis_id=analysis_id)
        })
        
    except Exception as e:
        # Clean up on error
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        if 'output_dir' in locals() and os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)
        
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/results/<analysis_id>')
def results(analysis_id):
    """Display analysis results."""
    output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
    
    if not os.path.exists(output_dir):
        flash('Analysis results not found or have expired.', 'error')
        return redirect(url_for('index'))
    
    # Check for HTML report
    html_report = os.path.join(output_dir, 'phastats_report.html')
    stats_file = os.path.join(output_dir, 'phastats_statistics.json')
    plots_dir = os.path.join(output_dir, 'plots')
    
    # Get list of generated plots
    plot_files = []
    if os.path.exists(plots_dir):
        for plot_file in os.listdir(plots_dir):
            if plot_file.endswith(('.png', '.jpg', '.jpeg', '.svg')):
                plot_files.append(plot_file)
    
    return render_template('results.html', 
                         analysis_id=analysis_id,
                         has_html_report=os.path.exists(html_report),
                         has_stats=os.path.exists(stats_file),
                         plot_files=plot_files)

@app.route('/download/<analysis_id>/<file_type>')
def download_file(analysis_id, file_type):
    """Download analysis results."""
    output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
    
    if not os.path.exists(output_dir):
        return jsonify({'error': 'Analysis results not found'}), 404
    
    try:
        if file_type == 'html':
            file_path = os.path.join(output_dir, 'phastats_report.html')
            return send_file(file_path, as_attachment=True, download_name=f'phastats_report_{analysis_id}.html')
        
        elif file_type == 'json':
            file_path = os.path.join(output_dir, 'phastats_statistics.json')
            return send_file(file_path, as_attachment=True, download_name=f'phastats_statistics_{analysis_id}.json')
        
        elif file_type == 'all':
            # Create ZIP file with all results
            zip_path = os.path.join(TEMP_FOLDER, f"phastats_results_{analysis_id}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(output_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, output_dir)
                        zipf.write(file_path, arcname)
            
            return send_file(zip_path, as_attachment=True, download_name=f'phastats_results_{analysis_id}.zip')
        
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

@app.route('/download_plot/<analysis_id>/<plot_name>')
def download_plot(analysis_id, plot_name):
    """Download individual plot files."""
    output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
    plots_dir = os.path.join(output_dir, 'plots')
    
    if not os.path.exists(plots_dir):
        return jsonify({'error': 'Plots not found'}), 404
    
    # Security: ensure the plot name is safe
    safe_plot_name = secure_filename(plot_name)
    plot_path = os.path.join(plots_dir, safe_plot_name)
    
    if not os.path.exists(plot_path):
        return jsonify({'error': 'Plot not found'}), 404
    
    return send_file(plot_path, as_attachment=True, download_name=safe_plot_name)

@app.route('/view_plot/<analysis_id>/<plot_name>')
def view_plot(analysis_id, plot_name):
    """View plot inline in browser."""
    output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
    plots_dir = os.path.join(output_dir, 'plots')
    
    if not os.path.exists(plots_dir):
        return jsonify({'error': 'Plots not found'}), 404
    
    # Security: ensure the plot name is safe
    safe_plot_name = secure_filename(plot_name)
    plot_path = os.path.join(plots_dir, safe_plot_name)
    
    if not os.path.exists(plot_path):
        return jsonify({'error': 'Plot not found'}), 404
    
    return send_file(plot_path, mimetype='image/png')

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """API endpoint for programmatic analysis."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    try:
        # Save file temporarily
        analysis_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        upload_path = os.path.join(UPLOAD_FOLDER, f"{analysis_id}_{filename}")
        file.save(upload_path)
        
        # Create output directory
        output_dir = os.path.join(TEMP_FOLDER, f"phastats_output_{analysis_id}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Get parameters from JSON or form data
        data = request.get_json() or {}
        quality_threshold = data.get('quality_threshold', 20)
        high_quality_threshold = data.get('high_quality_threshold', 30)
        skip_perbase = data.get('skip_perbase', False)
        encoding = data.get('encoding', 'phred33')
        
        # Run analysis
        results = analyze_fastq(
            upload_path,
            output_dir=output_dir,
            quality_threshold=quality_threshold,
            high_quality_threshold=high_quality_threshold,
            skip_perbase=skip_perbase,
            encoding=encoding,
            verbosity=0
        )
        
        # Clean up uploaded file
        os.remove(upload_path)
        
        # Return results with download URLs
        return jsonify({
            'success': True,
            'analysis_id': analysis_id,
            'results': results,
            'download_urls': {
                'html': url_for('download_file', analysis_id=analysis_id, file_type='html'),
                'json': url_for('download_file', analysis_id=analysis_id, file_type='json'),
                'all': url_for('download_file', analysis_id=analysis_id, file_type='all')
            }
        })
        
    except Exception as e:
        # Clean up on error
        if 'upload_path' in locals() and os.path.exists(upload_path):
            os.remove(upload_path)
        if 'output_dir' in locals() and os.path.exists(output_dir):
            shutil.rmtree(output_dir, ignore_errors=True)
        
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 100MB.'}), 413

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 