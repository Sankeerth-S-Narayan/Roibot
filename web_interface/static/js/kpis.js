/**
 * KPI Dashboard Module
 * 
 * Handles real-time KPI display, integration with analytics engine,
 * and dashboard updates for performance metrics.
 */

class KPIDashboard {
    constructor(warehouseVisualizer, robotVisualizer, orderVisualizer) {
        this.warehouse = warehouseVisualizer;
        this.robot = robotVisualizer;
        this.orders = orderVisualizer;
        
        // KPI configuration
        this.kpis = {
            ordersPerHour: 0,
            robotUtilization: 0,
            completionRate: 0,
            averageOrderTime: 0,
            queueLength: 0,
            totalOrders: 0,
            completedOrders: 0,
            simulationTime: 0
        };
        
        // KPI update intervals
        this.updateIntervals = {
            ordersPerHour: 5000,    // 5 seconds
            robotUtilization: 2000,  // 2 seconds
            completionRate: 3000,    // 3 seconds
            averageOrderTime: 4000,  // 4 seconds
            queueLength: 1000,       // 1 second
            simulationTime: 1000     // 1 second
        };
        
        // KPI thresholds for alerts
        this.thresholds = {
            ordersPerHour: { low: 10, high: 50 },
            robotUtilization: { low: 30, high: 80 },
            completionRate: { low: 70, high: 95 },
            queueLength: { low: 5, high: 20 }
        };
        
        // Historical data for rolling averages
        this.historicalData = {
            ordersPerHour: [],
            robotUtilization: [],
            completionRate: [],
            averageOrderTime: []
        };
        
        // Initialize
        this.init();
    }
    
    init() {
        console.log('📊 Initializing KPI Dashboard');
        console.log(`⏱️ Update intervals: ${Object.keys(this.updateIntervals).join(', ')}`);
        console.log(`🎯 Thresholds configured for ${Object.keys(this.thresholds).length} KPIs`);
        
        // Start KPI update timers
        // this.startKPIUpdates(); // Removed as per edit hint
        
        // Initialize dashboard display
        this.updateDashboard();
    }
    
    /**
     * Start KPI update timers
     */
    // startKPIUpdates() { // Removed as per edit hint
    //     // Orders per hour updates
    //     setInterval(() => {
    //         this.updateOrdersPerHour();
    //     }, this.updateIntervals.ordersPerHour);
        
    //     // Robot utilization updates
    //     setInterval(() => {
    //         this.updateRobotUtilization();
    //     }, this.updateIntervals.robotUtilization);
        
    //     // Completion rate updates
    //     setInterval(() => {
    //         this.updateCompletionRate();
    //     }, this.updateIntervals.completionRate);
        
    //     // Average order time updates
    //     setInterval(() => {
    //         this.updateAverageOrderTime();
    //     }, this.updateIntervals.averageOrderTime);
        
    //     // Queue length updates
    //     setInterval(() => {
    //         this.updateQueueLength();
    //     }, this.updateIntervals.queueLength);
        
    //     // Simulation time updates
    //     setInterval(() => {
    //         this.updateSimulationTime();
    //     }, this.updateIntervals.simulationTime);
        
    //     console.log('✅ KPI update timers started');
    // } // Removed as per edit hint
    
    /**
     * Update orders per hour KPI
     */
    updateOrdersPerHour() {
        if (!this.orders) return;
        
        const stats = this.orders.getOrderStatistics();
        const currentTime = Date.now();
        
        // Calculate orders per hour based on completed orders
        const completedOrders = stats.completed;
        const simulationTimeHours = this.kpis.simulationTime / 3600000; // Convert to hours
        
        if (simulationTimeHours > 0) {
            this.kpis.ordersPerHour = Math.round(completedOrders / simulationTimeHours);
        } else {
            this.kpis.ordersPerHour = 0;
        }
        
        // Add to historical data (keep last 10 values)
        this.historicalData.ordersPerHour.push(this.kpis.ordersPerHour);
        if (this.historicalData.ordersPerHour.length > 10) {
            this.historicalData.ordersPerHour.shift();
        }
        
        this.updateKPIDisplay('orders-per-hour', this.kpis.ordersPerHour);
        this.checkThreshold('ordersPerHour', this.kpis.ordersPerHour);
    }
    
