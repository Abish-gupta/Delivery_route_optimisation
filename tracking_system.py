import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class DeliveryStatus(Enum):
    """Enumeration for delivery status"""
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"

@dataclass
class Location:
    """Location data class"""
    latitude: float
    longitude: float
    timestamp: datetime
    accuracy: float = 10.0  # GPS accuracy in meters
    
    def to_dict(self) -> Dict:
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat(),
            'accuracy': self.accuracy
        }

@dataclass
class DeliveryUpdate:
    """Delivery update data class"""
    order_id: str
    status: DeliveryStatus
    location: Location
    message: str
    driver_id: str
    estimated_delivery_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'order_id': self.order_id,
            'status': self.status.value,
            'location': self.location.to_dict(),
            'message': self.message,
            'driver_id': self.driver_id,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None
        }

class DeliveryTrackingSystem:
    """Real-time delivery tracking system with notifications and analytics"""
    
    def __init__(self, db_path: str = "delivery_tracking.db"):
        self.db_path = db_path
        self.initialize_database()
        self.notification_handlers = []
        
    def initialize_database(self):
        """Initialize SQLite database for tracking data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                customer_email TEXT,
                customer_phone TEXT,
                pickup_address TEXT NOT NULL,
                delivery_address TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                scheduled_delivery TIMESTAMP,
                current_status TEXT DEFAULT 'pending',
                driver_id TEXT,
                vehicle_id TEXT,
                special_instructions TEXT
            )
        ''')
        
        # Create tracking_updates table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                status TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message TEXT,
                driver_id TEXT,
                accuracy REAL DEFAULT 10.0,
                FOREIGN KEY (order_id) REFERENCES orders (order_id)
            )
        ''')
        
        # Create notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                notification_type TEXT NOT NULL,
                recipient TEXT NOT NULL,
                message TEXT NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                delivery_status TEXT DEFAULT 'pending',
                FOREIGN KEY (order_id) REFERENCES orders (order_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_order(self, order_data: Dict) -> str:
        """Create a new delivery order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO orders (
                order_id, customer_id, customer_name, customer_email, 
                customer_phone, pickup_address, delivery_address, 
                scheduled_delivery, driver_id, vehicle_id, special_instructions
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            order_data['order_id'],
            order_data['customer_id'],
            order_data['customer_name'],
            order_data.get('customer_email'),
            order_data.get('customer_phone'),
            order_data['pickup_address'],
            order_data['delivery_address'],
            order_data.get('scheduled_delivery'),
            order_data.get('driver_id'),
            order_data.get('vehicle_id'),
            order_data.get('special_instructions')
        ))
        
        conn.commit()
        conn.close()
        
        # Send initial notification
        self.send_notification(
            order_data['order_id'], 
            "order_created", 
            f"Order {order_data['order_id']} has been created and will be processed soon."
        )
        
        return order_data['order_id']
    
    def update_delivery_status(self, update: DeliveryUpdate):
        """Update delivery status with location and send notifications"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insert tracking update
        cursor.execute('''
            INSERT INTO tracking_updates (
                order_id, status, latitude, longitude, timestamp, 
                message, driver_id, accuracy
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            update.order_id,
            update.status.value,
            update.location.latitude,
            update.location.longitude,
            update.location.timestamp,
            update.message,
            update.driver_id,
            update.location.accuracy
        ))
        
        # Update order status
        cursor.execute('''
            UPDATE orders 
            SET current_status = ?, driver_id = ?
            WHERE order_id = ?
        ''', (update.status.value, update.driver_id, update.order_id))
        
        conn.commit()
        conn.close()
        
        # Send status notification
        self.send_status_notification(update)
        
        # Calculate ETA if in transit
        if update.status in [DeliveryStatus.IN_TRANSIT, DeliveryStatus.OUT_FOR_DELIVERY]:
            eta = self.calculate_eta(update.order_id, update.location)
            if eta:
                self.send_eta_notification(update.order_id, eta)
    
    def get_order_tracking(self, order_id: str) -> Dict:
        """Get complete tracking information for an order"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get order details
        cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
        order_row = cursor.fetchone()
        
        if not order_row:
            conn.close()
            return {"error": "Order not found"}
        
        # Convert to dictionary
        order_columns = [desc[0] for desc in cursor.description]
        order_data = dict(zip(order_columns, order_row))
        
        # Get tracking updates
        cursor.execute('''
            SELECT * FROM tracking_updates 
            WHERE order_id = ? 
            ORDER BY timestamp DESC
        ''', (order_id,))
        
        tracking_rows = cursor.fetchall()
        tracking_columns = [desc[0] for desc in cursor.description]
        tracking_updates = [dict(zip(tracking_columns, row)) for row in tracking_rows]
        
        conn.close()
        
        # Calculate progress percentage
        status_progress = {
            'pending': 0,
            'picked_up': 20,
            'in_transit': 40,
            'out_for_delivery': 80,
            'delivered': 100,
            'failed': 0,
            'returned': 0
        }
        
        current_progress = status_progress.get(order_data['current_status'], 0)
        
        # Get latest location
        latest_location = None
        if tracking_updates:
            latest_update = tracking_updates[0]
            if latest_update['latitude'] and latest_update['longitude']:
                latest_location = {
                    'latitude': latest_update['latitude'],
                    'longitude': latest_update['longitude'],
                    'timestamp': latest_update['timestamp'],
                    'accuracy': latest_update['accuracy']
                }
        
        return {
            'order_details': order_data,
            'current_progress': current_progress,
            'latest_location': latest_location,
            'tracking_history': tracking_updates,
            'estimated_delivery': self.calculate_eta(order_id, 
                Location(latest_location['latitude'], latest_location['longitude'], 
                        datetime.now()) if latest_location else None)
        }
    
    def calculate_eta(self, order_id: str, current_location: Optional[Location]) -> Optional[datetime]:
        """Calculate estimated time of arrival based on current location and traffic"""
        if not current_location:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get delivery address coordinates (simplified - in reality, you'd geocode the address)
        cursor.execute('SELECT delivery_address FROM orders WHERE order_id = ?', (order_id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        # Simplified ETA calculation
        # In production, you'd use Google Maps API or similar for accurate routing
        base_travel_time = 30  # minutes
        traffic_factor = 1.2   # 20% delay for traffic
        
        eta = datetime.now() + timedelta(minutes=int(base_travel_time * traffic_factor))
        return eta
    
    def send_notification(self, order_id: str, notification_type: str, message: str):
        """Send notification to customer"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get customer contact info
        cursor.execute('''
            SELECT customer_email, customer_phone, customer_name 
            FROM orders WHERE order_id = ?
        ''', (order_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
        
        email, phone, name = result
        
        # Log notification
        if email:
            cursor.execute('''
                INSERT INTO notifications (order_id, notification_type, recipient, message)
                VALUES (?, ?, ?, ?)
            ''', (order_id, notification_type, email, message))
        
        if phone:
            cursor.execute('''
                INSERT INTO notifications (order_id, notification_type, recipient, message)
                VALUES (?, ?, ?, ?)
            ''', (order_id, notification_type, phone, message))
        
        conn.commit()
        conn.close()
        
        # Send actual notifications (email/SMS)
        if email:
            self.send_email_notification(email, name, order_id, message)
        if phone:
            self.send_sms_notification(phone, message)
    
    def send_status_notification(self, update: DeliveryUpdate):
        """Send status-specific notifications"""
        status_messages = {
            DeliveryStatus.PICKED_UP: "Your order has been picked up and is being prepared for delivery.",
            DeliveryStatus.IN_TRANSIT: "Your order is now in transit to the delivery location.",
            DeliveryStatus.OUT_FOR_DELIVERY: "Your order is out for delivery and will arrive soon!",
            DeliveryStatus.DELIVERED: "Your order has been successfully delivered. Thank you for your business!",
            DeliveryStatus.FAILED: "Delivery attempt failed. We will try again or contact you for rescheduling.",
            DeliveryStatus.RETURNED: "Your order has been returned to the sender. Please contact customer service."
        }
        
        message = status_messages.get(update.status, update.message)
        self.send_notification(update.order_id, f"status_{update.status.value}", message)
    
    def send_eta_notification(self, order_id: str, eta: datetime):
        """Send ETA notification to customer"""
        eta_str = eta.strftime("%I:%M %p")
        message = f"Your order is on the way! Estimated delivery time: {eta_str}"
        self.send_notification(order_id, "eta_update", message)
    
    def send_email_notification(self, email: str, name: str, order_id: str, message: str):
        """Send email notification (placeholder implementation)"""
        print(f"EMAIL TO {email}: Dear {name}, Order {order_id} - {message}")
        # In production, implement actual email sending with SMTP
    
    def send_sms_notification(self, phone: str, message: str):
        """Send SMS notification (placeholder implementation)"""
        print(f"SMS TO {phone}: {message}")
        # In production, implement actual SMS sending with provider API
    
    def get_delivery_analytics(self, date_range: Tuple[datetime, datetime]) -> Dict:
        """Generate delivery analytics for specified date range"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date, end_date = date_range
        
        # Overall statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_orders,
                COUNT(CASE WHEN current_status = 'delivered' THEN 1 END) as delivered_orders,
                COUNT(CASE WHEN current_status = 'failed' THEN 1 END) as failed_orders,
                AVG(CASE 
                    WHEN current_status = 'delivered' 
                    THEN (julianday(
                        (SELECT timestamp FROM tracking_updates 
                         WHERE order_id = orders.order_id AND status = 'delivered' 
                         ORDER BY timestamp DESC LIMIT 1)
                    ) - julianday(created_at)) * 24
                END) as avg_delivery_time_hours
            FROM orders 
            WHERE created_at BETWEEN ? AND ?
        ''', (start_date, end_date))
        
        stats = cursor.fetchone()
        
        # Status distribution
        cursor.execute('''
            SELECT current_status, COUNT(*) as count
            FROM orders 
            WHERE created_at BETWEEN ? AND ?
            GROUP BY current_status
        ''', (start_date, end_date))
        
        status_distribution = dict(cursor.fetchall())
        
        # Daily delivery trends
        cursor.execute('''
            SELECT 
                DATE(created_at) as delivery_date,
                COUNT(*) as orders_created,
                COUNT(CASE WHEN current_status = 'delivered' THEN 1 END) as orders_delivered
            FROM orders 
            WHERE created_at BETWEEN ? AND ?
            GROUP BY DATE(created_at)
            ORDER BY delivery_date
        ''', (start_date, end_date))
        
        daily_trends = [
            {
                'date': row[0],
                'orders_created': row[1],
                'orders_delivered': row[2]
            }
            for row in cursor.fetchall()
        ]
        
        # Driver performance
        cursor.execute('''
            SELECT 
                driver_id,
                COUNT(*) as total_deliveries,
                COUNT(CASE WHEN current_status = 'delivered' THEN 1 END) as successful_deliveries,
                AVG(CASE 
                    WHEN current_status = 'delivered' 
                    THEN (julianday(
                        (SELECT timestamp FROM tracking_updates 
                         WHERE order_id = orders.order_id AND status = 'delivered' 
                         ORDER BY timestamp DESC LIMIT 1)
                    ) - julianday(created_at)) * 24
                END) as avg_delivery_time_hours
            FROM orders 
            WHERE created_at BETWEEN ? AND driver_id IS NOT NULL
            GROUP BY driver_id
        ''', (start_date, end_date))
        
        driver_performance = [
            {
                'driver_id': row[0],
                'total_deliveries': row[1],
                'successful_deliveries': row[2],
                'success_rate': (row[2] / row[1] * 100) if row[1] > 0 else 0,
                'avg_delivery_time_hours': row[3] or 0
            }
            for row in cursor.fetchall()
        ]
        
        conn.close()
        
        total_orders, delivered_orders, failed_orders, avg_delivery_time = stats
        
        return {
            'summary': {
                'total_orders': total_orders or 0,
                'delivered_orders': delivered_orders or 0,
                'failed_orders': failed_orders or 0,
                'success_rate': (delivered_orders / total_orders * 100) if total_orders > 0 else 0,
                'avg_delivery_time_hours': avg_delivery_time or 0
            },
            'status_distribution': status_distribution,
            'daily_trends': daily_trends,
            'driver_performance': driver_performance
        }
    
    def simulate_delivery_journey(self, order_id: str, driver_id: str):
        """Simulate a complete delivery journey for testing"""
        # Simulate pickup
        pickup_location = Location(19.0760, 72.8777, datetime.now(), 5.0)  # Mumbai depot
        self.update_delivery_status(DeliveryUpdate(
            order_id=order_id,
            status=DeliveryStatus.PICKED_UP,
            location=pickup_location,
            message="Package picked up from depot",
            driver_id=driver_id
        ))
        
        time.sleep(2)  # Simulate time passage
        
        # Simulate in transit
        transit_location = Location(19.0896, 72.8656, datetime.now(), 8.0)  # Bandra
        self.update_delivery_status(DeliveryUpdate(
            order_id=order_id,
            status=DeliveryStatus.IN_TRANSIT,
            location=transit_location,
            message="Package is in transit",
            driver_id=driver_id,
            estimated_delivery_time=datetime.now() + timedelta(minutes=30)
        ))
        
        time.sleep(2)
        
        # Simulate out for delivery
        delivery_location = Location(19.0544, 72.8322, datetime.now(), 3.0)  # Churchgate
        self.update_delivery_status(DeliveryUpdate(
            order_id=order_id,
            status=DeliveryStatus.OUT_FOR_DELIVERY,
            location=delivery_location,
            message="Out for delivery - driver is nearby",
            driver_id=driver_id,
            estimated_delivery_time=datetime.now() + timedelta(minutes=10)
        ))
        
        time.sleep(2)
        
        # Simulate delivery
        final_location = Location(19.0544, 72.8322, datetime.now(), 2.0)
        self.update_delivery_status(DeliveryUpdate(
            order_id=order_id,
            status=DeliveryStatus.DELIVERED,
            location=final_location,
            message="Package successfully delivered",
            driver_id=driver_id
        ))

# Example usage and testing
def main():
    """Example implementation and testing of the tracking system"""
    
    # Initialize tracking system
    tracker = DeliveryTrackingSystem()
    
    # Create sample orders
    sample_orders = [
        {
            'order_id': 'ORD_001',
            'customer_id': 'CUST_001',
            'customer_name': 'Rajesh Kumar',
            'customer_email': 'rajesh@example.com',
            'customer_phone': '+91-9876543210',
            'pickup_address': 'Distribution Center, Mumbai',
            'delivery_address': 'Bandra West, Mumbai',
            'scheduled_delivery': datetime.now() + timedelta(hours=2),
            'driver_id': 'DRV_001',
            'vehicle_id': 'VEH_001'
        },
        {
            'order_id': 'ORD_002',
            'customer_id': 'CUST_002',
            'customer_name': 'Priya Sharma',
            'customer_email': 'priya@example.com',
            'customer_phone': '+91-9876543211',
            'pickup_address': 'Distribution Center, Mumbai',
            'delivery_address': 'Churchgate, Mumbai',
            'scheduled_delivery': datetime.now() + timedelta(hours=3),
            'driver_id': 'DRV_002',
            'vehicle_id': 'VEH_002'
        }
    ]
    
    # Create orders
    for order in sample_orders:
        tracker.create_order(order)
        print(f"Created order: {order['order_id']}")
    
    # Simulate delivery journeys
    print("\nSimulating delivery journeys...")
    tracker.simulate_delivery_journey('ORD_001', 'DRV_001')
    
    # Get tracking information
    print("\nTracking Information for ORD_001:")
    tracking_info = tracker.get_order_tracking('ORD_001')
    print(json.dumps(tracking_info, indent=2, default=str))
    
    # Generate analytics
    print("\nDelivery Analytics:")
    analytics = tracker.get_delivery_analytics((
        datetime.now() - timedelta(days=7),
        datetime.now()
    ))
    print(json.dumps(analytics, indent=2, default=str))
    
    return tracker

if __name__ == "__main__":
    tracking_system = main()