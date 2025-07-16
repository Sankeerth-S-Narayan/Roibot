/**
 * Order Visualization Module
 * 
 * Handles order status display, queue visualization, order assignment,
 * progress tracking, and completion indicators.
 */

class OrderVisualizer {
    constructor(warehouseVisualizer) {
        this.warehouse = warehouseVisualizer;
        this.ctx = warehouseVisualizer.ctx;
        this.canvas = warehouseVisualizer.canvas;
        
        // Order configuration
        this.orderSize = 16; // 16x16 pixel order icon
        this.orderRadius = this.orderSize / 2;
        
        // Order queue and status
        this.orders = [];
        this.orderQueue = [];
        this.completedOrders = [];
        
        // Order colors by status
        this.orderColors = {
            PENDING: '#FF5722',    // Red
            IN_PROGRESS: '#FFC107', // Yellow
            COMPLETED: '#4CAF50',   // Green
            CANCELLED: '#9E9E9E'    // Gray
        };
        
        // Order status indicators
        this.orderStatusIcons = {
            PENDING: '⏳',
            IN_PROGRESS: '🔄',
            COMPLETED: '✅',
            CANCELLED: '❌'
        };
        
        // Animation configuration
        this.orderFadeDuration = 150; // ms
        this.orderUpdateInterval = 1000; // ms
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('📦 Initializing Order Visualizer');
        console.log(`📏 Order size: ${this.orderSize}x${this.orderSize}px`);
        console.log(`🎨 Order colors: ${Object.keys(this.orderColors).join(', ')}`);
        
        // Start order update timer
        this.startOrderUpdates();
    }
    
    /**
     * Create a new order
     */
    createOrder(orderData) {
        const order = {
            id: orderData.id || `ORDER_${Date.now()}`,
            status: 'PENDING',
            items: orderData.items || [],
            assignedRobot: null,
            createdAt: Date.now(),
            startedAt: null,
            completedAt: null,
            progress: 0,
            x: 0,
            y: 0,
            targetX: 0,
            targetY: 0,
            isMoving: false,
            movementProgress: 0
        };
        
        this.orders.push(order);
        this.orderQueue.push(order);
        
        console.log(`📦 Created order: ${order.id} with ${order.items.length} items`);
        this.updateOrderQueueDisplay();
        
        return order;
    }
    
