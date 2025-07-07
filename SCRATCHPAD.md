# VeriDoc Improvements Scratchpad

## Task 1: Fix Integration Tests

### Problem Analysis
- Integration tests are disabled due to httpx/FastAPI dependency conflicts
- Need to investigate the specific dependency versions causing issues

### Investigation Steps
1. Check current requirements.txt for version constraints
2. Look at test files to understand httpx usage
3. Research compatible versions of httpx and FastAPI
4. Update dependencies and test

## Task 2: Dark/Light Theme Toggle

### Implementation Plan
1. Add theme state management in frontend
2. Create CSS variables for themeable colors
3. Add toggle button in UI header
4. Persist theme preference in localStorage
5. Update all CSS to use theme variables

### Key Files to Modify
- frontend/css/main.css - Add CSS variables
- frontend/js/app.js - Theme state management
- frontend/index.html - Toggle button UI

## Task 3: Fuzzy Search Implementation

### Approach
- Use Levenshtein distance or similar algorithm
- Consider using fuse.js library for frontend search
- Backend could use python-Levenshtein or rapidfuzz

### Implementation Areas
- Modify search_optimization.py for backend fuzzy matching
- Update frontend search to show relevance scores
- Add search settings for fuzzy threshold

## Task 4: API Documentation (Swagger/ReDoc)

### FastAPI Built-in Support
- FastAPI automatically generates OpenAPI schema
- Just need to add proper endpoints and configure
- Add description metadata to all endpoints
- Configure Swagger UI and ReDoc paths

## Progress Tracking
- [x] Task 1: Integration tests fixed ✓ (All 36 tests passing, updated CONTRIBUTING.md)
- [x] Task 2: Theme toggle implemented ✓ (Light/dark theme with persistence, Prism theme switching)
- [x] Task 3: Fuzzy search added ✓ (Levenshtein distance, enhanced matching, acronym support)
- [ ] Task 4: API docs configured
- [ ] Task 5: Rate limiting added
- [ ] Task 6: Search previews implemented
- [ ] Task 7: Performance dashboard created