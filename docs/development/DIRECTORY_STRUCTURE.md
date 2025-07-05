# VeriDoc Directory Structure

This document describes the organization of the VeriDoc project directory structure and the rationale behind each directory.

## Project Overview

VeriDoc follows a clean, modular directory structure that separates concerns and maintains clear boundaries between different aspects of the application.

## Root Directory Structure

```
/root/veridoc/
├── app.py                    # Main FastAPI server entry point
├── veridoc                   # CLI script (executable)
├── requirements.txt          # Python dependencies
├── pyproject.toml           # Project configuration
├── setup.cfg                # Tool configuration
├── install.sh               # Installation script
├── CLAUDE.md                # Claude Code instructions
├── README.md                # Project documentation
├── LICENSE                  # License file
├── CHANGELOG.md             # Version history
├── core/                    # Backend core modules
├── models/                  # API data models
├── frontend/                # Web application
├── completions/             # Shell completion scripts
├── docs/                    # Documentation (organized by type)
├── tests/                   # Test files and test suites
└── dev/                     # Development artifacts
```

## Directory Descriptions

### Core Application Files

- **`app.py`**: Main FastAPI server application with API endpoints and WebSocket handlers
- **`veridoc`**: CLI script that provides command-line interface for launching VeriDoc
- **`requirements.txt`**: Python package dependencies
- **`install.sh`**: Installation script for setting up VeriDoc

### Backend Modules (`/core/`)

```
core/
├── __init__.py              # Python package initialization
├── config.py                # Configuration management
├── file_handler.py          # File system operations and security
├── git_integration.py       # Git operations and repository management
├── security.py              # Security validation and path controls
├── terminal_security.py     # Terminal command filtering and audit
├── search_optimization.py   # Search indexing and caching engine
├── performance_monitor.py   # Real-time performance metrics
└── enhanced_error_handling.py # Comprehensive exception management
```

**Purpose**: Contains the core backend logic with clear separation of concerns. Each module handles a specific aspect of the application.

### Data Models (`/models/`)

```
models/
├── __init__.py              # Python package initialization
└── api_models.py            # Pydantic models for API requests/responses
```

**Purpose**: Defines the data structures used throughout the application, ensuring type safety and validation.

### Frontend Application (`/frontend/`)

```
frontend/
├── index.html               # Main HTML template
├── css/                     # Stylesheets
│   ├── main.css            # Base styles and variables
│   ├── layout.css          # Layout and positioning
│   └── components.css      # Component-specific styles
└── js/                     # JavaScript modules
    ├── app.js              # Main application logic
    ├── components/         # UI components
    │   ├── content-viewer.js  # File content rendering
    │   ├── file-tree.js      # Directory navigation
    │   ├── search.js         # Search functionality
    │   └── terminal.js       # Terminal integration
    └── utils/              # Utility modules
        ├── api.js            # API communication
        ├── markdown.js       # Markdown rendering
        └── url-handler.js    # URL routing and navigation
```

**Purpose**: Contains the web application with clear separation between styles, components, and utilities. Follows vanilla JavaScript best practices.

### Shell Completions (`/completions/`)

```
completions/
├── bash_completion.sh       # Bash completion script
├── fish_completion.fish     # Fish shell completion
└── zsh_completion.zsh       # Zsh completion script
```

**Purpose**: Provides shell completion for the VeriDoc CLI across different shell environments.

### Documentation (`/docs/`)

```
docs/
├── specs/                   # Technical specifications
│   ├── API_SPEC.md         # Backend API documentation
│   ├── CLI_SPEC.md         # CLI interface specification
│   └── UI_SPEC.md          # Frontend UI specification
├── development/            # Development documentation
│   ├── ALIGNMENT_ASSESSMENT.md  # Project alignment analysis
│   ├── ARCHITECTURE.md          # System architecture
│   ├── CONTRIBUTING.md          # Contribution guidelines
│   ├── DEVELOPMENT_PLAN.md      # Development roadmap
│   └── DIRECTORY_STRUCTURE.md   # This file
└── logs/                   # Development logs
    └── dev-log-2025-07-04.md   # Session development log
```

