/**
 * Interactive Controls & User Interface
 * Provides simulation controls, status indicators, and user interface elements
 */

class SimulationControls {
    constructor() {
        this.isRunning = true;
        this.simulationSpeed = 1.0;
        this.errorStatus = null;
        this.robotStates = new Map();
        this.orderQueueStatus = {
            pending: 0,
            inProgress: 0,
            completed: 0,
            total: 0
        };
        
        this.initializeControls();
        this.setupEventListeners();
        this.startStatusUpdates();
    }

    /**
     * Initialize control elements
     */
    initializeControls() {
        // Create control panel
        const controlPanel = document.createElement('div');
        controlPanel.id = 'control-panel';
        controlPanel.className = 'control-panel';
        
        controlPanel.innerHTML = `
            <div class="control-section">
                <h3>Simulation Controls</h3>
                <div class="control-buttons">
                    <button id="pause-resume-btn" class="control-btn primary">
                        <span class="btn-icon">⏸️</span>
                        <span class="btn-text">Pause</span>
                    </button>
                    <button id="reset-btn" class="control-btn secondary">
                        <span class="btn-icon">🔄</span>
                        <span class="btn-text">Reset</span>
                    </button>
                    <button id="step-btn" class="control-btn secondary">
                        <span class="btn-icon">⏭️</span>
                        <span class="btn-text">Step</span>
                    </button>
                </div>
            </div>
            
            <div class="control-section">
                <h3>Simulation Status</h3>
                <div class="status-indicators">
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span id="simulation-status" class="status-value running">Running</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Speed:</span>
                        <span id="simulation-speed" class="status-value">1.0x</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Runtime:</span>
                        <span id="simulation-runtime" class="status-value">00:00:00</span>
                    </div>
                </div>
            </div>
            
            <div class="control-section">
                <h3>Robot Status</h3>
                <div id="robot-status-panel" class="robot-status-panel">
                    <div class="robot-status-item">
                        <span class="robot-id">Robot 1</span>
                        <span class="robot-state idle">IDLE</span>
                        <span class="robot-position">A1</span>
                    </div>
                </div>
            </div>
            
            <div class="control-section">
                <h3>Order Queue</h3>
                <div id="order-queue-status" class="order-queue-status">
                    <div class="queue-item">
                        <span class="queue-label">Pending:</span>
                        <span id="pending-orders" class="queue-value">0</span>
                    </div>
                    <div class="queue-item">
                        <span class="queue-label">In Progress:</span>
                        <span id="in-progress-orders" class="queue-value">0</span>
                    </div>
                    <div class="queue-item">
                        <span class="queue-label">Completed:</span>
                        <span id="completed-orders" class="queue-value">0</span>
                    </div>
                    <div class="queue-item">
                        <span class="queue-label">Total:</span>
                        <span id="total-orders" class="queue-value">0</span>
                    </div>
                </div>
            </div>
            
            <div class="control-section">
                <h3>Error Status</h3>
                <div id="error-status" class="error-status hidden">
                    <span class="error-icon">⚠️</span>
                    <span class="error-message">No errors</span>
                </div>
            </div>
        `;
        
        // Add to main container
        const mainContainer = document.getElementById('warehouse-container');
        if (mainContainer) {
            mainContainer.appendChild(controlPanel);
        }
    }

    /**
     * Setup event listeners for controls
     */
    setupEventListeners() {
        // Pause/Resume button
        const pauseResumeBtn = document.getElementById('pause-resume-btn');
        if (pauseResumeBtn) {
            pauseResumeBtn.addEventListener('click', () => this.toggleSimulation());
        }

        // Reset button
        const resetBtn = document.getElementById('reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetSimulation());
        }

        // Step button
        const stepBtn = document.getElementById('step-btn');
        if (stepBtn) {
            stepBtn.addEventListener('click', () => this.stepSimulation());
        }

        // Speed control
        this.setupSpeedControl();
    }

    /**
     * Setup simulation speed control
     */
    setupSpeedControl() {
        const speedContainer = document.createElement('div');
        speedContainer.className = 'speed-control';
        speedContainer.innerHTML = `
            <label for="speed-slider">Speed:</label>
            <input type="range" id="speed-slider" min="0.1" max="5.0" step="0.1" value="1.0">
            <span id="speed-value">1.0x</span>
        `;

        // Insert after simulation status
        const statusSection = document.querySelector('.control-section:nth-child(2)');
        if (statusSection) {
            statusSection.appendChild(speedContainer);
        }

        // Speed slider event listener
        const speedSlider = document.getElementById('speed-slider');
        const speedValue = document.getElementById('speed-value');
        
        if (speedSlider && speedValue) {
            speedSlider.addEventListener('input', (e) => {
                this.simulationSpeed = parseFloat(e.target.value);
                speedValue.textContent = `${this.simulationSpeed.toFixed(1)}x`;
                this.updateSimulationSpeed();
            });
        }
    }

    /**
     * Toggle simulation pause/resume
     */
    toggleSimulation() {
        this.isRunning = !this.isRunning;
        this.updateSimulationStatus();
        
        // Emit event for other components
        const event = new CustomEvent('simulationToggle', {
            detail: { isRunning: this.isRunning }
        });
        document.dispatchEvent(event);
    }

