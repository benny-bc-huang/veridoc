# Contributing to VeriDoc

Thank you for your interest in contributing to VeriDoc! This document provides guidelines for contributing to the project.

## Development Status

VeriDoc is currently in Phase 4 (Open Source Preparation):
- **Phase 1**: ✅ Complete - Core documentation MVP
- **Phase 2**: ✅ Complete - Enhanced features (search, pagination, ToC)
- **Phase 3**: ✅ Complete - CLI integration, terminal features, Git operations
- **Phase 4**: 🚧 In Progress - Open source preparation and polish

## Getting Started

### Prerequisites
- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Git

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/benny-bc-huang/veridoc.git
cd veridoc

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
python app.py
# Opens automatically at http://localhost:5000

# Alternative: Use CLI integration
./veridoc                     # Launch VeriDoc from any directory
./veridoc docs/               # Open specific directory
./veridoc README.md           # Open specific file
```

## Project Structure

```
veridoc/
├── veridoc               # Executable CLI script
├── app.py                # Main FastAPI application
├── core/                 # Backend core modules
│   ├── config.py        # Configuration management
│   ├── file_handler.py  # File system operations
│   ├── git_integration.py # Git operations
│   └── security.py      # Security validation
├── models/              # API data models
│   └── api_models.py    # Request/response models
├── frontend/            # Frontend application
│   ├── css/             # Component stylesheets
│   ├── js/              # JavaScript modules & components
│   └── index.html       # Main HTML template
├── completions/         # Shell completion scripts
├── docs/                # Documentation
└── tests/               # Test files (Phase 4)
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

## Current Phase 4 Priorities

### High Priority (Security & Stability)
- [ ] **Testing**: Implement comprehensive test suite (unit, integration, security)
- [ ] **Error Handling**: Replace generic exception handling with specific exceptions
- [ ] **Terminal Security**: Add command restrictions and session isolation
- [ ] **Documentation**: Complete API documentation and deployment guides

### Medium Priority (Performance & Quality)
- [ ] **Search Optimization**: Implement indexing and caching for large codebases
- [ ] **Code Quality**: Fix PEP 8 violations and extract embedded classes
- [ ] **Performance**: Optimize memory usage and file operations
- [ ] **User Experience**: Complete TODO items and enhance error messages

### Low Priority (Polish)
- [ ] **Documentation**: Generate OpenAPI docs, create deployment guide
- [ ] **Code Cleanup**: Remove debug console.log statements
- [ ] **Accessibility**: Add a11y considerations to frontend

## Testing

### Current Status
VeriDoc needs comprehensive testing infrastructure as part of Phase 4.

### Testing Priorities
1. **Unit Tests**: Core functionality (security, file handling, Git operations)
2. **Integration Tests**: API endpoints, WebSocket terminal
3. **Security Tests**: Path traversal prevention, input validation
4. **Performance Tests**: Memory usage, search performance

### Test Structure (Planned)
```bash
tests/
├── unit/
│   ├── test_security.py      # SecurityManager tests
│   ├── test_file_handler.py  # FileHandler tests
│   └── test_git_integration.py # Git operations tests
├── integration/
│   ├── test_api.py           # API endpoint tests
│   └── test_terminal.py      # Terminal WebSocket tests
├── security/
│   └── test_path_traversal.py # Security vulnerability tests
└── conftest.py               # Test configuration
```

### Test Coverage
- Aim for >80% test coverage
- Include unit tests for all core functionality
- Add integration tests for API endpoints
- Include security tests for vulnerability prevention

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

### Security Model
- All file access restricted to BASE_PATH
- Path traversal prevention with symbolic link validation
- Input sanitization for all API parameters
- Read-only interface design
- Terminal commands logged for audit

### Security Contributions
- Never commit secrets or API keys
- Validate all user inputs
- Follow secure coding practices
- Report security issues privately to maintainers

## Performance

### Performance Targets
- **Application startup**: < 2 seconds ✅
- **File loading**: < 500ms for typical files ✅
- **Search response**: < 200ms across 1000+ files ✅
- **Memory usage**: < 100MB total ✅
- **Browser response**: < 100ms for navigation ✅

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
- Clear description of changes and motivation
- Reference related issues using `#issue-number`
- Include tests for new functionality
- Update documentation as needed
- Ensure all CI checks pass
- Follow code style guidelines

## Code Review

### Review Process
- All pull requests require review
- Address all feedback before merging
- Maintain project code quality standards
- Ensure compatibility with existing features

### Review Checklist
- [ ] Code follows project style guidelines (PEP 8, ES6+)
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact evaluated
- [ ] No hardcoded values or debug code

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
- [ ] CHANGELOG.md updated
- [ ] Version numbers incremented

## Community

### Communication
- Use GitHub Issues for bug reports
- Use GitHub Discussions for questions
- Follow the code of conduct
- Be respectful and inclusive

### Getting Help
- Check existing issues and documentation first
- Search GitHub Discussions for similar questions
- Open an issue with clear description and steps to reproduce
- Provide system information and error messages

## License

By contributing to VeriDoc, you agree that your contributions will be licensed under the MIT License.

## Acknowledgments

Thank you to all contributors who help make VeriDoc better!

---

**Happy coding!** 🚀

For questions about contributing, please open an issue or discussion on GitHub.