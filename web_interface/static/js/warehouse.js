/**
 * Warehouse Visualization Module
 * 
 * Handles the 25x20 warehouse grid rendering, layout visualization,
 * snake pattern paths, and inventory location markers.
 */

class WarehouseVisualizer {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        
        // Grid configuration
        this.gridWidth = 20; // Racks (X axis, horizontal)
        this.gridHeight = 25; // Aisles (Y axis, vertical)
        this.cellSize = 28; // Slightly larger for clarity
        
        // Padding for external labels
        this.labelPadding = {
            top: 25,    // Space for column letters
            left: 35,   // Space for row numbers
            right: 10,  // Small right margin
            bottom: 25  // Space for legend/info
        };
        
        // Canvas setup with padding for labels
        this.canvasWidth = this.gridWidth * this.cellSize + this.labelPadding.left + this.labelPadding.right;
        this.canvasHeight = this.gridHeight * this.cellSize + this.labelPadding.top + this.labelPadding.bottom;
        this.canvas.width = this.canvasWidth;
        this.canvas.height = this.canvasHeight;
        
        // Warehouse grid offset (to account for label space)
        this.gridOffsetX = this.labelPadding.left;
        this.gridOffsetY = this.labelPadding.top;
        
        // Color scheme (light theme)
        this.colors = {
            background: '#FFFFFF',
            gridLines: '#E0E0E0',
            aisles: '#F5F5F5',
            racks: '#D3D3D3',
            packoutZone: '#E8F5E8',
            inventory: '#FFE0B2',
            path: '#2196F3',
            boundary: '#9E9E9E'
        };
        
        // Warehouse layout configuration
        this.layout = {
            aisles: [
                { x: 5, y: 0, width: 1, height: 20 },
                { x: 15, y: 0, width: 1, height: 20 }
            ],
            racks: [
                { x: 0, y: 0, width: 5, height: 20 },
                { x: 6, y: 0, width: 9, height: 20 },
                { x: 16, y: 0, width: 9, height: 20 }
            ],
            packoutZone: { x: 20, y: 15, width: 5, height: 5 },
            inventoryLocations: [
                { x: 1, y: 2, type: 'A' },
                { x: 2, y: 5, type: 'B' },
                { x: 3, y: 8, type: 'C' },
                { x: 4, y: 12, type: 'D' },
                { x: 7, y: 3, type: 'E' },
                { x: 8, y: 7, type: 'F' },
                { x: 9, y: 11, type: 'G' },
                { x: 10, y: 15, type: 'H' },
                { x: 11, y: 2, type: 'I' },
                { x: 12, y: 6, type: 'J' },
                { x: 13, y: 10, type: 'K' },
                { x: 14, y: 14, type: 'L' },
                { x: 17, y: 4, type: 'M' },
                { x: 18, y: 8, type: 'N' },
                { x: 19, y: 12, type: 'O' },
                { x: 21, y: 16, type: 'P' },
                { x: 22, y: 17, type: 'Q' },
                { x: 23, y: 18, type: 'R' }
            ]
        };
        
        // Snake pattern path for robot navigation
        this.snakePath = this.generateSnakePath();
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('🏭 Initializing Warehouse Visualizer');
        console.log(`📐 Grid size: ${this.gridWidth}x${this.gridHeight}`);
        console.log(`📏 Cell size: ${this.cellSize}px`);
        console.log(`🎨 Canvas size: ${this.canvas.width}x${this.canvas.height}`);
        
