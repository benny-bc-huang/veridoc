/**
 * Terminal Component
 * Manages xterm.js terminal integration with WebSocket backend
 */

class TerminalComponent {
    constructor() {
        this.terminal = null;
        this.websocket = null;
        this.terminalId = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 3;
        this.reconnectDelay = 1000;
        
        this.initializeTerminal();
    }
    
    async initializeTerminal() {
        try {
            console.log('Terminal: Starting initialization...');
            
            // Check if xterm.js is loaded
            if (typeof Terminal === 'undefined') {
                console.error('Terminal: xterm.js not loaded');
                throw new Error('xterm.js library not available');
            }
            
            console.log('Terminal: xterm.js library available');
            
            // Create terminal instance
            this.terminal = new Terminal({
                cursorBlink: true,
                fontSize: 14,
                fontFamily: 'Consolas, "Liberation Mono", Menlo, Courier, monospace',
                theme: {
                    background: '#1e1e1e',
                    foreground: '#ffffff',
                    cursor: '#ffffff',
                    selection: '#ffffff40'
                },
                scrollback: 1000,
                tabStopWidth: 4
            });
            
            // Add fitness addon for resizing
            if (typeof FitAddon !== 'undefined') {
                this.fitAddon = new FitAddon.FitAddon();
                this.terminal.loadAddon(this.fitAddon);
            }
            
            // Generate terminal ID
            this.terminalId = 'terminal_' + Math.random().toString(36).substr(2, 9);
            
            // Terminal event handlers
            this.terminal.onData(data => {
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(data);
                }
            });
            
            this.terminal.onResize(size => {
                if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(JSON.stringify({
                        type: 'resize',
                        rows: size.rows,
                        cols: size.cols
                    }));
                }
            });
            
            console.log('Terminal initialized successfully');
            
        } catch (error) {
            console.error('Failed to initialize terminal:', error);
        }
    }
    
    mount(container) {
        console.log('Terminal: Starting mount process...', container);
        
        if (!this.terminal) {
            console.error('Terminal: Cannot mount - terminal not initialized');
            throw new Error('Terminal not initialized');
        }
        
        if (!container) {
            console.error('Terminal: Cannot mount - no container provided');
            throw new Error('No container provided for terminal mount');
        }
        
        try {
            console.log('Terminal: Opening terminal in container...');
            this.terminal.open(container);
            console.log('Terminal: Terminal opened successfully');
            
            // Fit terminal to container
            if (this.fitAddon) {
                console.log('Terminal: Fitting terminal to container...');
                this.fitAddon.fit();
                console.log('Terminal: Terminal fitted to container');
            } else {
                console.warn('Terminal: FitAddon not available');
            }
            
            // Connect to backend
            console.log('Terminal: Connecting to backend...');
            this.connect();
            
            // Handle container resize
            const resizeObserver = new ResizeObserver(() => {
                if (this.fitAddon) {
                    this.fitAddon.fit();
                }
            });
            resizeObserver.observe(container);
            
            console.log('Terminal: Mount completed successfully');
            
        } catch (error) {
            console.error('Terminal: Failed to mount terminal:', error);
            throw error;
        }
    }
    
    connect() {
        if (this.websocket && this.websocket.readyState === WebSocket.OPEN) {
            return;
        }
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/terminal/${this.terminalId}`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                this.isConnected = true;
                this.reconnectAttempts = 0;
                console.log('Terminal WebSocket connected');
                
                // Send a test message to see if backend is working
                if (this.terminal) {
                    this.terminal.write('\r\n🔥 Terminal connected! Type a command...\r\n');
                }
                
                // Send initial terminal size
                if (this.terminal && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(JSON.stringify({
                        type: 'resize',
                        rows: this.terminal.rows,
                        cols: this.terminal.cols
                    }));
                }
            };
            
            this.websocket.onmessage = (event) => {
                if (this.terminal) {
                    this.terminal.write(event.data);
                }
            };
            
            this.websocket.onclose = () => {
                this.isConnected = false;
                console.log('Terminal WebSocket disconnected');
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    setTimeout(() => {
                        this.reconnectAttempts++;
                        console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
                        this.connect();
                    }, this.reconnectDelay);
                } else {
                    if (this.terminal) {
                        this.terminal.write('\r\n\x1b[31mTerminal connection lost. Refresh page to reconnect.\x1b[0m\r\n');
                    }
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('Terminal WebSocket error:', error);
                if (this.terminal) {
                    this.terminal.write('\r\n\x1b[31mTerminal connection error.\x1b[0m\r\n');
                }
            };
            
        } catch (error) {
            console.error('Failed to connect terminal WebSocket:', error);
        }
    }
    
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
    }
    
    clear() {
        if (this.terminal) {
            this.terminal.clear();
        }
    }
    
    focus() {
        if (this.terminal) {
            this.terminal.focus();
        }
    }
    
    dispose() {
        this.disconnect();
        if (this.terminal) {
            this.terminal.dispose();
            this.terminal = null;
        }
    }
    
    // Helper method to check if terminal is ready
    isReady() {
        return this.terminal && this.isConnected;
    }
    
    // Send command to terminal
    sendCommand(command) {
        if (this.isReady()) {
            this.websocket.send(command + '\r');
        }
    }
    
    // Get terminal dimensions
    getDimensions() {
        if (this.terminal) {
            return {
                rows: this.terminal.rows,
                cols: this.terminal.cols
            };
        }
        return null;
    }
}

// Export for use in other modules
window.TerminalComponent = TerminalComponent;