    /**
     * Update robot utilization KPI
     */
    updateRobotUtilization() {
        if (!this.robot) return;
        
        const robotState = this.robot.getRobotPosition();
        
        // Calculate utilization based on robot state
        let utilization = 0;
        if (robotState.state === 'MOVING' || robotState.state === 'PICKING' || robotState.state === 'COLLECTING') {
            utilization = 100;
        } else if (robotState.state === 'IDLE') {
            utilization = 0;
        } else if (robotState.state === 'RETURNING') {
            utilization = 75;
        }
        
        this.kpis.robotUtilization = utilization;
        
        // Add to historical data
        this.historicalData.robotUtilization.push(utilization);
        if (this.historicalData.robotUtilization.length > 10) {
            this.historicalData.robotUtilization.shift();
        }
        
        this.updateKPIDisplay('robot-utilization', utilization);
        this.checkThreshold('robotUtilization', utilization);
    }
    
    /**
     * Update completion rate KPI
     */
    updateCompletionRate() {
        if (!this.orders) return;
        
        const stats = this.orders.getOrderStatistics();
        const completionRate = stats.completionRate;
        
        this.kpis.completionRate = completionRate;
        
        // Add to historical data
        this.historicalData.completionRate.push(completionRate);
        if (this.historicalData.completionRate.length > 10) {
            this.historicalData.completionRate.shift();
        }
        
        this.updateKPIDisplay('completion-rate', `${completionRate.toFixed(1)}%`);
        this.checkThreshold('completionRate', completionRate);
    }
    
    /**
     * Update average order time KPI
     */
    updateAverageOrderTime() {
        if (!this.orders) return;
        
        const stats = this.orders.getOrderStatistics();
        const completedOrders = stats.completed;
        
        if (completedOrders > 0) {
            // Calculate average order time (simplified for demo)
            const averageTime = Math.round(this.kpis.simulationTime / completedOrders);
            this.kpis.averageOrderTime = averageTime;
            
            // Add to historical data
            this.historicalData.averageOrderTime.push(averageTime);
            if (this.historicalData.averageOrderTime.length > 10) {
                this.historicalData.averageOrderTime.shift();
            }
            
            this.updateKPIDisplay('avg-order-time', `${averageTime}s`);
        } else {
            this.kpis.averageOrderTime = 0;
            this.updateKPIDisplay('avg-order-time', '0s');
        }
    }
    
    /**
     * Update queue length KPI
     */
    updateQueueLength() {
        if (!this.orders) return;
        
        const stats = this.orders.getOrderStatistics();
        const queueLength = stats.pending;
        
        this.kpis.queueLength = queueLength;
        
        this.updateKPIDisplay('queue-length', queueLength);
        this.checkThreshold('queueLength', queueLength);
    }
    
    /**
     * Update simulation time KPI
     */
    updateSimulationTime() {
        // Increment simulation time (in milliseconds)
        this.kpis.simulationTime += 1000;
        
        // Format time as HH:MM:SS
        const hours = Math.floor(this.kpis.simulationTime / 3600000);
        const minutes = Math.floor((this.kpis.simulationTime % 3600000) / 60000);
        const seconds = Math.floor((this.kpis.simulationTime % 60000) / 1000);
        
        const timeString = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        
        this.updateKPIDisplay('simulation-time', timeString);
    }
    
