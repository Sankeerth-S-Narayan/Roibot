/**
 * Main JavaScript for Roibot Warehouse Visualization
 * Handles application initialization, state management, and coordination
 */

//= require socket.io client
// <script src="/socket.io/socket.io.js"></script> should be included in index.html

class RoibotApp {
    constructor() {
        this.isInitialized = false;
        this.simulationState = 'paused';
        this.updateInterval = null;
        this.lastUpdateTime = 0;
        this.fps = 60;
        this.frameTime = 1000 / this.fps;
        
        // Initialize components
        this.warehouse = null;
        this.robot = null;
        this.orders = null;
        this.kpis = null;
        this.controls = null;
        
        // WebSocket connection
        this.socket = null; // Socket.IO client
        this.connected = false;
        
        // Performance tracking
        this.frameCount = 0;
        this.lastFpsUpdate = 0;
        this.currentFps = 0;
    }

    /**
     * Initialize the application
     */
    async init() {
        try {
            console.log('🚀 Initializing Roibot Warehouse Visualization...');
            
            // Initialize components
            await this.initializeComponents();
            
            // Set up event listeners
            this.setupEventListeners();
            
            // Initialize WebSocket connection
            await this.initializeWebSocket();
            
            // Start the render loop
            this.startRenderLoop();
            
            // Start simulation time updates
            this.startSimulationTimeUpdates();
            
            this.isInitialized = true;
            console.log('✅ Roibot app initialized successfully');
            
            // Update UI to show ready state
            this.updateSimulationStatus('Ready');
            
        } catch (error) {
            console.error('❌ Failed to initialize Roibot app:', error);
            this.showError('Failed to initialize application');
        }
    }

    /**
     * Initialize all application components
     */
    async initializeComponents() {
        // Initialize warehouse visualization
        this.warehouse = new WarehouseVisualizer('warehouse-canvas');
        this.warehouse.initEventListeners();
        
        // Initialize robot visualization
        this.robot = new RobotVisualizer(this.warehouse);
        
        // Initialize order visualization
        this.orders = new OrderVisualizer(this.warehouse);
        
        // Initialize KPI dashboard
        this.kpis = new KPIDashboard(this.warehouse, this.robot, this.orders);
        
        // Initialize simulation controls
        this.controls = new SimulationControls();
        
        // Setup control event listeners
        this.setupControlEventListeners();
        
        console.log('✅ All components initialized');
    }

    /**
     * Set up event listeners for the application
     */
    setupEventListeners() {
        // Window events
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('beforeunload', () => this.cleanup());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyPress(e));
        
        // Error handling
        window.addEventListener('error', (e) => this.handleError(e));
        
        // Setup control buttons
        this.setupControlButtons();
        
