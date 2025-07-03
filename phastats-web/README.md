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
   heroku create your-app-name
   ```

2. Push to Heroku:
   ```bash
   git push heroku main
   ```

3. The `Procfile` is already configured for Heroku

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

Build and run:
```bash
docker build -t phastats-web .
docker run -p 5000:5000 phastats-web
```

### Traditional Server Deployment

Using gunicorn (recommended for production):

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:5000 --workers 4
```

## Security Features

- **File Validation**: Only allows FASTQ file extensions
- **Size Limits**: 100MB maximum file size
- **Secure Filenames**: Uses werkzeug's secure_filename()
- **Auto-cleanup**: Files automatically deleted after 2 hours
- **Input Sanitization**: All user inputs are validated

## File Structure

```
phastats-web/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Heroku deployment configuration
├── README.md             # This file
├── .gitignore           # Git ignore patterns
├── templates/           # HTML templates
│   ├── base.html        # Base template
│   ├── index.html       # Upload page
│   └── results.html     # Results page
├── static/              # Static assets
│   └── css/
│       └── custom.css   # Custom styles
├── phastats/           # Phastats source code (copy here)
├── uploads/            # Temporary uploads (auto-created)
└── temp/              # Analysis results (auto-created)
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| POST | `/upload` | Upload and analyze file |
| GET | `/results/<id>` | View results page |
| GET | `/download/<id>/<type>` | Download results |
| GET | `/download_plot/<id>/<name>` | Download plot |
| GET | `/view_plot/<id>/<name>` | View plot inline |
| POST | `/api/analyze` | API analysis endpoint |
| GET | `/health` | Health check |

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure phastats source code is in the `phastats/` directory
2. **Permission errors**: Check file system permissions for upload/temp directories
3. **Memory issues**: Large files may require more RAM; consider increasing worker timeout
4. **Port conflicts**: Change the port in `app.py` if 5000 is already in use

### Debug Mode

Enable debug mode for development:

```bash
export FLASK_ENV=development
python app.py
```

### Logs

Check application logs for detailed error information:

```bash
# For Heroku
heroku logs --tail

# For local development
# Logs are printed to console when running with python app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project follows the same license as the main Phastats project.

## Support

For issues and questions:
1. Check this README
2. Review the main Phastats documentation
3. Submit an issue on the project repository 