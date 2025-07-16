from typing import List, Optional, Dict, Any, Callable
from enum import Enum
import time
from dataclasses import dataclass
from .robot_orders import Order, OrderStatus
from .robot_order_assigner import RobotOrderAssigner
from .order_queue_manager import OrderQueueManager
from .robot_state import RobotState

class OrderStatusEvent(Enum):
    """Enumeration for order status events."""
    ORDER_CREATED = "order_created"
    ORDER_ASSIGNED = "order_assigned"
    ORDER_IN_PROGRESS = "order_in_progress"
    ITEM_COLLECTED = "item_collected"
    ORDER_COMPLETED = "order_completed"
    ORDER_FAILED = "order_failed"
    ORDER_TIMEOUT = "order_timeout"

@dataclass
class OrderCompletionMetrics:
    """Metrics for order completion tracking."""
    completion_time: float = 0.0  # Time from IN_PROGRESS to COMPLETED
    total_distance: float = 0.0   # Total distance traveled by robot
    efficiency_score: float = 0.0  # Efficiency score (0.0 to 1.0)
    items_collected: int = 0      # Number of items collected
    total_items: int = 0          # Total items in order
    direction_changes: int = 0    # Number of direction changes
    path_optimization_savings: float = 0.0  # Distance saved by path optimization