        console.log('✅ Event listeners set up');
    }
    
    /**
     * Setup control button event listeners
     */
    setupControlButtons() {
        // Play button
        const playBtn = document.getElementById('play-btn');
        if (playBtn) {
            playBtn.addEventListener('click', () => {
                console.log('▶️ Play button clicked');
                this.playSimulation();
            });
        }
        
        // Pause button
        const pauseBtn = document.getElementById('pause-btn');
        if (pauseBtn) {
            pauseBtn.addEventListener('click', () => {
                console.log('⏸️ Pause button clicked');
                this.pauseSimulation();
            });
        }
        
        // Reset button
        const resetBtn = document.getElementById('reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                console.log('🔄 Reset button clicked');
                this.resetSimulation();
            });
        }
    }

    /**
     * Setup event listeners for simulation controls
     */
    setupControlEventListeners() {
        // Listen for simulation toggle events
        document.addEventListener('simulationToggle', (event) => {
            const { isRunning } = event.detail;
            console.log(`Simulation ${isRunning ? 'resumed' : 'paused'}`);
            
            if (isRunning) {
                this.playSimulation();
            } else {
                this.pauseSimulation();
            }
        });
        
        // Listen for simulation reset events
        document.addEventListener('simulationReset', () => {
            console.log('Simulation reset requested');
            this.resetSimulation();
        });
        
        // Listen for simulation step events
        document.addEventListener('simulationStep', () => {
            console.log('Simulation step requested');
            this.stepSimulation();
        });
        
        // Listen for speed change events
        document.addEventListener('simulationSpeedChange', (event) => {
            const { speed } = event.detail;
            console.log(`Simulation speed changed to ${speed}x`);
            this.updateSimulationSpeed(speed);
        });
    }

    /**
     * Step simulation (single step)
     */
    stepSimulation() {
        console.log('Executing simulation step');
        this.sendCommand('step');
    }

    /**
     * Update simulation speed
     */
    updateSimulationSpeed(speed) {
        console.log(`Updating simulation speed to ${speed}x`);
        this.sendCommand('speed', { speed: speed });
    }

    /**
     * Initialize WebSocket connection for real-time updates
     */
    async initializeWebSocket() {
        try {
            // Check if Socket.IO is available
            if (typeof io === 'undefined') {
                console.error('❌ Socket.IO client not loaded');
                this.connected = false;
                this.updateConnectionStatus(false);
                return;
            }
            
            this.initializeSocketIO();
            
        } catch (error) {
            console.error('❌ Failed to initialize Socket.IO:', error);
            this.connected = false;
            this.updateConnectionStatus(false);
        }
    }
    
    initializeSocketIO() {
        try {
            // Use Socket.IO client
            this.socket = io(); // Connects to the same host/port

            this.socket.on('connect', () => {
                console.log('✅ Socket.IO connected');
                this.connected = true;
                this.updateConnectionStatus(true);
            });

            this.socket.on('disconnect', () => {
                console.log('⚠️ Socket.IO disconnected');
                this.connected = false;
                this.updateConnectionStatus(false);
            });

            // Listen for backend events and update UI
            this.socket.on('robot_data', (data) => {
                console.log('[SocketIO] robot_data received:', data);
                if (this.robot) this.robot.update(data);
            });
            this.socket.on('order_data', (data) => {
                console.log('[SocketIO] order_data received:', data);
                if (this.orders) this.orders.update(data);
            });
            this.socket.on('kpi_data', (data) => {
                console.log('[SocketIO] kpi_data received:', data);
                if (this.kpis) this.kpis.update(data);
            });
            this.socket.on('simulation_state', (data) => {
                this.updateSimulationState(data);
            });
            this.socket.on('warehouse_data', (data) => {
                // Warehouse layout is static, no need for real-time updates
                // this.warehouse.update(data); // Removed - warehouse doesn't have update method
            });
            
            // Handle command responses for immediate feedback
            this.socket.on('command_response', (response) => {
                console.log('🎮 [Main] Command response received:', response);
                if (response.success && response.result) {
                    const status = response.result.status;
                    console.log('🎮 [Main] Command result status:', status);
                    
                    // Provide immediate UI feedback
                    switch (status) {
                        case 'running':
                            this.simulationState = 'running';
                            this.updateSimulationStatus('Running');
                            break;
                        case 'paused':
                            this.simulationState = 'paused';
                            this.updateSimulationStatus('Paused');
                            break;
                        case 'reset':
                            this.simulationState = 'paused';
                            this.updateSimulationStatus('Ready');
                            break;
                    }
                }
            });

            // Optionally: handle errors
            this.socket.on('connect_error', (err) => {
                console.error('❌ Socket.IO connection error:', err);
                this.handleError(err);
            });
        } catch (error) {
            console.error('❌ Failed to initialize Socket.IO connection:', error);
            this.connected = false;
            this.updateConnectionStatus(false);
        }
    }

    /**
     * Start the main render loop
     */
    startRenderLoop() {
        const render = (timestamp) => {
            // Calculate FPS
            this.frameCount++;
            if (timestamp - this.lastFpsUpdate >= 1000) {
                this.currentFps = this.frameCount;
                this.frameCount = 0;
                this.lastFpsUpdate = timestamp;
            }
            
            // Render components
            this.render(timestamp);
            
            // Schedule next frame
            requestAnimationFrame(render);
        };
        
        requestAnimationFrame(render);
        console.log('✅ Render loop started');
    }
    
    /**
     * Start simulation time updates
     */
    startSimulationTimeUpdates() {
        // DISABLED: Using backend simulation time instead of local time
        // The backend will send simulation_time updates via Socket.IO
        console.log('✅ Simulation time updates disabled - using backend time');
    }

    /**
     * Main render function
     */
    render(timestamp) {
        // Update warehouse
        if (this.warehouse) {
            this.warehouse.render(timestamp);
        }
        
        // Update robot
        if (this.robot) {
            this.robot.render(timestamp);
        }
        
        // Update orders
        if (this.orders) {
            this.orders.render(timestamp);
        }
        
        // Update KPIs
        if (this.kpis) {
            this.kpis.render(timestamp);
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (this.warehouse) {
            this.warehouse.handleResize();
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyPress(event) {
        switch (event.key) {
            case ' ':
                event.preventDefault();
                this.toggleSimulation();
                break;
            case 'r':
            case 'R':
                if (event.ctrlKey) {
                    event.preventDefault();
                    this.resetSimulation();
                }
                break;
            case 'p':
            case 'P':
                event.preventDefault();
                this.pauseSimulation();
                break;
        }
    }

    /**
     * Toggle simulation play/pause
     */
    toggleSimulation() {
        if (this.simulationState === 'running') {
            this.pauseSimulation();
        } else {
            this.playSimulation();
        }
    }

    /**
     * Play simulation
     */
    playSimulation() {
        this.simulationState = 'running';
        this.updateSimulationStatus('Running');
        this.sendCommand('play');
    }

    /**
     * Pause simulation
     */
    pauseSimulation() {
        this.simulationState = 'paused';
        this.updateSimulationStatus('Paused');
        this.sendCommand('pause');
    }

    /**
     * Reset simulation
     */
    resetSimulation() {
        this.simulationState = 'paused';
        this.updateSimulationStatus('Resetting...');
        this.sendCommand('reset');
        
        // Reset components
        if (this.warehouse) this.warehouse.reset();
        if (this.robot) this.robot.reset();
        if (this.orders) this.orders.reset();
        if (this.kpis) this.kpis.reset();
    }

    /**
     * Send command to server
     */
    sendCommand(command, payload = {}) {
        if (this.socket && this.connected) {
            this.socket.emit('command', {
                command: command,
                payload: payload,
                timestamp: Date.now()
            });
        } else {
            // Fallback to HTTP
            fetch('/api/command', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ command: command, payload: payload })
            }).catch(error => {
                console.error('❌ Failed to send command:', error);
            });
        }
    }

    /**
     * Update simulation status display
     */
    updateSimulationStatus(status) {
        const statusElement = document.getElementById('simulation-status');
        if (statusElement) {
            statusElement.textContent = status;
        }
    }
    
    /**
     * Update simulation time display
     */
    updateSimulationTime(seconds) {
        const timeElement = document.getElementById('simulation-time');
        if (timeElement) {
            timeElement.textContent = this.formatTime(seconds);
        }
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('simulation-status');
        if (statusElement) {
            if (connected) {
                statusElement.classList.remove('disconnected');
                statusElement.classList.add('connected');
            } else {
                statusElement.classList.remove('connected');
                statusElement.classList.add('disconnected');
            }
        }
    }

    /**
     * Update simulation state
     */
    updateSimulationState(state) {
        console.log('🔄 [Main] Simulation state update:', state);
        
        // Update simulation state based on backend status
        if (state.status) {
            switch (state.status) {
                case 'running':
                    this.simulationState = 'running';
                    this.updateSimulationStatus('Running');
                    break;
                case 'paused':
                    this.simulationState = 'paused';
                    this.updateSimulationStatus('Paused');
                    break;
                case 'reset':
                    this.simulationState = 'paused';
                    this.updateSimulationStatus('Ready');
                    break;
                case 'error':
                    this.simulationState = 'error';
                    this.updateSimulationStatus('Error');
                    break;
                default:
                    // Handle legacy format
                    if (state.paused !== undefined) {
                        this.simulationState = state.paused ? 'paused' : 'running';
                        this.updateSimulationStatus(state.paused ? 'Paused' : 'Running');
                    }
            }
        } else if (state.paused !== undefined) {
            this.simulationState = state.paused ? 'paused' : 'running';
            this.updateSimulationStatus(state.paused ? 'Paused' : 'Running');
        }
        
        if (state.speed !== undefined) {
            this.updateSimulationSpeed(state.speed);
        }
        
        if (state.time !== undefined) {
            this.updateSimulationTime(state.time);
        }
        
        // Update simulation time from any time-related field
        if (state.simulation_time !== undefined) {
            this.updateSimulationTime(state.simulation_time);
        }
        
        // Update order counts with debug logging
        console.log('🔍 [Main] Checking total_orders in state:', state.total_orders);
        if (state.total_orders !== undefined) {
            const totalElement = document.getElementById('total-orders');
            console.log('🔍 [Main] Total orders element:', totalElement);
            if (totalElement) {
                totalElement.textContent = state.total_orders;
                console.log('🔍 [Main] Updated total orders to:', state.total_orders);
            }
        }
        
        if (state.completed_orders !== undefined) {
            const completedElement = document.getElementById('completed-orders');
            if (completedElement) completedElement.textContent = state.completed_orders;
        }
    }

    /**
     * Format time in HH:MM:SS
     */
    formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Handle errors
     */
    handleError(error) {
        console.error('❌ Application error:', error);
        this.showError('An error occurred. Please check the console for details.');
    }

    /**
     * Show error message to user
     */
    showError(message) {
        // Create error alert
        const alert = document.createElement('div');
        alert.className = 'alert alert-error';
        alert.textContent = message;
        
        // Add to page
        document.body.appendChild(alert);
        
        // Remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 5000);
    }

    /**
     * Cleanup resources
     */
    cleanup() {
        // Stop render loop
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        // Close Socket.IO
        if (this.socket) {
            this.socket.disconnect();
        }
        
        // Stop polling
        if (this.pollInterval) {
            clearInterval(this.pollInterval);
        }
        
        console.log('🧹 Cleanup completed');
    }
}

// Global app instance
let roibotApp;

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    roibotApp = new RoibotApp();
    await roibotApp.init();
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    if (roibotApp) {
        roibotApp.cleanup();
    }
}); 