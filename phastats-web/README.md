# Phastats Web Application

A Flask-based web interface for the Phastats FASTQ quality analysis tool.

## Features

- **Modern Web Interface**: Clean, responsive Bootstrap-based UI
- **Drag & Drop Upload**: Easy file upload with progress tracking
- **Multiple Output Formats**: HTML reports, JSON data, and high-quality plots
- **Batch Download**: Download all results as a ZIP package
- **API Support**: RESTful API for programmatic access
- **Auto-cleanup**: Automatic file cleanup for security

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the phastats source code to the `phastats/` directory
4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

### Development Setup

For development with additional dependencies:

```bash
pip install -r requirements.txt
pip install gunicorn  # For production deployment
```

## Usage

### Web Interface

1. Navigate to the home page
2. Upload a FASTQ file (supported formats: .fastq, .fq, .fastq.gz, .fq.gz)
3. Optionally adjust analysis parameters
4. Click "Start Analysis"
5. View and download results

### API Usage

**Analyze a FASTQ file:**

```bash
curl -X POST \
  -F "file=@your_file.fastq" \
  -F "quality_threshold=20" \
  -F "encoding=phred33" \
  http://localhost:5000/api/analyze
```

**Response format:**
```json
{
  "success": true,
  "analysis_id": "uuid-string",
  "download_urls": {
    "html": "/download/uuid-string/html",
    "json": "/download/uuid-string/json", 
    "all": "/download/uuid-string/all"
  }
}
```

## Configuration

### Environment Variables

- `FLASK_ENV`: Set to `development` for debug mode
- `SECRET_KEY`: Change the secret key for production deployments
- `MAX_CONTENT_LENGTH`: Maximum upload file size (default: 100MB)

### Application Settings

Edit `app.py` to modify:

- `UPLOAD_FOLDER`: Directory for temporary file uploads
- `TEMP_FOLDER`: Directory for analysis results
- `ALLOWED_EXTENSIONS`: Supported file extensions
- Auto-cleanup interval (default: 2 hours)

## Deployment

### Heroku Deployment

1. Create a new Heroku app:
   ```bash
   heroku create phastats-demo
   ```

2. Push to Heroku:
   ```