        this.draw();
    }
    
    /**
     * Generate snake pattern path for efficient robot navigation
     */
    generateSnakePath() {
        const path = [];
        
        // Start from top-left, snake through the warehouse
        for (let y = 0; y < this.gridHeight; y++) {
            if (y % 2 === 0) {
                // Left to right
                for (let x = 0; x < this.gridWidth; x++) {
                    path.push({ x, y });
                }
            } else {
                // Right to left
                for (let x = this.gridWidth - 1; x >= 0; x--) {
                    path.push({ x, y });
                }
            }
        }
        
        console.log(`🐍 Generated snake path with ${path.length} points`);
        return path;
    }
    
    /**
     * Draw the complete warehouse visualization
     */
    draw() {
        this.clear();
        this.drawBackground();
        this.drawGrid();
        this.drawLayout();
        // Remove this line to eliminate yellow dots
        // this.drawInventoryLocations();
        this.drawSnakePath();
        this.drawBoundaries();
        this.drawCoordinates();
    }
    
    /**
     * Clear the canvas
     */
    clear() {
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    /**
     * Draw background
     */
    drawBackground() {
        this.ctx.fillStyle = this.colors.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }
    
    /**
     * Draw grid lines
     */
    drawGrid() {
        this.ctx.strokeStyle = this.colors.gridLines;
        this.ctx.lineWidth = 1;
        
        // Vertical lines
        for (let x = 0; x <= this.gridWidth; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.cellSize + this.gridOffsetX, this.gridOffsetY);
            this.ctx.lineTo(x * this.cellSize + this.gridOffsetX, this.gridOffsetY + this.gridHeight * this.cellSize);
            this.ctx.stroke();
        }
        
        // Horizontal lines
        for (let y = 0; y <= this.gridHeight; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(this.gridOffsetX, y * this.cellSize + this.gridOffsetY);
            this.ctx.lineTo(this.gridOffsetX + this.gridWidth * this.cellSize, y * this.cellSize + this.gridOffsetY);
            this.ctx.stroke();
        }
    }
    
    /**
     * Draw warehouse layout (aisles, racks, packout zone)
     */
    drawLayout() {
        // Remove all fillRect calls for aisles, racks, and packoutZone
        // Only draw boundaries or overlays if needed
        // this.drawBoundaries(); // If you want to keep boundaries
        this.drawLabels();
    }
    
    /**
     * Draw warehouse labels
     */
    drawLabels() {
        // Draw Y axis (vertical) numbers 1-25 - moved outside the warehouse boundary
        this.ctx.save();
        this.ctx.font = 'bold 14px Segoe UI, Arial';
        this.ctx.fillStyle = '#333333';
        this.ctx.textAlign = 'right';
        this.ctx.textBaseline = 'middle';
        for (let y = 0; y < this.gridHeight; y++) {
            const py = y * this.cellSize + this.cellSize / 2 + this.gridOffsetY;
            this.ctx.fillText(`${y + 1}`, this.gridOffsetX - 10, py); // Moved further left
        }
        
        // Draw X axis (horizontal) letters A-T - moved outside the warehouse boundary
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'bottom';
        for (let x = 0; x < this.gridWidth; x++) {
            const px = x * this.cellSize + this.cellSize / 2 + this.gridOffsetX;
            const label = String.fromCharCode(65 + x); // A, B, C, etc.
            this.ctx.fillText(label, px, this.gridOffsetY - 5); // Position above the warehouse grid
        }
        this.ctx.restore();
    }
    
    /**
     * Draw inventory locations
     */
    drawInventoryLocations() {
        this.ctx.fillStyle = this.colors.inventory;
        
        this.layout.inventoryLocations.forEach(location => {
            const x = location.x * this.cellSize + this.cellSize / 2 + this.gridOffsetX;
            const y = location.y * this.cellSize + this.cellSize / 2 + this.gridOffsetY;
            const radius = this.cellSize / 4;
            
            // Draw inventory marker
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, 2 * Math.PI);
            this.ctx.fill();
            
            // Draw location type
            this.ctx.fillStyle = '#212121';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(location.type, x, y);
            this.ctx.fillStyle = this.colors.inventory;
        });
    }
    
    /**
     * Draw snake pattern path
     */
    drawSnakePath() {
        this.ctx.strokeStyle = this.colors.path;
        this.ctx.lineWidth = 2;
        this.ctx.setLineDash([5, 5]);
        
        this.ctx.beginPath();
        this.snakePath.forEach((point, index) => {
            const x = point.x * this.cellSize + this.cellSize / 2 + this.gridOffsetX;
            const y = point.y * this.cellSize + this.cellSize / 2 + this.gridOffsetY;
            
            if (index === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        });
        this.ctx.stroke();
        this.ctx.setLineDash([]);
    }
    
    /**
     * Draw warehouse boundaries
     */
    drawBoundaries() {
        this.ctx.strokeStyle = this.colors.boundary;
        this.ctx.lineWidth = 3;
        
        this.ctx.strokeRect(this.gridOffsetX, this.gridOffsetY, this.gridWidth * this.cellSize, this.gridHeight * this.cellSize);
    }
    
    /**
     * Draw coordinate system - Updated to avoid overlap with boundaries
     */
    drawCoordinates() {
        // Coordinates are now handled in drawLabels() method
        // This method can be used for additional coordinate features if needed
        
        // Optional: Add coordinate display in corner
        this.ctx.fillStyle = '#888888';
        this.ctx.font = '10px Arial';
        this.ctx.textAlign = 'left';
        this.ctx.textBaseline = 'top';
        this.ctx.fillText('Warehouse Grid (A-T, 1-25)', this.gridOffsetX - 10, this.canvasHeight - this.labelPadding.bottom + 5);
    }
    
    /**
     * Get grid coordinates from pixel coordinates
     */
    getGridCoordinates(pixelX, pixelY) {
        const gridX = Math.floor((pixelX - this.gridOffsetX) / this.cellSize);
        const gridY = Math.floor((pixelY - this.gridOffsetY) / this.cellSize);
        
        return {
            x: Math.max(0, Math.min(gridX, this.gridWidth - 1)),
            y: Math.max(0, Math.min(gridY, this.gridHeight - 1))
        };
    }
    
    /**
     * Get pixel coordinates from grid coordinates
     */
    getPixelCoordinates(gridX, gridY) {
        return {
            x: gridX * this.cellSize + this.cellSize / 2 + this.gridOffsetX,
            y: gridY * this.cellSize + this.cellSize / 2 + this.gridOffsetY
        };
    }
    
    /**
     * Check if a position is valid (within warehouse bounds)
     */
    isValidPosition(x, y) {
        return x >= 0 && x < this.gridWidth && y >= 0 && y < this.gridHeight;
    }
    
    /**
     * Get inventory location at grid coordinates
     */
    getInventoryLocation(x, y) {
        return this.layout.inventoryLocations.find(
            location => location.x === x && location.y === y
        );
    }
    
    /**
     * Update grid coordinates display
     */
    updateGridCoordinates(x, y) {
        const coordinatesElement = document.getElementById('grid-coordinates');
        if (coordinatesElement) {
            const column = String.fromCharCode(65 + x);
            const row = y + 1;
            coordinatesElement.textContent = `Grid: ${column}${row}`;
        }
    }
    
    /**
     * Handle canvas click events
     */
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const gridCoords = this.getGridCoordinates(x, y);
        this.updateGridCoordinates(gridCoords.x, gridCoords.y);
        
        console.log(`🖱️ Clicked at grid position: (${gridCoords.x}, ${gridCoords.y})`);
        
        // Check if clicked on inventory location
        const inventoryLocation = this.getInventoryLocation(gridCoords.x, gridCoords.y);
        if (inventoryLocation) {
            console.log(`📦 Clicked on inventory location: ${inventoryLocation.type}`);
        }
    }
    
    /**
     * Initialize event listeners
     */
    initEventListeners() {
        this.canvas.addEventListener('click', (event) => {
            this.handleClick(event);
        });
        
        console.log('🎯 Warehouse event listeners initialized');
    }
    
    /**
     * Render the warehouse (alias for draw method)
     */
    render() {
        this.draw();
    }
    
    /**
     * Handle window resize
     */
    handleResize() {
        // Recalculate canvas size if needed
        const container = this.canvas.parentElement;
        if (container) {
            const containerWidth = container.clientWidth;
            const containerHeight = container.clientHeight;
            
            // Maintain aspect ratio
            const aspectRatio = this.gridWidth / this.gridHeight;
            let newWidth = containerWidth;
            let newHeight = containerWidth / aspectRatio;
            
            if (newHeight > containerHeight) {
                newHeight = containerHeight;
                newWidth = containerHeight * aspectRatio;
            }
            
            // Update canvas size
            this.canvas.style.width = `${newWidth}px`;
            this.canvas.style.height = `${newHeight}px`;
            
            // Recalculate cell size
            this.cellSize = Math.min(newWidth / this.gridWidth, newHeight / this.gridHeight);
            
            // Recalculate padding and grid offset
            this.labelPadding.left = Math.floor((newWidth - this.gridWidth * this.cellSize) / 2);
            this.labelPadding.right = newWidth - (this.gridWidth * this.cellSize + this.labelPadding.left);
            this.labelPadding.top = Math.floor((newHeight - this.gridHeight * this.cellSize) / 2);
            this.labelPadding.bottom = newHeight - (this.gridHeight * this.cellSize + this.labelPadding.top);
            this.gridOffsetX = this.labelPadding.left;
            this.gridOffsetY = this.labelPadding.top;

            console.log(`📏 Resized canvas to ${newWidth}x${newHeight}, cell size: ${this.cellSize}px`);
        }
        
        // Redraw
        this.draw();
    }
}

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WarehouseVisualizer;
} 