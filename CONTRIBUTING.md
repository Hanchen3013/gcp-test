# Contributing to GCP Data Pipeline

Thank you for your interest in contributing to the GCP Data Pipeline project!

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Python version, OS, etc.)

### Suggesting Enhancements

We welcome suggestions! Please open an issue with:
- A clear description of the enhancement
- Use cases and benefits
- Any implementation ideas

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Add or update tests as needed
5. Ensure all tests pass (`make test`)
6. Run linting (`make lint`)
7. Commit your changes (`git commit -m 'Add some feature'`)
8. Push to your branch (`git push origin feature/your-feature`)
9. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/gcp-test.git
cd gcp-test

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
make test

# Run linting
make lint
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (`make format`)
- Maximum line length: 100 characters
- Add docstrings to all functions and classes
- Write meaningful commit messages

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest for testing
- Mock external dependencies (GCP services)

### Documentation

- Update README.md for user-facing changes
- Add docstrings for all public APIs
- Include examples for new features

## Questions?

Feel free to open an issue for any questions!