**Purpose**: Centralized documentation organized by type. Specifications for technical details, development docs for process and architecture, logs for historical records.

### Test Files (`/tests/`)

```
tests/
├── __init__.py             # Python package initialization
├── conftest.py             # Pytest fixtures and configuration
├── test_unit/              # Unit tests for individual components
│   ├── test_security.py    # Security module tests
│   ├── test_search.py      # Search engine tests
│   └── test_performance.py # Performance monitor tests
├── test_integration/       # Integration tests
│   ├── test_api.py         # API endpoint tests
│   └── test_terminal.py    # Terminal integration tests
├── test_security/          # Security-specific tests
│   ├── test_path_traversal.py # Path traversal attack tests
│   └── test_command_injection.py # Command injection tests
├── frontend/               # Frontend-specific tests
│   └── test.html          # HTML test file
├── test_readme.md         # Test documentation
└── test_script.js         # JavaScript test files
```

**Purpose**: Comprehensive test suite with unit, integration, and security tests. Organized by test type for easy navigation and maintenance.

### Development Artifacts (`/dev/`)

```
dev/
├── initialize.prompt      # Claude initialization prompt
├── project_statement.md   # Project statement document
└── project_statement.md:Zone.Identifier  # Windows metadata
```

**Purpose**: Contains development-specific files that are not part of the production application but are useful for development workflows.

## Design Principles

### 1. Separation of Concerns
- Backend logic isolated in `/core/`
- Frontend organized by function (components, utils)
- Documentation grouped by purpose
- Tests consolidated in dedicated directory

### 2. Clear Naming Conventions
- Descriptive directory names
- Consistent file naming patterns
- Logical grouping by functionality

### 3. Scalability
- Modular structure supports growth
- Clear boundaries between components
- Easy to add new modules or features

### 4. Developer Experience
- Clean root directory (only essential files)
- Logical file organization
- Easy navigation and discovery

## File Organization Rules

### Root Directory
**Keep minimal**: Only essential application files (entry points, configs, core docs)

### Subdirectories
- **`/core/`**: One module per major backend concern
- **`/frontend/js/components/`**: One file per UI component
- **`/frontend/js/utils/`**: Reusable utility functions
- **`/docs/specs/`**: Technical specifications
- **`/docs/development/`**: Process and architecture docs
- **`/tests/`**: Mirror application structure for tests

### Documentation Placement
- **Root**: Core project docs (README, LICENSE, CLAUDE.md)
- **`/docs/specs/`**: API and technical specifications
- **`/docs/development/`**: Architecture, processes, planning
- **`/docs/logs/`**: Development session logs

## Maintenance Guidelines

### Adding New Features
1. Backend logic: Add modules to `/core/`
2. Frontend components: Add to `/frontend/js/components/`
3. Utilities: Add to appropriate `/utils/` directory
4. Documentation: Update relevant specs and add to `/docs/`
5. Tests: Add to `/tests/` mirroring the application structure

### File Naming
- Use descriptive names that indicate purpose
- Use kebab-case for directories (e.g., `file-tree.js`)
- Use snake_case for Python modules (e.g., `file_handler.py`)
- Group related files in logical directories

### Documentation Updates
- Update this file when adding new directories
- Update relevant specifications when changing APIs
- Document architectural decisions in `/docs/development/`

## Benefits of This Structure

1. **Maintainability**: Clear organization makes code easy to find and modify
2. **Onboarding**: New developers can quickly understand the project layout
3. **Scalability**: Structure supports growth without reorganization
4. **Tooling**: Consistent structure works well with development tools
5. **Collaboration**: Clear boundaries reduce merge conflicts

---

*This document should be updated whenever the directory structure changes significantly.*