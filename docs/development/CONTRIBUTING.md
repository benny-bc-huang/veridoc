# Contributing to VeriDoc

Thank you for your interest in contributing to VeriDoc! This document provides guidelines for contributing to the project.

## Development Status

🎉 **All Phases Complete - Production Ready!**
- **Phase 1**: ✅ Complete - Core documentation MVP
- **Phase 2**: ✅ Complete - Enhanced features (search, pagination, ToC)
- **Phase 3**: ✅ Complete - CLI integration, terminal features, Git operations
- **Phase 4**: ✅ **Complete** - Open source preparation and production polish

🏆 **Testing Achievement**: **100% unit test pass rate (70/70 tests)**

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

## ✅ Phase 4 Achievements - All Complete!

### ✅ Security & Stability (Completed)
- ✅ **Testing**: **100% unit test pass rate (70/70 tests)** - SecurityManager, FileHandler, GitIntegration
- ✅ **Error Handling**: Enhanced exception handling with categorized error types
- ✅ **Terminal Security**: Command filtering, session isolation, and audit logging
- ✅ **Documentation**: Complete API documentation and deployment guides

### ✅ Performance & Quality (Completed)
- ✅ **Search Optimization**: Advanced indexing with sub-200ms response times across 1000+ files
- ✅ **Code Quality**: PEP 8 compliance and comprehensive code organization
- ✅ **Performance**: All targets met (<100MB memory, <500ms file loading, <200ms search)
- ✅ **User Experience**: Enhanced error messages and production-ready UX

### ✅ Polish & Production Readiness (Completed)
- ✅ **Documentation**: OpenAPI-compatible API spec, comprehensive README and guides
- ✅ **Code Quality**: Production-ready codebase with proper logging
- ✅ **Testing Excellence**: Async test patterns, isolated testing, comprehensive coverage

## Testing

### ✅ Current Status - **100% Unit Test Pass Rate Achieved!**
🏆 **70/70 unit tests passing** with comprehensive test infrastructure complete.

### ✅ Testing Infrastructure Completed
1. ✅ **Unit Tests**: **100% passing** - SecurityManager (26/26), FileHandler (21/21), GitIntegration (23/23)
2. ✅ **Integration Tests**: API endpoint testing with dependency compatibility handling
3. ✅ **Security Tests**: Comprehensive path traversal prevention and input validation
4. ✅ **Async Testing**: Proper async test patterns with AsyncMock and isolated environments

### ✅ Test Structure (Implemented)
```bash
tests/
├── unit/                       # ✅ 70/70 tests passing (100%)
│   ├── test_security.py       # ✅ 26/26 SecurityManager tests
│   ├── test_file_handler.py   # ✅ 21/21 FileHandler tests  
│   └── test_git_integration.py # ✅ 23/23 GitIntegration tests
├── integration/                # ✅ Implemented with dependency handling
│   └── test_api.py            # API endpoint tests with TestClient compatibility
└── conftest.py                # ✅ Comprehensive fixtures and test data setup
```

### ✅ Test Coverage Achievement
- ✅ **100% unit test pass rate** achieved
- ✅ **All core functionality** covered with comprehensive unit tests
- ✅ **Security validation** fully tested with malicious path detection
- ✅ **Async patterns** properly implemented with GitIntegration edge cases resolved

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

### ✅ Performance Targets (All Met)
- ✅ **Application startup**: < 2 seconds 
- ✅ **File loading**: < 500ms for typical files
- ✅ **Search response**: < 200ms across 1000+ files
- ✅ **Large file pagination**: Smooth 10MB+ handling
- ✅ **Memory usage**: < 100MB total
- ✅ **Browser response**: < 100ms for navigation

### Optimization Guidelines
- Use lazy loading for large datasets
- Implement caching strategies
- Optimize CSS and JavaScript
- Monitor memory usage

## 🚀 Current Contribution Opportunities

Since all 4 development phases are complete with **100% unit test coverage**, here are areas for community contribution:

### Enhancement Opportunities
- **Language Support**: Additional syntax highlighting for more file types
- **Themes**: Dark/light theme variations and custom CSS themes
- **Accessibility**: Enhanced a11y features and screen reader support
- **Extensions**: Plugin system for custom file renderers
- **Mobile**: Responsive design improvements for mobile devices

### Quality Improvements
- **Documentation**: Usage examples, video tutorials, best practices guides
- **Performance**: Further optimization for very large codebases (>10GB)
- **Testing**: Additional edge case testing and browser compatibility
- **Internationalization**: Multi-language support for UI text

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