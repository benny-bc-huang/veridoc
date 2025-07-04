# Contributing to VeriDoc

Thank you for your interest in contributing to VeriDoc! This document provides guidelines for contributing to the project.

## Development Status

VeriDoc is currently in active development:
- **Phase 1**: ✅ Complete - Core documentation MVP
- **Phase 2**: 🚧 In Progress - Enhanced features
- **Phase 3**: 📋 Planned - CLI integration  
- **Phase 4**: 📋 Planned - Open source polish

## Getting Started

### Prerequisites
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/veridoc.git
cd veridoc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py

# Open browser to http://localhost:5000
```

## Project Structure

```
veridoc/
├── app.py                 # Main FastAPI application
├── core/                  # Backend core modules
│   ├── config.py         # Configuration management
│   ├── file_handler.py   # File system operations
│   └── security.py       # Security validation
├── models/               # Data models
│   └── api_models.py     # API request/response models
├── frontend/             # Frontend application
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript modules
│   └── index.html        # Main HTML template
├── docs/                 # Documentation
└── tests/                # Test files (future)
```

## Development Guidelines

### Code Style
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ES6+ features, maintain consistent indentation
- **CSS**: Use CSS custom properties, maintain component-based organization
- **HTML**: Use semantic HTML5 elements

### Commit Messages
Follow conventional commit format:
```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: code style changes
- refactor: code refactoring
- test: test additions/changes
- chore: maintenance tasks
```

### Development Workflow
1. Create a feature branch from `main`
2. Make your changes with appropriate tests
3. Ensure all tests pass
4. Submit a pull request with clear description

## Areas for Contribution

### High Priority (Phase 2)
- [ ] **Search functionality** - Full-text search across documentation
- [ ] **Large file handling** - Pagination for files > 1MB
- [ ] **Table of contents** - Auto-generated for Markdown files
- [ ] **Find-in-file** - Regex search within documents

### Medium Priority (Phase 3)
- [ ] **CLI integration** - Helper script implementation
- [ ] **Terminal functionality** - Integrated terminal with xterm.js
- [ ] **Syntax highlighting** - Code file support
- [ ] **Performance optimization** - Memory usage < 100MB

### Low Priority (Phase 4)
- [ ] **Testing** - Unit and integration tests
- [ ] **Documentation** - API docs, user guides
- [ ] **CI/CD** - GitHub Actions pipeline
- [ ] **Packaging** - Distribution preparation

## Testing

### Running Tests
```bash
# Python tests (when implemented)
pytest tests/

# Frontend tests (when implemented)
cd frontend && npm test

# Integration tests (when implemented)
python -m pytest tests/integration/
```

### Test Coverage
- Aim for >80% test coverage
- Include unit tests for all new features
- Add integration tests for API endpoints
- Include frontend tests for UI components

## Documentation

### Code Documentation
- Add docstrings to all Python functions/classes
- Use JSDoc comments for JavaScript functions
- Include type hints in Python code
- Document API endpoints with examples

### User Documentation
- Update README.md for new features
- Add usage examples
- Include troubleshooting guides
- Maintain API documentation

## Security

### Security Guidelines
- Never commit secrets or API keys
- Validate all user inputs
- Follow secure coding practices
- Report security issues privately

### File Access Security
- All file access must be within BASE_PATH
- Prevent path traversal attacks
- Validate file extensions and sizes
- Implement proper error handling

## Performance

### Performance Targets
- Application startup: < 2 seconds
- File loading: < 500ms for typical files
- Memory usage: < 100MB total
- Browser response: < 100ms for navigation

### Optimization Guidelines
- Use lazy loading for large datasets
- Implement caching strategies
- Optimize CSS and JavaScript
- Monitor memory usage

## Pull Request Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Pull Request Requirements
- Clear description of changes
- Reference related issues
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass

## Code Review

### Review Process
- All pull requests require review
- Address all feedback before merging
- Maintain project code quality standards
- Ensure compatibility with existing features

### Review Checklist
- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact evaluated

## Release Process

### Versioning
- Follow semantic versioning (SemVer)
- Tag releases with version numbers
- Maintain changelog for releases
- Document breaking changes

### Release Checklist
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Performance targets met
- [ ] Security review completed
- [ ] Changelog updated

## Community

### Communication
- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Follow the code of conduct
- Be respectful and inclusive

### Getting Help
- Check existing issues and documentation
- Ask questions in GitHub Discussions
- Reach out to maintainers if needed

## License

By contributing to VeriDoc, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all contributors who help make VeriDoc better!

---

**Happy coding!** 🚀

For questions about contributing, please open an issue or discussion on GitHub.