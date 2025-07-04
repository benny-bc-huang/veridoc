#!/usr/bin/env python3
"""
VeriDoc Backend Server
AI-Optimized Documentation Browser
"""

import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import uvicorn
from typing import Optional, List
import json
import mimetypes
from datetime import datetime
import asyncio
import subprocess
import pty
import select
import termios
import struct
import fcntl

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.security import SecurityManager
from core.file_handler import FileHandler
from core.config import Config
from core.git_integration import GitIntegration
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
git_integration = GitIntegration(config.base_path)

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
                    filename_lower = filename.lower()
                    query_lower = q.lower()
                    
                    if filename_lower == query_lower:
                        # Exact filename match gets perfect score
                        score = 1.0
                    elif filename_lower.startswith(query_lower):
                        # Filename starts with query gets high score
                        score = 0.9
                    else:
                        # Filename contains query gets good score
                        score = 0.7
                    match_type = "filename"
                
                # Content search for text files
                if type in ["content", "both"] and file_handler._is_text_file(file_path):
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()
                            for i, line in enumerate(lines):
                                if q.lower() in line.lower():
                                    # Only update if no filename match or content match is better
                                    content_score = 0.6 if line.strip().lower() == q.lower() else 0.4
                                    if not match_type or (match_type == "content" and content_score > score) or (match_type == "filename" and score < 0.8):
                                        score = max(score, content_score) if match_type == "filename" else content_score
                                        match_type = "content" if not match_type or match_type == "content" else match_type
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

@app.get("/api/git/info")
async def get_git_info():
    """Get Git repository information"""
    try:
        repo_info = await git_integration.get_repository_info()
        return repo_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/git/status/{file_path:path}")
async def get_file_git_status(file_path: str):
    """Get Git status for a specific file"""
    try:
        safe_path = security_manager.validate_path(file_path)
        status = await git_integration.get_file_status(safe_path)
        return status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/git/history/{file_path:path}")
async def get_file_git_history(file_path: str, limit: int = 10):
    """Get Git commit history for a specific file"""
    try:
        safe_path = security_manager.validate_path(file_path)
        history = await git_integration.get_file_history(safe_path, limit)
        return {"history": history}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/git/diff/{file_path:path}")
async def get_file_git_diff(file_path: str, commit: Optional[str] = None):
    """Get Git diff for a specific file"""
    try:
        safe_path = security_manager.validate_path(file_path)
        diff = await git_integration.get_file_diff(safe_path, commit)
        return {"diff": diff}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/git/changes")
async def get_git_changes():
    """Get list of changed files in repository"""
    try:
        changes = await git_integration.get_changed_files()
        return {"changes": changes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Terminal WebSocket connection manager
class TerminalManager:
    def __init__(self):
        self.active_connections = {}
        self.processes = {}
    
    async def connect(self, websocket: WebSocket, terminal_id: str):
        await websocket.accept()
        self.active_connections[terminal_id] = websocket
        
        # Start a new shell process
        master, slave = pty.openpty()
        proc = subprocess.Popen(
            ['/bin/bash'],
            stdin=slave,
            stdout=slave,
            stderr=slave,
            preexec_fn=os.setsid,
            cwd=str(config.base_path)
        )
        
        os.close(slave)
        self.processes[terminal_id] = {'master': master, 'proc': proc}
        
        # Start reading from terminal
        asyncio.create_task(self.read_terminal(terminal_id))
    
    async def disconnect(self, terminal_id: str):
        if terminal_id in self.active_connections:
            del self.active_connections[terminal_id]
        
        if terminal_id in self.processes:
            proc_info = self.processes[terminal_id]
            try:
                os.close(proc_info['master'])
                proc_info['proc'].terminate()
                proc_info['proc'].wait(timeout=1)
            except:
                try:
                    proc_info['proc'].kill()
                except:
                    pass
            del self.processes[terminal_id]
    
    async def send_to_terminal(self, terminal_id: str, data: str):
        if terminal_id in self.processes:
            master = self.processes[terminal_id]['master']
            try:
                os.write(master, data.encode('utf-8'))
            except:
                await self.disconnect(terminal_id)
    
    async def read_terminal(self, terminal_id: str):
        if terminal_id not in self.processes:
            return
        
        master = self.processes[terminal_id]['master']
        websocket = self.active_connections.get(terminal_id)
        
        try:
            while terminal_id in self.processes and terminal_id in self.active_connections:
                # Check if there's data to read
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        data = os.read(master, 1024)
                        if data:
                            await websocket.send_text(data.decode('utf-8', errors='ignore'))
                        else:
                            break
                    except OSError:
                        break
                await asyncio.sleep(0.01)
        except:
            pass
        finally:
            await self.disconnect(terminal_id)

terminal_manager = TerminalManager()

@app.websocket("/ws/terminal/{terminal_id}")
async def websocket_terminal(websocket: WebSocket, terminal_id: str):
    """WebSocket endpoint for terminal communication"""
    await terminal_manager.connect(websocket, terminal_id)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Handle terminal resize
            if data.startswith('{"type":"resize"'):
                try:
                    msg = json.loads(data)
                    if terminal_id in terminal_manager.processes:
                        master = terminal_manager.processes[terminal_id]['master']
                        # Set terminal size
                        fcntl.ioctl(master, termios.TIOCSWINSZ, 
                                   struct.pack('HHHH', msg['rows'], msg['cols'], 0, 0))
                except:
                    pass
            else:
                # Regular input
                await terminal_manager.send_to_terminal(terminal_id, data)
    except WebSocketDisconnect:
        await terminal_manager.disconnect(terminal_id)
    except Exception as e:
        print(f"Terminal WebSocket error: {e}")
        await terminal_manager.disconnect(terminal_id)

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
        git_integration = GitIntegration(config.base_path)
    
    print(f"🚀 VeriDoc server starting on http://{args.host}:{args.port}")
    print(f"📁 Base path: {config.base_path}")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level="debug" if args.debug else "info"
    )