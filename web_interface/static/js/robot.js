/**
 * Robot Visualization Module
 * 
 * Handles robot visualization, movement animation, state visualization,
 * direction indicators, and path visualization.
 */

class RobotVisualizer {
    constructor(warehouseVisualizer) {
        this.warehouse = warehouseVisualizer;
        this.ctx = warehouseVisualizer.ctx;
        this.canvas = warehouseVisualizer.canvas;
        
        // Robot configuration
        this.robotSize = 20; // 20x20 pixel robot icon
        this.robotRadius = this.robotSize / 2;
        
        // Robot state
        this.robot = {
            x: 0,
            y: 0,
            state: 'IDLE',
            direction: 0, // 0 = right, 90 = down, 180 = left, 270 = up
            targetX: 0,
            targetY: 0,
            isMoving: false,
            movementProgress: 0,
            currentOrder: null,
            path: []
        };
        
        // Robot colors by state
        this.robotColors = {
            IDLE: '#4CAF50',      // Green
            MOVING: '#2196F3',     // Blue
            PICKING: '#FF5722',    // Orange-Red for picking
            COLLECTING: '#FF9800',  // Orange
            RETURNING: '#9C27B0',   // Purple
            ERROR: '#F44336'        // Red
        };
        
        // Animation configuration
        this.animationSpeed = 0.05; // Movement speed (0-1)
        this.stateTransitionDuration = 200; // ms
        this.pathArrowSize = 8;
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('🤖 Initializing Robot Visualizer');
        console.log(`📏 Robot size: ${this.robotSize}x${this.robotSize}px`);
        console.log(`🎨 Robot colors: ${Object.keys(this.robotColors).join(', ')}`);
        
        // Set initial position (top-left corner)
        this.setRobotPosition(0, 0);
    }
    
    /**
     * Set robot position
     */
    setRobotPosition(x, y) {
        this.robot.x = x;
        this.robot.y = y;
        this.robot.targetX = x;
        this.robot.targetY = y;
        this.robot.isMoving = false;
        this.robot.movementProgress = 0;
        
        console.log(`🤖 Robot positioned at (${x}, ${y})`);
    }
    
    /**
     * Move robot to target position
     */
    moveRobotTo(targetX, targetY, path = []) {
        if (targetX === this.robot.x && targetY === this.robot.y) {
            return; // Already at target
        }
        
        this.robot.targetX = targetX;
        this.robot.targetY = targetY;
        this.robot.path = path;
        this.robot.isMoving = true;
        this.robot.movementProgress = 0;
        
        // Calculate direction
        const dx = targetX - this.robot.x;
        const dy = targetY - this.robot.y;
        this.robot.direction = Math.atan2(dy, dx) * 180 / Math.PI;
        
        // Set state to MOVING
        this.setRobotState('MOVING');
        
        console.log(`🤖 Robot moving from (${this.robot.x}, ${this.robot.y}) to (${targetX}, ${targetY})`);
    }
    
    /**
     * Set robot state
     */
    setRobotState(state) {
        if (this.robot.state !== state) {
            console.log(`🤖 Robot state changed: ${this.robot.state} → ${state}`);
            this.robot.state = state;
        }
    }
    
    /**
     * Assign order to robot
     */
    assignOrder(order) {
        this.robot.currentOrder = order;
        console.log(`📦 Robot assigned order: ${order.id}`);
    }
    
    /**
     * Clear robot order
     */
    clearOrder() {
        this.robot.currentOrder = null;
        console.log(`📦 Robot order cleared`);
    }
    
    /**
     * Update robot animation
     */
    update(data) {
        console.log('🤖 [RobotVisualizer] Received robot_data:', data);
        // Assume data is an array of robot objects or a single robot object
        let robotInfo = Array.isArray(data) ? data[0] : data;
        if (!robotInfo) return;
        
        // Update position - handle different position formats
        if (robotInfo.position) {
            if (Array.isArray(robotInfo.position)) {
                // Array format [x, y] - convert to grid coordinates
                const gridX = robotInfo.position[0];
                const gridY = robotInfo.position[1];
                this.setRobotPosition(gridX, gridY);
                // Disable frontend movement animation when receiving live data
                this.robot.isMoving = false;
            } else if (typeof robotInfo.position === 'string') {
                // String format like "A1" - convert to coordinates
                const coords = this.parseGridPosition(robotInfo.position);
                if (coords) {
                    this.setRobotPosition(coords.x, coords.y);
                    this.robot.isMoving = false;
                }
            } else if (robotInfo.position.aisle !== undefined && robotInfo.position.rack !== undefined) {
                // Coordinate object format
                this.setRobotPosition(robotInfo.position.aisle, robotInfo.position.rack);
                this.robot.isMoving = false;
            }
        } else if (robotInfo.x !== undefined && robotInfo.y !== undefined) {
            this.setRobotPosition(robotInfo.x, robotInfo.y);
            this.robot.isMoving = false;
        }
        
        // Update state
        if (robotInfo.state) {
            this.setRobotState(robotInfo.state);
        }
        
        // Update current order
        if (robotInfo.current_order) {
            this.assignOrder({ id: robotInfo.current_order });
        } else {
            this.clearOrder();
        }
        
        // Update items held and target items
        if (robotInfo.items_held) {
            this.robot.items_held = robotInfo.items_held;
        }
        
        if (robotInfo.target_items) {
            this.robot.target_items = robotInfo.target_items;
        }
        
        // Update battery level if provided
        if (robotInfo.battery_level !== undefined) {
            this.robot.batteryLevel = robotInfo.battery_level;
        }
        
        // Update path if provided
        if (robotInfo.path) {
            this.robot.path = robotInfo.path;
        }
        
        // Force a redraw
        this.render();
        
        // Update robot status display
        this.updateRobotStatusDisplay();
    }
    
