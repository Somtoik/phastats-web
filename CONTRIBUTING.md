# Contributing to Phastats

We're excited that you're interested in contributing to Phastats! This document outlines the process for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.7 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Local Development

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/somtoik/phastats.git
   cd phastats
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   # For command-line tool development
   cd phastats-main/phastats
   pip install -e ".[dev]"
   
   # For web application development
   cd ../../phastats-web
   pip install -r requirements.txt
   ```

4. **Run Tests**
   ```bash
   # Command-line tool tests
   cd phastats-main/phastats
   pytest tests/
   
   # Web application tests
   cd ../../phastats-web
   pytest tests/ || echo "Web tests not yet implemented"
   ```

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes
- Follow the existing code style and patterns
- Add tests for new functionality
- Update documentation as needed

### 3. Code Quality Checks
```bash
# Format code
black src/

# Check linting
flake8 src/

# Type checking
mypy src/
```

### 4. Run Tests
```bash
pytest tests/ -v --cov=src
```

### 5. Commit Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation updates
- `test:` for adding tests
- `refactor:` for code refactoring

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Code Style Guidelines

### Python Code Style
- Follow PEP 8 style guide
- Use Black for code formatting (line length: 88 characters)
- Use type hints where appropriate
- Write descriptive docstrings for functions and classes

### Testing
- Write unit tests for all new functionality
- Aim for high test coverage (>90%)
- Use pytest fixtures for test setup
- Mock external dependencies appropriately

### Documentation
- Update README.md if adding new features
- Add docstrings to all public functions
- Update GitHub Pages documentation if needed

## Project Structure

```
phastats/
├── phastats-main/phastats/    # Command-line tool
│   ├── src/phastats/          # Source code
│   ├── tests/                 # Test files
│   ├── setup.py               # Package setup
│   └── pyproject.toml         # Modern Python config
├── phastats-web/              # Web application
│   ├── app.py                 # Flask application
│   ├── templates/             # HTML templates
│   ├── static/                # Static files
│   └── requirements.txt       # Dependencies
├── docs/                      # GitHub Pages documentation
└── .github/workflows/         # CI/CD configuration
```

## Types of Contributions

### Bug Reports
- Use the GitHub issue template
- Include steps to reproduce
- Provide system information
- Include sample data if relevant

### Feature Requests
- Describe the use case
- Explain the expected behavior
- Consider backward compatibility

### Code Contributions
- Start with small, focused changes
- Include tests and documentation
- Follow the code review process

### Documentation
- Improve existing documentation
- Add examples and tutorials
- Fix typos and improve clarity

## Release Process

1. **Version Bumping**
   - Update version in `src/phastats/__init__.py`
   - Update CHANGELOG.md
   - Create a git tag: `git tag v1.0.0`

2. **Testing**
   - All CI/CD checks must pass
   - Manual testing of core functionality

3. **Publishing**
   - Push tag to trigger automated PyPI release
   - Update GitHub Pages documentation

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow

### Communication
- Use GitHub issues for bug reports and feature requests
- Use pull requests for code changes
- Be clear and concise in communications

## Getting Help

- Check existing issues and documentation
- Ask questions in GitHub discussions
- Reach out to maintainers for guidance

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- GitHub contributors page

Thank you for contributing to Phastats! 