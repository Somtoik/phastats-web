# Phastats - Advanced FASTQ Quality Analysis Tool

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://phastats-demo-8328e0496479.herokuapp.com/)
[![GitHub Pages](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://somtoik.github.io/phastats/)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Professional FASTQ Quality Analysis Tool with Modern Web Interface**

Phastats is a comprehensive bioinformatics tool that provides detailed quality control analysis for FASTQ sequencing data. It offers both command-line and web-based interfaces with interactive visualizations and professional reporting capabilities.

## Live Demo

**Try it now:** [phastats-demo-8328e0496479.herokuapp.com](https://phastats-demo-8328e0496479.herokuapp.com/)

Upload your FASTQ files and get instant professional analysis results!

## Documentation

**Full Documentation:** [somtoik.github.io/phastats](https://somtoik.github.io/phastats/)

## Key Features

- **Comprehensive Analysis**: Quality scores, sequence lengths, GC content, and per-base content analysis
- **N50 Calculation**: Genome assembly quality metric not available in FastQC
- **Dual Interface**: Both command-line tool and modern web application
- **Responsive Design**: Professional, mobile-friendly web interface
- **Interactive Visualizations**: High-quality plots and charts
- **Multiple Output Formats**: HTML, JSON, CSV, and TSV reports
- **High Performance**: Optimized algorithms for large file processing
- **Docker Ready**: Containerized for easy deployment

## Performance Comparison

| Feature | Phastats | FastQC |
|---------|----------|---------|
| **N50 Calculation** | Included | Not Available |
| **Web Interface** | Built-in | Desktop Only |
| **Modern UI** | Responsive | Traditional |
| **Output Formats** | HTML, JSON, CSV, TSV | HTML, TXT |
| **Runtime (SRR29246139.fastq)** | 52.2 seconds | 12.76 seconds |

## Project Structure

```
phastats/
├── phastats-main/phastats/    # Command-line tool & PyPI package
│   ├── src/phastats/          # Core Python modules
│   ├── tests/                 # Test suite
│   ├── setup.py               # Package configuration
│   └── pyproject.toml         # Modern Python config
├── phastats-web/              # Web application
│   ├── app.py                 # Flask web server
│   ├── templates/             # HTML templates
│   ├── static/                # CSS & assets
│   ├── Dockerfile             # Container config
│   └── requirements.txt       # Dependencies
├── docs/                      # GitHub Pages website
│   ├── index.html             # Landing page
│   └── getting-started.html   # Documentation
└── .github/workflows/         # CI/CD pipeline
```

## Quick Start

### Web Interface (Easiest)
Visit the **[Live Demo](https://phastats-demo-8328e0496479.herokuapp.com/)** - no installation required!

### Command Line Tool

```bash
# Install from PyPI (when published)
pip install phastats

# Or install from source
git clone https://github.com/somtoik/phastats.git
cd phastats/phastats-main/phastats
pip install -e .

# Run analysis
phastats input.fastq
```

### Local Web Development

```bash
git clone https://github.com/somtoik/phastats.git
cd phastats/phastats-web
pip install -r requirements.txt
python app.py
```

### Docker Deployment

```bash
cd phastats-web
docker build -t phastats-web .
docker run -p 5000:5000 phastats-web
```

## Example Analysis Output

- **Quality Distribution**: Per-base quality scores and statistics
- **Length Analysis**: Sequence length distribution with N50
- **GC Content**: Per-sequence GC analysis and bias detection  
- **Per-Base Content**: Base composition across read positions
- **Summary Statistics**: Comprehensive quality metrics

## Technologies Used

- **Backend**: Python, Flask, NumPy, Pandas, SciPy, Matplotlib
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Deployment**: Heroku, Docker
- **CI/CD**: GitHub Actions
- **Documentation**: GitHub Pages

## Professional Features

- **Production-ready deployment** on Heroku
- **Professional documentation** with GitHub Pages
- **Automated CI/CD pipeline** with GitHub Actions
- **Docker containerization** for easy deployment
- **Comprehensive test suite** with pytest
- **Code quality tools** (Black, Flake8, MyPy)
- **Modern Python packaging** (setuptools, pyproject.toml)
- **Responsive web design** for all devices

## Requirements

- **Python 3.7+**
- **Dependencies**: Flask, NumPy, Pandas, SciPy, Matplotlib
- **Browser**: Modern browser for web interface
- **Memory**: Scales with file size (optimized for large files)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](phastats-main/phastats/LICENSE) file for details.

## Author

**somtochukwu Ikeanyi**
- GitHub: [@somtoik](https://github.com/somtoik)
- Email: somtoikeanyi1@gmail.com

## Links

- **Live Demo**: [phastats-demo-8328e0496479.herokuapp.com](https://phastats-demo-8328e0496479.herokuapp.com/)
- **Documentation**: [somtoik.github.io/phastats](https://somtoik.github.io/phastats/)
- **PyPI Package**: [pypi.org/project/phastats](https://pypi.org/project/phastats/) *(coming soon)*
- **Docker Hub**: [hub.docker.com/r/somtoik/phastats-web](https://hub.docker.com/r/somtoik/phastats-web) *(coming soon)*

---

**If you find this project useful, please consider giving it a star!** 