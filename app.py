#!/usr/bin/env python3
"""
VeriDoc Backend Server
AI-Optimized Documentation Browser
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from typing import Optional, List
import json
import mimetypes
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.security import SecurityManager
from core.file_handler import FileHandler
from core.config import Config
from models.api_models import (
    FileListResponse, FileItem, FileContentResponse, 
    FileMetadata, HealthResponse, ErrorResponse
)

# Initialize configuration
config = Config()
app = FastAPI(
    title="VeriDoc API",
    description="AI-Optimized Documentation Browser API",
    version="1.0.0"
)

# Initialize core components
security_manager = SecurityManager(config.base_path)
file_handler = FileHandler(security_manager)

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=FileResponse)
async def serve_index():
    """Serve the main application"""
    return FileResponse("frontend/index.html")

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        base_path=str(config.base_path),
        memory_usage_mb=0,  # TODO: Implement memory monitoring
        uptime_seconds=0,   # TODO: Implement uptime tracking
        active_connections=0
    )

@app.get("/api/files", response_model=FileListResponse)
async def get_files(
    path: str = Query("/", description="Relative path from base directory"),
    include_hidden: bool = Query(False, description="Include hidden files"),
    sort_by: str = Query("name", description="Sort field: name, size, modified"),
    sort_order: str = Query("asc", description="Sort order: asc, desc")
):
    """Get directory listing"""
    try:
        # Validate and resolve path
        safe_path = security_manager.validate_path(path)
        
        # Get directory listing
        items = await file_handler.list_directory(
            safe_path, 
            include_hidden=include_hidden,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get parent path
        parent_path = "/" if safe_path == config.base_path else str(safe_path.parent.relative_to(config.base_path))
        
        return FileListResponse(
            path=path,
            parent=parent_path,
            items=items,
            total_items=len(items)
        )
        
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Directory not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/file_content", response_model=FileContentResponse)
async def get_file_content(
    path: str = Query(..., description="Relative file path"),
    page: int = Query(1, ge=1, description="Page number"),
    lines_per_page: int = Query(1000, ge=1, le=10000, description="Lines per page"),
    encoding: str = Query("utf-8", description="Text encoding")
):
    """Get file content with pagination"""
    try:
        # Validate and resolve path
        safe_path = security_manager.validate_path(path)
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(safe_path)
        
        # For non-text files, stream the file directly
        if mime_type and not mime_type.startswith('text/'):
            return FileResponse(safe_path, media_type=mime_type)
        
        # For text files, proceed with pagination
        file_size = safe_path.stat().st_size
        if file_size > config.max_file_size:
            raise HTTPException(
                status_code=413, 
                detail=f"File too large. Maximum size: {config.max_file_size // (1024*1024)}MB"
            )
        
        # Get file content
        content_data = await file_handler.get_file_content(
            safe_path,
            page=page,
            lines_per_page=lines_per_page,
            encoding=encoding
        )
        
        return content_data
        
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding not supported")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/file_info")
async def get_file_info(path: str = Query(..., description="Relative file path")):
    """Get file metadata"""
    try:
        safe_path = security_manager.validate_path(path)
        
        if not safe_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        metadata = await file_handler.get_file_metadata(safe_path)
        return metadata
        
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/search")
async def search_files(
    q: str = Query(..., description="Search query"),
    type: str = Query("both", description="Search type: filename, content, both"),
    path: str = Query("", description="Limit search to specific directory"),
    extensions: str = Query("", description="Comma-separated file extensions"),
    limit: int = Query(50, ge=1, le=200, description="Maximum results")
):
    """Search files and content"""
    try:
        # Simple search implementation for MVP
        results = []
        search_path = security_manager.validate_path(path if path else "/")
        
        # Get all files recursively
        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                rel_path = str(file_path.relative_to(config.base_path))
                filename = file_path.name
                
                # Filter by extensions if specified
                if extensions:
                    ext_list = [ext.strip().lower() for ext in extensions.split(",")]
                    file_ext = file_path.suffix.lower()
                    if file_ext not in ext_list and file_ext.lstrip('.') not in ext_list:
                        continue
                
                score = 0
                match_type = None
                snippet = None
                line_number = None
                
                # Filename search
                if type in ["filename", "both"] and q.lower() in filename.lower():
                    score = 0.9 if filename.lower() == q.lower() else 0.7
                    match_type = "filename"
                
                # Content search for text files
                if type in ["content", "both"] and file_handler._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if q.lower() in line.lower():
                                    if not match_type or score < 0.8:
                                        score = 0.8
                                        match_type = "content"
                                        snippet = line.strip()[:100]
                                        line_number = i + 1
                                    break
                    except (UnicodeDecodeError, PermissionError):
                        continue
                
                if match_type:
                    results.append({
                        "path": rel_path,
                        "type": "file",
                        "match_type": match_type,
                        "score": score,
                        "snippet": snippet,
                        "line_number": line_number
                    })
                
                if len(results) >= limit:
                    break
        
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return {
            "query": q,
            "results": results,
            "total_results": len(results),
            "search_time_ms": 0  # TODO: Implement timing
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "code": "INTERNAL_ERROR"
        }
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="VeriDoc Server")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--base-path", help="Base directory path")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    
    args = parser.parse_args()
    
    # Update config if base path provided
    if args.base_path:
        config.base_path = Path(args.base_path).resolve()
        security_manager = SecurityManager(config.base_path)
        file_handler = FileHandler(security_manager)
    
    print(f"🚀 VeriDoc server starting on http://{args.host}:{args.port}")
    print(f"📁 Base path: {config.base_path}")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="debug" if args.debug else "info"
    )