    /**
     * Reset simulation
     */
    resetSimulation() {
        // Emit reset event
        const event = new CustomEvent('simulationReset');
        document.dispatchEvent(event);
        
        // Reset local state
        this.isRunning = true;
        this.simulationSpeed = 1.0;
        this.errorStatus = null;
        this.updateSimulationStatus();
        this.updateErrorStatus();
    }

    /**
     * Step simulation (single step)
     */
    stepSimulation() {
        // Emit step event
        const event = new CustomEvent('simulationStep');
        document.dispatchEvent(event);
    }

    /**
     * Update simulation speed
     */
    updateSimulationSpeed() {
        // Emit speed change event
        const event = new CustomEvent('simulationSpeedChange', {
            detail: { speed: this.simulationSpeed }
        });
        document.dispatchEvent(event);
    }

    /**
     * Update simulation status display
     */
    updateSimulationStatus() {
        const statusElement = document.getElementById('simulation-status');
        const pauseResumeBtn = document.getElementById('pause-resume-btn');
        const btnText = pauseResumeBtn?.querySelector('.btn-text');
        const btnIcon = pauseResumeBtn?.querySelector('.btn-icon');

        if (statusElement) {
            if (this.isRunning) {
                statusElement.textContent = 'Running';
                statusElement.className = 'status-value running';
            } else {
                statusElement.textContent = 'Paused';
                statusElement.className = 'status-value paused';
            }
        }

        if (pauseResumeBtn && btnText && btnIcon) {
            if (this.isRunning) {
                btnText.textContent = 'Pause';
                btnIcon.textContent = '⏸️';
                pauseResumeBtn.className = 'control-btn primary';
            } else {
                btnText.textContent = 'Resume';
                btnIcon.textContent = '▶️';
                pauseResumeBtn.className = 'control-btn primary';
            }
        }
    }

    /**
     * Update robot status panel
     */
    updateRobotStatus(robotData) {
        const robotPanel = document.getElementById('robot-status-panel');
        if (!robotPanel) return;

        // Update or create robot status items
        robotData.forEach((robot, robotId) => {
            let robotItem = robotPanel.querySelector(`[data-robot-id="${robotId}"]`);
            
            if (!robotItem) {
                robotItem = document.createElement('div');
                robotItem.className = 'robot-status-item';
                robotItem.setAttribute('data-robot-id', robotId);
                robotPanel.appendChild(robotItem);
            }

            const stateClass = robot.state.toLowerCase();
            robotItem.innerHTML = `
                <span class="robot-id">Robot ${robotId}</span>
                <span class="robot-state ${stateClass}">${robot.state}</span>
                <span class="robot-position">${robot.position}</span>
            `;
        });
    }

    /**
     * Update order queue status
     */
    updateOrderQueueStatus(queueData) {
        this.orderQueueStatus = { ...queueData };
        
        const elements = {
            pending: document.getElementById('pending-orders'),
            inProgress: document.getElementById('in-progress-orders'),
            completed: document.getElementById('completed-orders'),
            total: document.getElementById('total-orders')
        };

        Object.entries(elements).forEach(([key, element]) => {
            if (element) {
                element.textContent = this.orderQueueStatus[key] || 0;
            }
        });
    }

    /**
     * Update error status
     */
    updateErrorStatus(error = null) {
        this.errorStatus = error;
        const errorElement = document.getElementById('error-status');
        
        if (errorElement) {
            if (error) {
                errorElement.classList.remove('hidden');
                errorElement.querySelector('.error-message').textContent = error;
                errorElement.className = 'error-status error';
            } else {
                errorElement.classList.add('hidden');
                errorElement.querySelector('.error-message').textContent = 'No errors';
                errorElement.className = 'error-status';
            }
        }
    }

    /**
     * Start status update timer
     */
    startStatusUpdates() {
        // DISABLED: Using backend simulation time instead of local time
        // The backend will send simulation time updates via Socket.IO
        console.log('✅ Status updates disabled - using backend time');
    }

    /**
     * Get current simulation state
     */
    getSimulationState() {
        return {
            isRunning: this.isRunning,
            speed: this.simulationSpeed,
            error: this.errorStatus,
            robotStates: this.robotStates,
            orderQueue: this.orderQueueStatus
        };
    }

    /**
     * Set simulation state from external source
     */
    setSimulationState(state) {
        if (state.isRunning !== undefined) {
            this.isRunning = state.isRunning;
            this.updateSimulationStatus();
        }
        
        if (state.speed !== undefined) {
            this.simulationSpeed = state.speed;
            const speedSlider = document.getElementById('speed-slider');
            const speedValue = document.getElementById('speed-value');
            
            if (speedSlider) speedSlider.value = this.simulationSpeed;
            if (speedValue) speedValue.textContent = `${this.simulationSpeed.toFixed(1)}x`;
        }
        
        if (state.error !== undefined) {
            this.updateErrorStatus(state.error);
        }
        
        if (state.robotStates) {
            this.updateRobotStatus(state.robotStates);
        }
        
        if (state.orderQueue) {
            this.updateOrderQueueStatus(state.orderQueue);
        }
    }
}

// Export for use in main.js
window.SimulationControls = SimulationControls; 