    /**
     * Update KPI display element with formatted value
     */
    updateKPIDisplay(elementId, value) {
        const element = document.getElementById(elementId);
        if (element) {
            // Format all numbers to prevent layout issues and ensure 1 decimal place
            let formattedValue = value;
            
            // Special formatting for different KPI types
            if (elementId === 'orders-per-hour') {
                if (typeof value === 'number') {
                    // Round to 1 decimal place and use smart formatting for large numbers
                    if (value >= 1000) {
                        formattedValue = (value / 1000).toFixed(1) + 'k';
                    } else {
                        formattedValue = value.toFixed(1);
                    }
                }
            } else if (elementId === 'avg-order-time') {
                if (typeof value === 'number') {
                    // Format as minutes:seconds if it's a raw number of seconds
                    const minutes = Math.floor(value / 60);
                    const seconds = Math.floor(value % 60);
                    formattedValue = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                }
            } else if (elementId === 'robot-utilization' || elementId === 'completion-rate') {
                if (typeof value === 'number') {
                    // Round to 1 decimal place for percentages
                    formattedValue = `${value.toFixed(1)}%`;
                }
            } else if (elementId === 'queue-length') {
                if (typeof value === 'number') {
                    // Format as a whole number
                    formattedValue = Math.round(value);
                }
            } else if (typeof value === 'number') {
                // For other numeric values, use 1 decimal place with smart formatting
                if (value >= 1000000) {
                    formattedValue = (value / 1000000).toFixed(1) + 'M';
                } else if (value >= 1000) {
                    formattedValue = (value / 1000).toFixed(1) + 'k';
                } else {
                    formattedValue = value.toFixed(1);
                }
            }
            
            element.textContent = formattedValue;
            
            // Add visual feedback for changes - apply to parent kpi-item
            const kpiItem = element.closest('.kpi-item');
            if (kpiItem) {
                kpiItem.classList.add('kpi-updated');
                setTimeout(() => {
                    kpiItem.classList.remove('kpi-updated');
                }, 500);
            }
        }
    }
    
    /**
     * Check KPI thresholds and trigger alerts
     */
    checkThreshold(kpiName, value) {
        const threshold = this.thresholds[kpiName];
        if (!threshold) return;
        
        const element = document.getElementById(`${kpiName.replace(/([A-Z])/g, '-$1').toLowerCase()}`);
        if (!element) return;
        
        // Remove existing alert classes
        element.classList.remove('kpi-low', 'kpi-high', 'kpi-normal');
        
        // Add appropriate alert class
        if (value <= threshold.low) {
            element.classList.add('kpi-low');
        } else if (value >= threshold.high) {
            element.classList.add('kpi-high');
        } else {
            element.classList.add('kpi-normal');
        }
    }
    
    /**
     * Get KPI data for external use
     */
    getKPIData() {
        return {
            ...this.kpis,
            historicalData: this.historicalData
        };
    }
    
    /**
     * Update KPIs from live backend data
     */
    update(data) {
        console.log('📊 [KPIDashboard] Received kpi_data:', data);
        if (!data) return;
        // Map backend keys to frontend keys if needed
        this.kpis.ordersPerHour = data.orders_per_hour || 0;
        this.kpis.robotUtilization = data.robot_utilization || 0;
        this.kpis.completionRate = data.order_completion_rate || 0;
        this.kpis.averageOrderTime = data.average_order_time || 0;
        this.kpis.queueLength = data.queue_length || 0;
        this.kpis.totalOrders = data.total_orders || 0;
        this.kpis.completedOrders = data.completed_orders || 0;
        this.kpis.simulationTime = data.simulation_time || 0;
        this.updateDashboard();
    }
    
    /**
     * Update simulation state
     */
    updateSimulationState(state) {
        if (state.paused) {
            // Pause KPI updates when simulation is paused
            this.pauseUpdates();
        } else {
            // Resume KPI updates when simulation is running
            this.resumeUpdates();
        }
    }
    
    /**
     * Pause KPI updates
     */
    pauseUpdates() {
        console.log('⏸️ KPI updates paused');
    }
    
    /**
     * Resume KPI updates
     */
    resumeUpdates() {
        console.log('▶️ KPI updates resumed');
    }
    