    /**
     * Assign order to robot
     */
    assignOrderToRobot(orderId, robotId) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) {
            console.warn(`⚠️ Order ${orderId} not found`);
            return;
        }
        
        order.assignedRobot = robotId;
        order.status = 'IN_PROGRESS';
        order.startedAt = Date.now();
        
        // Remove from queue
        const queueIndex = this.orderQueue.findIndex(o => o.id === orderId);
        if (queueIndex !== -1) {
            this.orderQueue.splice(queueIndex, 1);
        }
        
        console.log(`🤖 Order ${orderId} assigned to robot ${robotId}`);
        this.updateOrderQueueDisplay();
    }
    
    /**
     * Update order progress
     */
    updateOrderProgress(orderId, progress) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) return;
        
        order.progress = Math.min(100, Math.max(0, progress));
        
        if (order.progress >= 100) {
            this.completeOrder(orderId);
        }
    }
    
    /**
     * Complete order
     */
    completeOrder(orderId) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) return;
        
        order.status = 'COMPLETED';
        order.completedAt = Date.now();
        order.progress = 100;
        
        this.completedOrders.push(order);
        
        console.log(`✅ Order ${orderId} completed`);
        this.updateOrderQueueDisplay();
    }
    
    /**
     * Cancel order
     */
    cancelOrder(orderId) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) return;
        
        order.status = 'CANCELLED';
        
        // Remove from queue
        const queueIndex = this.orderQueue.findIndex(o => o.id === orderId);
        if (queueIndex !== -1) {
            this.orderQueue.splice(queueIndex, 1);
        }
        
        console.log(`❌ Order ${orderId} cancelled`);
        this.updateOrderQueueDisplay();
    }
    
    /**
     * Move order to target position
     */
    moveOrderTo(orderId, targetX, targetY) {
        const order = this.orders.find(o => o.id === orderId);
        if (!order) return;
        
        order.targetX = targetX;
        order.targetY = targetY;
        order.isMoving = true;
        order.movementProgress = 0;
        
        console.log(`📦 Order ${orderId} moving to (${targetX}, ${targetY})`);
    }
    
    /**
     * Update orders from live backend data
     */
    update(data) {
        console.log('📦 [OrderVisualizer] Received order_data:', data);
        
        if (!data) {
            console.warn('📦 [OrderVisualizer] No data received');
            return;
        }
        
        // Handle different data formats
        if (Array.isArray(data)) {
            // Direct array of orders
            this.orders = data;
            this.orderQueue = data.filter(o => o.status === 'pending' || o.status === 'in_progress');
            this.completedOrders = data.filter(o => o.status === 'completed');
            console.log('📦 [OrderVisualizer] Processed array format - Queue:', this.orderQueue.length, 'Completed:', this.completedOrders.length);
        } else if (data.orders) {
            // Object with orders property
            this.orders = data.orders;
            this.orderQueue = data.orders.filter(o => o.status === 'pending' || o.status === 'in_progress');
            this.completedOrders = data.completed_orders || data.orders.filter(o => o.status === 'completed');
            console.log('📦 [OrderVisualizer] Processed object format - Queue:', this.orderQueue.length, 'Completed:', this.completedOrders.length);
        } else {
            console.warn('📦 [OrderVisualizer] Unknown data format:', data);
            return;
        }
        
        // Log the order queue details
        console.log('📦 [OrderVisualizer] Order queue details:', this.orderQueue);
        console.log('📦 [OrderVisualizer] Order statuses:', this.orders.map(o => `${o.id}: ${o.status}`));
        
        // Update order queue display
        this.updateOrderQueueDisplay();
        
        // Update completed orders panel
        if (typeof renderCompletedOrdersPanel === 'function') {
            renderCompletedOrdersPanel(this.completedOrders);
        }
        
        // Force a redraw
        this.render();
    }
    
    /**
     * Update order movement
     */
    updateOrderMovement(order, deltaTime) {
        if (!order.isMoving) return;
        
        // Update movement progress
        order.movementProgress += 0.05 * deltaTime; // 5% per frame
        
        if (order.movementProgress >= 1) {
            // Movement complete
            order.x = order.targetX;
            order.y = order.targetY;
            order.isMoving = false;
            order.movementProgress = 1;
        } else {
            // Interpolate position
            order.x = order.x + (order.targetX - order.x) * 0.05;
            order.y = order.y + (order.targetY - order.y) * 0.05;
        }
    }
    
    /**
     * Render orders
     */
    render() {
        if (!this.warehouse) return;
        
        // Render all orders
        this.orders.forEach(order => {
            this.renderOrder(order);
        });
    }
    
    /**
     * Render single order
     */
    renderOrder(order) {
        // Get pixel coordinates
        const pixelCoords = this.warehouse.getPixelCoordinates(order.x, order.y);
        
        // Draw order
        this.drawOrder(pixelCoords.x, pixelCoords.y, order);
        
        // Draw progress indicator if in progress
        if (order.status === 'IN_PROGRESS') {
            this.drawProgressIndicator(pixelCoords.x, pixelCoords.y, order.progress);
        }
    }
    
    /**
     * Draw order icon
     */
    drawOrder(x, y, order) {
        const color = this.orderColors[order.status] || this.orderColors.PENDING;
        const icon = this.orderStatusIcons[order.status] || '📦';
        
        // Draw order circle
        this.ctx.fillStyle = color;
        this.ctx.beginPath();
        this.ctx.arc(x, y, this.orderRadius, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Draw order border
        this.ctx.strokeStyle = '#FFFFFF';
        this.ctx.lineWidth = 1;
        this.ctx.stroke();
        
        // Draw order icon
        this.ctx.fillStyle = '#FFFFFF';
        this.ctx.font = '10px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(icon, x, y);
        
        // Draw order ID
        this.drawOrderLabel(x, y, order);
    }
    
    /**
     * Draw order label
     */
    drawOrderLabel(x, y, order) {
        const labelY = y - this.orderRadius - 8;
        
        this.ctx.fillStyle = '#212121';
        this.ctx.font = '8px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(order.id, x, labelY);
    }
    
    /**
     * Draw progress indicator
     */
    drawProgressIndicator(x, y, progress) {
        const indicatorY = y + this.orderRadius + 8;
        const indicatorWidth = 20;
        const indicatorHeight = 3;
        
        // Draw progress background
        this.ctx.fillStyle = '#E0E0E0';
        this.ctx.fillRect(x - indicatorWidth / 2, indicatorY, indicatorWidth, indicatorHeight);
        
        // Draw progress bar
        this.ctx.fillStyle = '#4CAF50';
        this.ctx.fillRect(x - indicatorWidth / 2, indicatorY, (indicatorWidth * progress) / 100, indicatorHeight);
        
        // Draw progress text
        this.ctx.fillStyle = '#212121';
        this.ctx.font = '8px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText(`${progress}%`, x, indicatorY + indicatorHeight + 8);
    }
    
    /**
     * Update order queue display in sidebar
     */
    updateOrderQueueDisplay() {
        console.log('📦 [OrderVisualizer] Updating order queue display');
        const queueElement = document.getElementById('order-queue-entity');
        if (!queueElement) {
            console.warn('📦 [OrderVisualizer] order-queue-entity element not found');
            return;
        }
        
        console.log('📦 [OrderVisualizer] Order queue length:', this.orderQueue.length);
        console.log('📦 [OrderVisualizer] Order queue contents:', this.orderQueue);
        
        // Clear current queue display
        queueElement.innerHTML = '';
        
        if (this.orderQueue.length === 0) {
            console.log('📦 [OrderVisualizer] No orders in queue, showing empty message');
            queueElement.innerHTML = '<div class="queue-item"><span class="order-id">No orders</span><span class="order-status">-</span></div>';
            return;
        }
        
        // Display queue orders
        this.orderQueue.slice(0, 5).forEach((order, index) => { // Show first 5 orders
            console.log(`📦 [OrderVisualizer] Adding order ${index + 1} to display:`, order);
            const queueItem = document.createElement('div');
            queueItem.className = 'queue-item';
            queueItem.innerHTML = `
                <span class="order-id">${order.id}</span>
                <span class="order-status">${order.status}</span>
            `;
            queueElement.appendChild(queueItem);
        });
        
        if (this.orderQueue.length > 5) {
            const moreItem = document.createElement('div');
            moreItem.className = 'queue-item';
            moreItem.innerHTML = `<span class="order-id">+${this.orderQueue.length - 5} more</span>`;
            queueElement.appendChild(moreItem);
        }
        
        console.log('📦 [OrderVisualizer] Order queue display updated with', this.orderQueue.length, 'orders');
    }
    
    /**
     * Get order statistics
     */
    getOrderStatistics() {
        const total = this.orders.length;
        const pending = this.orderQueue.length;
        const inProgress = this.orders.filter(o => o.status === 'IN_PROGRESS').length;
        const completed = this.completedOrders.length;
        const cancelled = this.orders.filter(o => o.status === 'CANCELLED').length;
        
        return {
            total,
            pending,
            inProgress,
            completed,
            cancelled,
            completionRate: total > 0 ? (completed / total) * 100 : 0
        };
    }
    
    /**
     * Update order from external data
     */
    updateFromData(data) {
        switch (data.type) {
            case 'order_created':
                this.createOrder(data.order);
                break;
            case 'order_assigned':
                this.assignOrderToRobot(data.orderId, data.robotId);
                break;
            case 'order_progress':
                this.updateOrderProgress(data.orderId, data.progress);
                break;
            case 'order_completed':
                this.completeOrder(data.orderId);
                break;
            case 'order_cancelled':
                this.cancelOrder(data.orderId);
                break;
            case 'order_moved':
                this.moveOrderTo(data.orderId, data.x, data.y);
                break;
        }
    }
    
    /**
     * Start order update timer
     */
    startOrderUpdates() {
        // DISABLED: Using real data from backend instead of local updates
        // The backend will send order updates via Socket.IO
        console.log('✅ Order updates disabled - using backend data');
    }
    
    /**
     * Simulate order creation for testing
     */
    simulateOrders() {
        // DISABLED: Using real backend order generation instead of simulation
        console.log('✅ Order simulation disabled - using real backend data');
    }
    
    /**
     * Clear all orders
     */
    clearOrders() {
        this.orders = [];
        this.orderQueue = [];
        this.completedOrders = [];
        this.updateOrderQueueDisplay();
        console.log('🗑️ All orders cleared');
    }
}

