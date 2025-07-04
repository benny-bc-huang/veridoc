# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VeriDoc is a lightweight, open-source documentation browser designed for AI-assisted development workflows. It provides rapid documentation verification and context gathering for developers working with AI coding assistants.

**Core Purpose**: Sub-second documentation access optimized for AI development workflows, running locally at `http://localhost:5000`

## Architecture

### Technology Stack
- **Backend**: Python Flask/FastAPI or Node.js Express
- **Frontend**: Vanilla HTML/CSS/JavaScript (no frameworks)
- **Terminal Integration**: xterm.js for integrated terminal
- **Content Rendering**: Markdown with Mermaid diagram support

### Key Components
- **Backend Server**: File system APIs, security validation, terminal proxy
- **Frontend Application**: Two-pane layout (file tree + content viewer)
- **CLI Integration**: Helper script for seamless terminal workflow integration

### Design Principles
- **Verification-Optimized**: Read-only interface prioritizing viewing speed over editing
- **Performance Independence**: Response time constant regardless of documentation volume
- **Zero-Context-Switch**: <500ms startup time to maintain AI development flow
- **Terminal-Native**: Direct integration with command-line AI workflows

## Development Commands

Since this is a new project without existing build configuration, typical commands would be:

```bash
# For Python backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py

# For Node.js backend
npm install
npm start
npm test
npm run dev

# CLI integration
./veridoc docs/api-spec.md 42
./veridoc docs/
```

## Performance Targets

- **Application startup**: < 2 seconds
- **File loading**: < 500ms for typical files
- **Memory usage**: < 100MB total
- **Browser response time**: < 100ms for navigation

## Security Model

- All file access restricted to BASE_PATH (server launch directory)
- Path traversal prevention with explicit symbolic link rejection
- Input validation for all API parameters
- Terminal commands logged to `./logs/server.log`

## Development Phases

1. **Phase 1**: Core documentation MVP with backend APIs and frontend layout
2. **Phase 2**: Enhanced documentation features (pagination, navigation, search)
3. **Phase 3**: CLI integration and basic code support
4. **Phase 4**: Open source preparation and polish

## File Structure Priorities

### Content Rendering Priority
1. **Tier 1 (MVP)**: `.md`, `.mmd`, `.txt` files
2. **Tier 2**: `.json`, `.yaml`, `.xml`, code files with syntax highlighting
3. **Tier 3**: Images, binary file detection

### File Size Handling
- Files > 1MB: Paginated at 1000 lines per page
- Files > 10MB: Warning prompt before loading
- Files > 50MB: Rejected with alternative suggestions

## URL Navigation
- `/?path=<file_path>&line=<line_number>` - Direct file/line access
- Graceful fallback to directory view on invalid paths
- Browser history support for navigation

## Git Workflow

**IMPORTANT**: Always use git for code changes. Follow this workflow for all development:

### Before Making Changes
```bash
git status              # Check current state
git diff               # Review uncommitted changes  
git log --oneline -5   # Check recent commits
```

### After Making Changes
```bash
git add .                              # Stage all changes
git commit -m "type(scope): message"   # Commit with descriptive message
git push origin main                   # Push to GitHub
```

### Commit Message Format
- **feat**: new feature
- **fix**: bug fix
- **docs**: documentation changes
- **style**: code style changes
- **refactor**: code refactoring
- **test**: test additions/changes
- **chore**: maintenance tasks

### Examples
```bash
git commit -m "feat(file-tree): add directory navigation system"
git commit -m "fix(layout): resolve panel scrolling synchronization"
git commit -m "docs(readme): update installation instructions"
```

### Repository Status
- **GitHub Repository**: https://github.com/benny-bc-huang/veridoc (private)
- **Current Branch**: main
- **Phase Status**: Phase 1 MVP Complete ✅