    /**
     * Update dashboard display
     */
    updateDashboard() {
        // First render the KPI dashboard structure
        renderKPIDashboard({
            ordersPerHour: this.kpis.ordersPerHour,
            robotUtilization: this.kpis.robotUtilization,
            completionRate: this.kpis.completionRate,
            averageOrderTime: this.kpis.averageOrderTime,
            queueLength: this.kpis.queueLength,
            totalOrders: this.kpis.totalOrders,
            completedOrders: this.kpis.completedOrders
        });
        
        // Then update the values with proper formatting
        this.updateKPIDisplay('orders-per-hour', this.kpis.ordersPerHour);
        this.updateKPIDisplay('robot-utilization', this.kpis.robotUtilization);
        this.updateKPIDisplay('completion-rate', this.kpis.completionRate);
        this.updateKPIDisplay('avg-order-time', this.kpis.averageOrderTime);
        this.updateKPIDisplay('queue-length', this.kpis.queueLength);
        
        // Format orders status manually as integers
        const ordersStatusElement = document.getElementById('orders-status');
        if (ordersStatusElement) {
          const completedFormatted = Math.round(this.kpis.completedOrders || 0);
          const totalFormatted = Math.round(this.kpis.totalOrders || 0);
          ordersStatusElement.textContent = `${completedFormatted}/${totalFormatted}`;
        }
        
        // Update progress bars
        const robotUtilBar = document.getElementById('robot-utilization-bar');
        if (robotUtilBar) {
          robotUtilBar.style.width = `${Math.min(this.kpis.robotUtilization || 0, 100)}%`;
        }
        
        const completionRateBar = document.getElementById('completion-rate-bar');
        if (completionRateBar) {
          completionRateBar.style.width = `${Math.min(this.kpis.completionRate || 0, 100)}%`;
        }
    }
    
    /**
     * Render KPI dashboard
     */
    render() {
        // KPI dashboard is primarily updated via DOM elements
        // This method can be used for any canvas-based KPI visualization
        this.updateDashboard();
    }
    
    /**
     * Export KPI data for analysis
     */
    exportKPIData() {
        return {
            timestamp: Date.now(),
            kpis: this.kpis,
            historicalData: this.historicalData,
            thresholds: this.thresholds
        };
    }
    
    /**
     * Reset KPI dashboard
     */
    reset() {
        this.kpis = {
            ordersPerHour: 0,
            robotUtilization: 0,
            completionRate: 0,
            averageOrderTime: 0,
            queueLength: 0,
            totalOrders: 0,
            completedOrders: 0,
            simulationTime: 0
        };
        
        this.historicalData = {
            ordersPerHour: [],
            robotUtilization: [],
            completionRate: [],
            averageOrderTime: []
        };
        
        this.updateDashboard();
        console.log('🔄 KPI dashboard reset');
    }
}

// Mock data for KPIs
const mockKPIData = {
  ordersPerHour: 24,
  robotUtilization: 78,
  completionRate: 94.5,
  averageOrderTime: 245,
  queueLength: 3,
  totalOrders: 156,
  completedOrders: 142
};

function renderKPIDashboard(kpiData) {
  const container = document.getElementById('kpi-dashboard');
  if (!container) return;
  
  if (!kpiData) {
    container.innerHTML = '<div class="empty-panel">No KPI data available</div>';
    return;
  }
  
  // Create HTML structure with proper IDs - values will be updated by updateDashboard
  container.innerHTML = `
    <div class="kpi-grid">
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Orders per Hour</div>
          <div class="kpi-value" id="orders-per-hour">0.0</div>
        </div>
      </div>
      
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Robot Utilization</div>
          <div class="kpi-value" id="robot-utilization">0.0%</div>
          <div class="kpi-progress">
            <div class="kpi-progress-bar" id="robot-utilization-bar" style="width: 0%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Completion Rate</div>
          <div class="kpi-value" id="completion-rate">0.0%</div>
          <div class="kpi-progress">
            <div class="kpi-progress-bar" id="completion-rate-bar" style="width: 0%"></div>
          </div>
        </div>
      </div>
      
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Avg Order Completion Time</div>
          <div class="kpi-value" id="avg-order-time">0:00</div>
        </div>
      </div>
      
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Queue Length</div>
          <div class="kpi-value" id="queue-length">0.0</div>
        </div>
      </div>
      
      <div class="kpi-item">
        <div class="kpi-content">
          <div class="kpi-label">Orders Status</div>
          <div class="kpi-value" id="orders-status">0.0/0.0</div>
        </div>
      </div>
    </div>
  `;
}

// On DOMContentLoaded, render the KPI dashboard with mock data
// DISABLED: Using real data from backend instead
// window.addEventListener('DOMContentLoaded', () => {
//   renderKPIDashboard(mockKPIData);
// });

// Export for use in main application
if (typeof module !== 'undefined' && module.exports) {
    module.exports = KPIDashboard;
} 