    /**
     * Update robot status display in sidebar
     */
    updateRobotStatusDisplay() {
        const container = document.getElementById('robot-status-entity');
        if (!container) return;
        
        const robot = this.robot;
        const status = robot.state || 'IDLE';
        
        // Always convert status to string before using toLowerCase
        const statusStr = String(status).toLowerCase();
        
        // Convert grid coordinates to display format (A1, B2, etc.)
        const column = String.fromCharCode(65 + Math.floor(robot.x)); // A, B, C, etc.
        const row = Math.floor(robot.y) + 1; // 1-based row number
        const position = `${column}${row}`;
        
        const order = robot.currentOrder ? robot.currentOrder.id : 'None';
        const battery = robot.batteryLevel || 100;
        
        // Get items held and target items from robot data
        const itemsHeld = robot.items_held || [];
        const targetItems = robot.target_items || [];
        
        // Format items for display - show all items with proper line breaks
        const formatItemsForDisplay = (items) => {
            if (!items || items.length === 0) return 'None';
            
            if (items.length <= 3) {
                return items.join(', ');
            } else {
                // Show items in groups of 3 per line
                const lines = [];
                for (let i = 0; i < items.length; i += 3) {
                    lines.push(items.slice(i, i + 3).join(', '));
                }
                return lines.join('<br>');
            }
        };
        
        const itemsHeldText = formatItemsForDisplay(itemsHeld);
        const targetItemsText = formatItemsForDisplay(targetItems);
        
        container.innerHTML = `
            <div class="robot-status-card">
                <div class="robot-status-header">
                    <div class="robot-id"><b>ROBOT_001</b></div>
                    <div class="robot-status ${statusStr}">${status}</div>
                </div>
                <div class="robot-status-details">
                    <div class="robot-position">
                        <span class="detail-label">Position:</span>
                        <span class="detail-value">${position}</span>
                    </div>
                    <div class="robot-order">
                        <span class="detail-label">Current Order:</span>
                        <span class="detail-value">${order}</span>
                    </div>
                    <div class="robot-items-held">
                        <span class="detail-label">Items Held:</span>
                        <span class="detail-value">${itemsHeldText}</span>
                    </div>
                    <div class="robot-target-items">
                        <span class="detail-label">Target Items:</span>
                        <span class="detail-value">${targetItemsText}</span>
                    </div>
                    <div class="robot-battery">
                        <span class="detail-label">Battery:</span>
                        <span class="detail-value">${battery}%</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Parse grid position string (e.g., "A1") to coordinates
     * Updated to handle the warehouse coordinate system properly
     */
    parseGridPosition(positionStr) {
        if (!positionStr || typeof positionStr !== 'string') return null;
        
        const match = positionStr.match(/^([A-Z])(\d+)$/);
        if (!match) return null;
        
        const col = match[1].charCodeAt(0) - 65; // A=0, B=1, etc.
        const row = parseInt(match[2]) - 1; // 1-based to 0-based
        
        // Ensure coordinates are within warehouse bounds
        const x = Math.max(0, Math.min(col, 19)); // 0-19 for 20 columns
        const y = Math.max(0, Math.min(row, 24)); // 0-24 for 25 rows
        
        console.log(`🗺️ Parsed position "${positionStr}" to coordinates (${x}, ${y})`);
        return { x, y };
    }
    
    /**
     * Update robot movement
     */
    updateMovement(deltaTime) {
        if (!this.robot.isMoving) return;
        
        // Update movement progress
        this.robot.movementProgress += this.animationSpeed * deltaTime;
        
        if (this.robot.movementProgress >= 1) {
            // Movement complete
            this.robot.x = this.robot.targetX;
            this.robot.y = this.robot.targetY;
            this.robot.isMoving = false;
            this.robot.movementProgress = 1;
            
            console.log(`🤖 Robot reached target (${this.robot.x}, ${this.robot.y})`);
            
            // Check if we should change state based on current order
            if (this.robot.currentOrder) {
                this.handleOrderState();
            } else {
                this.setRobotState('IDLE');
            }
        } else {
            // Interpolate position
            this.robot.x = this.robot.x + (this.robot.targetX - this.robot.x) * this.animationSpeed;
            this.robot.y = this.robot.y + (this.robot.targetY - this.robot.y) * this.animationSpeed;
        }
    }
    
    /**
     * Handle robot state based on current order
     */
    handleOrderState() {
        if (!this.robot.currentOrder) return;
        
        const order = this.robot.currentOrder;
        
        // Check if robot is at inventory location
        const inventoryLocation = this.warehouse.getInventoryLocation(this.robot.x, this.robot.y);
        if (inventoryLocation) {
            this.setRobotState('COLLECTING');
        } else if (this.isAtPackoutZone()) {
            this.setRobotState('RETURNING');
        } else {
            this.setRobotState('MOVING');
        }
    }
    
    /**
     * Check if robot is at packout zone
     */
    isAtPackoutZone() {
        const packout = this.warehouse.layout.packoutZone;
        return (this.robot.x >= packout.x && this.robot.x < packout.x + packout.width &&
                this.robot.y >= packout.y && this.robot.y < packout.y + packout.height);
    }
    
    /**
     * Render robot
     */
    render() {
        if (!this.warehouse) return;
        
        // Get pixel coordinates
        const pixelCoords = this.warehouse.getPixelCoordinates(this.robot.x, this.robot.y);
        
        // Draw robot
        this.drawRobot(pixelCoords.x, pixelCoords.y);
        
        // Draw path if moving
        if (this.robot.isMoving && this.robot.path.length > 0) {
            this.drawPath();
        }
        
        // Draw direction indicator
        this.drawDirectionIndicator(pixelCoords.x, pixelCoords.y);
    }
    
    /**
     * Draw robot icon
     */
    drawRobot(x, y) {
        const color = this.robotColors[this.robot.state] || this.robotColors.IDLE;
        
        // Draw robot circle
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(x, y, this.robotRadius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Draw robot border
        this.ctx.strokeStyle = '#FFFFFF';
        this.ctx.lineWidth = 2;
        this.ctx.stroke();
        
        // Draw robot icon (gear symbol)
        this.drawRobotIcon(x, y);
        
        // Draw state indicator
        this.drawStateIndicator(x, y);
    }
    
    /**
     * Draw robot icon (gear symbol)
     */
    drawRobotIcon(x, y) {
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '12px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('🤖', x, y);
    }
    
    /**
     * Draw state indicator
     */
    drawStateIndicator(x, y) {
        const state = this.robot.state;
        const indicatorY = y - this.robotRadius - 15;
        
        this.ctx.fillStyle = '#212121';
        this.ctx.font = '10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(state, x, indicatorY);
    }
    
    /**
     * Draw direction indicator
     */
    drawDirectionIndicator(x, y) {
        const angle = this.robot.direction * Math.PI / 180;
        const arrowLength = this.robotRadius + 8;
        
        const arrowX = x + Math.cos(angle) * arrowLength;
        const arrowY = y + Math.sin(angle) * arrowLength;
        
        // Draw direction arrow
        this.ctx.strokeStyle = '#212121';
        this.ctx.lineWidth = 2;
        this.ctx.beginPath();
        this.ctx.moveTo(x, y);
        this.ctx.lineTo(arrowX, arrowY);
        this.ctx.stroke();
        
        // Draw arrowhead
        const arrowheadAngle = Math.PI / 6;
        const arrowheadLength = 6;
        
        this.ctx.beginPath();
        this.ctx.moveTo(arrowX, arrowY);
        this.ctx.lineTo(
            arrowX - arrowheadLength * Math.cos(angle - arrowheadAngle),
            arrowY - arrowheadLength * Math.sin(angle - arrowheadAngle)
        );
        this.ctx.moveTo(arrowX, arrowY);
        this.ctx.lineTo(
            arrowX - arrowheadLength * Math.cos(angle + arrowheadAngle),
            arrowY - arrowheadLength * Math.sin(angle + arrowheadAngle)
        );
        this.ctx.stroke();
    }
    
    /**
     * Draw robot path
     */
    drawPath() {
        if (this.robot.path.length < 2) return;
        
        this.ctx.strokeStyle = '#2196F3';
        this.ctx.lineWidth = 3;
        this.ctx.setLineDash([5, 5]);
        
        this.ctx.beginPath();
        this.robot.path.forEach((point, index) => {
            const pixelCoords = this.warehouse.getPixelCoordinates(point.x, point.y);
            
            if (index === 0) {
                this.ctx.moveTo(pixelCoords.x, pixelCoords.y);
            } else {
                this.ctx.lineTo(pixelCoords.x, pixelCoords.y);
            }
        });
        this.ctx.stroke();
        this.ctx.setLineDash([]);
        
        // Draw direction arrows on path
        this.drawPathArrows();
    }
    
    /**
     * Draw direction arrows on path
     */
    drawPathArrows() {
        if (this.robot.path.length < 2) return;
        
        this.ctx.fillStyle = '#2196F3';
        
        for (let i = 0; i < this.robot.path.length - 1; i++) {
            const current = this.robot.path[i];
            const next = this.robot.path[i + 1];
            
            const currentPixel = this.warehouse.getPixelCoordinates(current.x, current.y);
            const nextPixel = this.warehouse.getPixelCoordinates(next.x, next.y);
            
            // Calculate direction
            const dx = nextPixel.x - currentPixel.x;
            const dy = nextPixel.y - currentPixel.y;
            const angle = Math.atan2(dy, dx);
            
            // Draw arrow at midpoint
            const midX = (currentPixel.x + nextPixel.x) / 2;
            const midY = (currentPixel.y + nextPixel.y) / 2;
            
            this.drawArrow(midX, midY, angle);
        }
    }
    
    /**
     * Draw single arrow
     */
    drawArrow(x, y, angle) {
        const arrowSize = this.pathArrowSize;
        
        this.ctx.save();
        this.ctx.translate(x, y);
        this.ctx.rotate(angle);
        
        this.ctx.beginPath();
        this.ctx.moveTo(arrowSize, 0);
        this.ctx.lineTo(-arrowSize, arrowSize / 2);
        this.ctx.lineTo(-arrowSize, -arrowSize / 2);
        this.ctx.closePath();
        this.ctx.fill();
        
        this.ctx.restore();
    }
    
    /**
     * Get robot position
     */
    getRobotPosition() {
        return {
            x: this.robot.x,
            y: this.robot.y,
            state: this.robot.state,
            direction: this.robot.direction,
            isMoving: this.robot.isMoving,
            currentOrder: this.robot.currentOrder
        };
    }
    
    /**
     * Update robot from external data
     */
    updateFromData(data) {
        if (data.position) {
            this.setRobotPosition(data.position.x, data.position.y);
        }
        
        if (data.state) {
            this.setRobotState(data.state);
        }
        
        if (data.target) {
            this.moveRobotTo(data.target.x, data.target.y, data.path);
        }
        
        if (data.order) {
            this.assignOrder(data.order);
        }
    }
    
    /**
     * Simulate robot movement for testing
     */
    simulateMovement() {
        // DISABLED: Using real backend robot movement instead of simulation
        console.log('✅ Robot movement simulation disabled - using real backend data');
    }
}

// Remove or comment out mockRobotStatus and related rendering
// function renderRobotStatusPanel(robots) {
//   const container = document.getElementById('robot-status-entity');
//   if (!container) return;
  
//   if (!robots || robots.length === 0) {
//     container.innerHTML = '<div class="empty-panel">No active robots</div>';
//     return;
//   }
  
//   container.innerHTML = robots.map(robot => `
//     <div class="robot-card">
//       <div class="robot-header">
//         <div class="robot-id"><b>${robot.robot_id}</b></div>
//         <div class="robot-status-indicator status-${robot.status.toLowerCase().replace(/_/g, '-')}">
//           ${getStatusIcon(robot.status)} ${robot.status.replace(/_/g, ' ')}
//         </div>
//       </div>
//       <div class="robot-position">
//         <span class="position-label">Position:</span>
//         <span class="position-value">(${robot.position.x}, ${robot.position.y})</span>
//       </div>
//       <div class="robot-task">
//         <span class="task-label">Current Task:</span>
//         <span class="task-value">${robot.current_task}</span>
//       </div>
//       ${robot.current_order ? `
//         <div class="robot-order">
//           <span class="order-label">Current Order:</span>
//           <span class="order-value">${robot.current_order}</span>
//         </div>
//       ` : ''}
//     </div>
//   `).join('');
// }

// function getStatusIcon(status) {
//   const statusIcons = {
//     'IDLE': '⏸️',
//     'MOVING_TO_ITEM': '🔄',
//     'PICKING_UP': '📦',
//     'RETURNING_ORDER': '🏠',
//     'ERROR': '❌'
//   };
//   return statusIcons[status] || '❓';
// }

// On DOMContentLoaded, render the panel with mock data
// window.addEventListener('DOMContentLoaded', () => {
//   renderRobotStatusPanel(mockRobotStatus);
// });

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RobotVisualizer;
} 