class OrderStatusTracker:
    """
    Handles comprehensive order status tracking and completion verification.
    
    Provides real-time status updates, completion verification based on robot
    item collection, metrics calculation, and integration with existing
    order management systems.
    """
    
    def __init__(self, robot_assigner: RobotOrderAssigner, queue_manager: OrderQueueManager):
        """
        Initialize the order status tracker.
        
        Args:
            robot_assigner: RobotOrderAssigner instance for robot integration
            queue_manager: OrderQueueManager instance for queue integration
        """
        self.robot_assigner = robot_assigner
        self.queue_manager = queue_manager
        
        # Status tracking
        self.active_orders: Dict[str, Order] = {}
        self.completed_orders: Dict[str, Order] = {}
        self.failed_orders: Dict[str, Order] = {}
        
        # Metrics tracking
        self.completion_metrics: Dict[str, OrderCompletionMetrics] = {}
        
        # Event callbacks
        self.status_callbacks: List[Callable] = []
        self.completion_callbacks: List[Callable] = []
        
        # Configuration
        self.order_timeout_seconds = 300.0  # 5 minutes default timeout
        self.efficiency_threshold = 0.8     # Efficiency threshold for good performance
        
        # Statistics
        self.total_orders_tracked = 0
        self.total_completions = 0
        self.total_failures = 0
        self.average_completion_time = 0.0
        self.average_efficiency_score = 0.0
        
        print(f"📊 OrderStatusTracker initialized")
    
    def track_order(self, order: Order) -> bool:
        """
        Start tracking an order for status updates.
        
        Args:
            order: Order object to track
            
        Returns:
            True if tracking started successfully, False otherwise
        """
        try:
            if order.order_id in self.active_orders:
                print(f"⚠️  Order {order.order_id} is already being tracked")
                return False
            
            # Set initial status to IN_QUEUE
            order.status = OrderStatus.PENDING  # This will be updated to IN_QUEUE when added to queue
            
            # Add to active orders
            self.active_orders[order.order_id] = order
            
            # Initialize completion metrics
            self.completion_metrics[order.order_id] = OrderCompletionMetrics(
                total_items=len(order.item_ids)
            )
            
            # Update statistics
            self.total_orders_tracked += 1
            
            # Emit order created event
            self._emit_status_event(OrderStatusEvent.ORDER_CREATED, order)
            
            print(f"📋 Started tracking order {order.order_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error tracking order {order.order_id}: {e}")
            return False
    
    def update_order_status(self, order_id: str, new_status: OrderStatus, 
                          robot_id: Optional[str] = None, 
                          collected_items: Optional[List[str]] = None) -> bool:
        """
        Update order status with real-time tracking.
        
        Args:
            order_id: ID of the order to update
            new_status: New status for the order
            robot_id: Optional robot ID for assignment
            collected_items: Optional list of collected items
            
        Returns:
            True if status updated successfully, False otherwise
        """
        try:
            if order_id not in self.active_orders:
                print(f"⚠️  Order {order_id} not found in active orders")
                return False
            
            order = self.active_orders[order_id]
            old_status = order.status
            
            # Update order status
            order.status = new_status
            
            # Handle specific status transitions
            if new_status == OrderStatus.IN_PROGRESS:
                self._handle_order_in_progress(order, robot_id)
            elif new_status == OrderStatus.COMPLETED:
                self._handle_order_completed(order)
            elif new_status == OrderStatus.FAILED:
                self._handle_order_failed(order)
            
            # Update collected items if provided
            if collected_items:
                for item_id in collected_items:
                    order.mark_item_collected(item_id)
                
                # Check for completion
                if order.is_complete() and new_status != OrderStatus.COMPLETED:
                    self._handle_order_completed(order)
            
            # Emit status event
            self._emit_status_event(OrderStatusEvent.ORDER_IN_PROGRESS, order)
            
            print(f"🔄 Updated order {order_id} status: {old_status.value} → {new_status.value}")
            return True
            
        except Exception as e:
            print(f"❌ Error updating order {order_id} status: {e}")
            return False
    
    def mark_item_collected(self, order_id: str, item_id: str, 
                           robot_id: str, collection_time: float) -> bool:
        """
        Mark an item as collected with real-time tracking.
        
        Args:
            order_id: ID of the order
            item_id: ID of the collected item
            robot_id: ID of the robot that collected the item
            collection_time: Timestamp of collection
            
        Returns:
            True if item marked as collected successfully, False otherwise
        """
        try:
            if order_id not in self.active_orders:
                print(f"⚠️  Order {order_id} not found in active orders")
                return False
            
            order = self.active_orders[order_id]
            
            # Mark item as collected
            if order.mark_item_collected(item_id):
                # Update metrics
                metrics = self.completion_metrics[order_id]
                metrics.items_collected += 1
                
                # Emit item collected event
                self._emit_status_event(OrderStatusEvent.ITEM_COLLECTED, order, {
                    'item_id': item_id,
                    'robot_id': robot_id,
                    'collection_time': collection_time,
                    'items_collected': metrics.items_collected,
                    'total_items': metrics.total_items
                })
                
                # Check if order is complete
                if order.is_complete():
                    self._handle_order_completed(order)
                
                print(f"📦 Marked item {item_id} as collected for order {order_id}")
                return True
            else:
                print(f"⚠️  Item {item_id} already collected or not in order {order_id}")
                return False
                
        except Exception as e:
            print(f"❌ Error marking item {item_id} as collected: {e}")
            return False
    
    def _handle_order_in_progress(self, order: Order, robot_id: Optional[str] = None):
        """Handle order transition to IN_PROGRESS status."""
        try:
            # Update assignment information
            if robot_id:
                order.assigned_robot_id = robot_id
                order.timestamp_assigned = time.time()
            
            # Emit order assigned event
            self._emit_status_event(OrderStatusEvent.ORDER_ASSIGNED, order, {
                'robot_id': robot_id,
                'assignment_time': time.time()
            })
            
            print(f"🎯 Order {order.order_id} assigned to robot {robot_id}")
            
        except Exception as e:
            print(f"❌ Error handling order in progress: {e}")
    
    def _handle_order_completed(self, order: Order):
        """Handle order completion."""
        try:
            # Calculate completion metrics
            completion_time = 0.0
            if order.timestamp_assigned:
                completion_time = time.time() - order.timestamp_assigned
            
            # Calculate efficiency score
            efficiency_score = self._calculate_efficiency_score(order)
            
            # Calculate total distance (simplified - in real system would track actual distance)
            total_distance = self._calculate_total_distance(order)
            
            # Update order completion
            order.complete_order(time.time(), total_distance, efficiency_score)
            
            # Update completion metrics
            metrics = self.completion_metrics[order.order_id]
            metrics.completion_time = completion_time
            metrics.efficiency_score = efficiency_score
            metrics.total_distance = total_distance
            metrics.items_collected = len(order.items_collected)
            
            # Move order to completed list
            del self.active_orders[order.order_id]
            self.completed_orders[order.order_id] = order
            
            # Remove from queue if present
            self.queue_manager.remove_order(order)
            
            # Update statistics
            self.total_completions += 1
            self._update_average_metrics()
            
            # Emit completion event
            self._emit_status_event(OrderStatusEvent.ORDER_COMPLETED, order, {
                'completion_time': completion_time,
                'efficiency_score': efficiency_score,
                'total_distance': total_distance
            })
            
            print(f"✅ Order {order.order_id} completed (time: {completion_time:.2f}s, efficiency: {efficiency_score:.2f})")
            
        except Exception as e:
            print(f"❌ Error handling order completion: {e}")
    
    def _handle_order_failed(self, order: Order):
        """Handle order failure."""
        try:
            # Mark order as failed
            order.fail_order()
            
            # Move order to failed list
            del self.active_orders[order.order_id]
            self.failed_orders[order.order_id] = order
            
            # Remove from queue if present
            self.queue_manager.remove_order(order)
            
            # Update statistics
            self.total_failures += 1
            
            # Emit failure event
            self._emit_status_event(OrderStatusEvent.ORDER_FAILED, order)
            
            print(f"❌ Order {order.order_id} failed")
            
        except Exception as e:
            print(f"❌ Error handling order failure: {e}")
    
    def _calculate_efficiency_score(self, order: Order) -> float:
        """
        Calculate efficiency score for the order.
        
        Args:
            order: Order object
            
        Returns:
            Efficiency score (0.0 to 1.0)
        """
        try:
            # Base efficiency on items collected vs total items
            if len(order.item_ids) == 0:
                return 0.0
            
            collection_efficiency = len(order.items_collected) / len(order.item_ids)
            
            # Consider completion time (shorter is better)
            time_efficiency = 1.0
            if order.timestamp_assigned and order.timestamp_completed:
                completion_time = order.timestamp_completed - order.timestamp_assigned
                # Normalize time efficiency (assume 5 minutes is optimal)
                time_efficiency = max(0.0, 1.0 - (completion_time / 300.0))
            
            # Weighted average
            efficiency = (collection_efficiency * 0.7) + (time_efficiency * 0.3)
            
            return min(1.0, max(0.0, efficiency))
            
        except Exception as e:
            print(f"❌ Error calculating efficiency score: {e}")
            return 0.0
    
    def _calculate_total_distance(self, order: Order) -> float:
        """
        Calculate total distance traveled for the order.
        
        Args:
            order: Order object
            
        Returns:
            Total distance traveled
        """
        try:
            # Simplified distance calculation
            # In a real system, this would track actual robot movement
            base_distance = len(order.item_ids) * 10.0  # 10 units per item
            return base_distance
            
        except Exception as e:
            print(f"❌ Error calculating total distance: {e}")
            return 0.0
    
    def _update_average_metrics(self):
        """Update average completion metrics."""
        try:
            if self.total_completions > 0:
                # Calculate average completion time
                total_time = sum(metrics.completion_time 
                               for metrics in self.completion_metrics.values())
                self.average_completion_time = total_time / self.total_completions
                
                # Calculate average efficiency score
                total_efficiency = sum(metrics.efficiency_score 
                                     for metrics in self.completion_metrics.values())
                self.average_efficiency_score = total_efficiency / self.total_completions
                
        except Exception as e:
            print(f"❌ Error updating average metrics: {e}")
    
    def _emit_status_event(self, event_type: OrderStatusEvent, order: Order, 
                          additional_data: Optional[Dict[str, Any]] = None):
        """Emit a status event to registered callbacks."""
        try:
            event_data = {
                'event_type': event_type.value,
                'order_id': order.order_id,
                'order_status': order.status.value,
                'timestamp': time.time()
            }
            
            if additional_data:
                event_data.update(additional_data)
            
            # Call status callbacks
            for callback in self.status_callbacks:
                try:
                    callback(event_data)
                except Exception as e:
                    print(f"❌ Error in status callback: {e}")
            
            # Call completion callbacks for completion events
            if event_type in [OrderStatusEvent.ORDER_COMPLETED, OrderStatusEvent.ORDER_FAILED]:
                for callback in self.completion_callbacks:
                    try:
                        callback(event_data)
                    except Exception as e:
                        print(f"❌ Error in completion callback: {e}")
                    
        except Exception as e:
            print(f"❌ Error emitting status event: {e}")
    
    def add_status_callback(self, callback: Callable):
        """Add a callback for status events."""
        self.status_callbacks.append(callback)
    
    def add_completion_callback(self, callback: Callable):
        """Add a callback for completion events."""
        self.completion_callbacks.append(callback)
    
    def get_order_status(self, order_id: str) -> Optional[OrderStatus]:
        """
        Get the current status of an order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Order status or None if order not found
        """
        if order_id in self.active_orders:
            return self.active_orders[order_id].status
        elif order_id in self.completed_orders:
            return self.completed_orders[order_id].status
        elif order_id in self.failed_orders:
            return self.failed_orders[order_id].status
        else:
            return None
    
    def get_completion_metrics(self, order_id: str) -> Optional[OrderCompletionMetrics]:
        """
        Get completion metrics for an order.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Completion metrics or None if not found
        """
        return self.completion_metrics.get(order_id)
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive tracking statistics.
        
        Returns:
            Dictionary with tracking statistics
        """
        return {
            'total_orders_tracked': self.total_orders_tracked,
            'active_orders': len(self.active_orders),
            'completed_orders': len(self.completed_orders),
            'failed_orders': len(self.failed_orders),
            'total_completions': self.total_completions,
            'total_failures': self.total_failures,
            'average_completion_time': self.average_completion_time,
            'average_efficiency_score': self.average_efficiency_score,
            'completion_rate': self.total_completions / max(1, self.total_orders_tracked),
            'failure_rate': self.total_failures / max(1, self.total_orders_tracked)
        }
    
    def get_active_orders(self) -> List[Order]:
        """Get list of currently active orders."""
        return list(self.active_orders.values())
    
    def get_completed_orders(self) -> List[Order]:
        """Get list of completed orders."""
        return list(self.completed_orders.values())
    
    def get_failed_orders(self) -> List[Order]:
        """Get list of failed orders."""
        return list(self.failed_orders.values())
    
    def clear_completed_orders(self):
        """Clear completed orders from memory."""
        self.completed_orders.clear()
        print("🧹 Cleared completed orders from memory")
    
    def clear_failed_orders(self):
        """Clear failed orders from memory."""
        self.failed_orders.clear()
        print("🧹 Cleared failed orders from memory")
    
    def reset_statistics(self):
        """Reset all tracking statistics."""
        self.total_orders_tracked = 0
        self.total_completions = 0
        self.total_failures = 0
        self.average_completion_time = 0.0
        self.average_efficiency_score = 0.0
        self.completion_metrics.clear()
        
        print("📊 Order status tracking statistics reset")
    
    def get_debug_info(self) -> Dict[str, Any]:
        """
        Get debug information for the status tracker.
        
        Returns:
            Dictionary with debug information
        """
        return {
            'tracking_statistics': self.get_tracking_statistics(),
            'active_orders': {
                order_id: {
                    'status': order.status.value,
                    'items_collected': len(order.items_collected),
                    'total_items': len(order.item_ids),
                    'assigned_robot': order.assigned_robot_id
                }
                for order_id, order in self.active_orders.items()
            },
            'completion_metrics': {
                order_id: {
                    'completion_time': metrics.completion_time,
                    'efficiency_score': metrics.efficiency_score,
                    'total_distance': metrics.total_distance,
                    'items_collected': metrics.items_collected,
                    'total_items': metrics.total_items
                }
                for order_id, metrics in self.completion_metrics.items()
            },
            'callbacks': {
                'status_callbacks': len(self.status_callbacks),
                'completion_callbacks': len(self.completion_callbacks)
            }
        } 