// Remove or comment out mockActiveOrders and renderOrderQueuePanel
// Mock data for completed orders
const mockCompletedOrders = [
  {
    order_id: "ORD_20250708_001",
    total_time_taken: "00:05:32",
    items_picked: ["ITEM_A1", "ITEM_B3", "ITEM_C7"],
    robot_id: "ROBOT_001",
    total_distance: "45.2m",
    completion_time: "2025-07-08T15:02:30Z",
    time_received: "2025-07-08T14:57:00Z"
  },
  {
    order_id: "ORD_20250708_002", 
    total_time_taken: "00:03:15",
    items_picked: ["ITEM_D2", "ITEM_E4"],
    robot_id: "ROBOT_002",
    total_distance: "28.7m",
    completion_time: "2025-07-08T15:05:45Z",
    time_received: "2025-07-08T15:02:30Z"
  },
  {
    order_id: "ORD_20250708_003",
    total_time_taken: "00:07:48",
    items_picked: ["ITEM_F5", "ITEM_G8", "ITEM_H2", "ITEM_I9"],
    robot_id: "ROBOT_001",
    total_distance: "67.3m",
    completion_time: "2025-07-08T15:12:18Z",
    time_received: "2025-07-08T15:04:30Z"
  }
];

function renderCompletedOrdersPanel(orders) {
  const container = document.getElementById('completed-orders-entity');
  if (!container) return;
  
  if (!orders || orders.length === 0) {
    container.innerHTML = '<div class="empty-panel">No completed orders</div>';
    return;
  }
  
  // Sort by completion time (newest first)
  const sortedOrders = orders.sort((a, b) => {
    const timeA = a.completed_time || a.completion_time || a.timestamp || 0;
    const timeB = b.completed_time || b.completion_time || b.timestamp || 0;
    return timeB - timeA;
  });
  
  container.innerHTML = sortedOrders.map(order => {
    // Handle different data structures from backend
    const orderId = order.order_id || order.id || 'Unknown';
    const items = order.items_picked || order.items || [];
    const robotId = order.robot_id || order.assigned_robot || 'ROBOT_001';
    
    // Calculate distance based on items count (rough estimate)
    const itemCount = Array.isArray(items) ? items.length : 0;
    const estimatedDistance = itemCount * 15; // 15 units per item average
    const distance = order.total_distance || `${estimatedDistance}m`;
    
    // FIXED TIMESTAMPS - Use ONLY stored backend values, NO fallbacks to current time
    const receivedTime = order.created_time || order.time_received || order.timestamp;
    const completionTime = order.completed_timestamp || order.completed_time || order.completion_time || order.frontend_completed_timestamp;
    
    // Calculate actual completion time from timestamps
    let totalTime = "00:00";
    if (receivedTime && completionTime) {
        // Convert timestamps to milliseconds if needed
        let receivedMs = receivedTime > 1000000000000 ? receivedTime : receivedTime * 1000;
        let completedMs = completionTime > 1000000000000 ? completionTime : completionTime * 1000;
        
        // Calculate duration in seconds
        const durationSeconds = Math.floor((completedMs - receivedMs) / 1000);
        
        if (durationSeconds >= 0) {
            const minutes = Math.floor(durationSeconds / 60);
            const seconds = durationSeconds % 60;
            totalTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }
    }
    // Fallback to backend's pre-calculated time if available and timestamps aren't
    else if (order.total_time_taken) {
        totalTime = order.total_time_taken;
    }
    
    // Format items array safely - show all items with proper line breaks
    const formatItemsForDisplay = (items) => {
        if (!Array.isArray(items) || items.length === 0) return 'No items';
        
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
    
    const itemsText = formatItemsForDisplay(items);
    
    return `
      <div class="completed-order-card">
        <div class="completed-order-header">
          <div class="completed-order-id"><b>${orderId}</b></div>
          <div class="completed-order-time">${totalTime}</div>
        </div>
        <div class="completed-order-details">
          <div class="completed-order-items">
            <span class="detail-label">Items:</span>
            <span class="detail-value">${itemsText}</span>
          </div>
          <div class="completed-order-robot">
            <span class="detail-label">Robot:</span>
            <span class="detail-value">${robotId}</span>
          </div>
          <div class="completed-order-distance">
            <span class="detail-label">Distance:</span>
            <span class="detail-value">${distance}</span>
          </div>
        </div>
        <div class="completed-order-timestamps">
          <div class="timestamp">
            <span class="timestamp-label">Received:</span>
            <span class="timestamp-value">${receivedTime ? formatTimestamp(receivedTime) : 'N/A'}</span>
          </div>
          <div class="timestamp">
            <span class="timestamp-label">Completed:</span>
            <span class="timestamp-value">${completionTime ? formatTimestamp(completionTime) : 'N/A'}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Helper function to format duration
function formatDuration(milliseconds) {
  const seconds = Math.floor(milliseconds / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${(minutes % 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
  } else {
    return `${minutes.toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`;
  }
}

// Helper function to format timestamp - show actual timestamp value
function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown';
  
  // Handle both seconds and milliseconds timestamps
  let date;
  if (timestamp > 1000000000000) {
    // Already in milliseconds
    date = new Date(timestamp);
  } else {
    // Convert seconds to milliseconds
    date = new Date(timestamp * 1000);
  }
  
  if (isNaN(date.getTime())) {
    return 'Invalid date';
  }
  
  // Format as timestamp showing date and time
  return date.toLocaleString();
}

// Helper function to format date/time (keeping for backward compatibility)
function formatDateTime(timestamp) {
  return formatTimestamp(timestamp);
}

// On DOMContentLoaded, render the completed orders panel with mock data
// DISABLED: Using real data from backend instead
// window.addEventListener('DOMContentLoaded', () => {
//   renderCompletedOrdersPanel(mockCompletedOrders);
// });

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OrderVisualizer;
} 