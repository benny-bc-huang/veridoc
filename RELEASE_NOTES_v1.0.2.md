# VeriDoc v1.0.2 Release Notes

## Release Date
July 6, 2025

## Overview
This patch release fixes image display issues on PyPI by updating all image references in the README to use absolute GitHub raw content URLs.

## What's Changed

### Bug Fixes
- **Fixed PyPI Image Display**: Updated README.md to use absolute GitHub raw URLs for logo and screenshot images
  - Logo now uses: `https://raw.githubusercontent.com/benny-bc-huang/veridoc/main/logo-dark.png`
  - Screenshot now uses: `https://raw.githubusercontent.com/benny-bc-huang/veridoc/main/img/web-page.png`
  - Images now display correctly on the PyPI project page

### Technical Details
- Changed from relative image paths to absolute GitHub raw content URLs
- No functionality changes - purely documentation updates
- Ensures proper rendering on PyPI and other external documentation sites

## Installation

### From PyPI (Recommended)
```bash
pip install veridoc
```

### From Source
```bash
git clone https://github.com/benny-bc-huang/veridoc.git
cd veridoc
pip install .
```

## Upgrading
If you have v1.0.1 installed, upgrade to v1.0.2:
```bash
pip install --upgrade veridoc
```

## Full Changelog
v1.0.1...v1.0.2

## Acknowledgments
Thank you to all users who reported the image display issue on PyPI!