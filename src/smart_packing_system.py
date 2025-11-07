import json
import math
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import heapq
from collections import defaultdict

class Priority(Enum):
    """Order priority levels"""
    URGENT = 1      # Same day delivery
    HIGH = 2        # Next day delivery
    NORMAL = 3      # Standard delivery
    LOW = 4         # Economy delivery

class PackageSize(Enum):
    """Package size categories"""
    SMALL = "small"     # < 1 kg, < 30cm
    MEDIUM = "medium"   # 1-5 kg, 30-60cm
    LARGE = "large"     # 5-20 kg, 60-100cm
    EXTRA_LARGE = "xl"  # > 20 kg, > 100cm

@dataclass
class Package:
    """Package information"""
    order_id: str
    customer_id: str
    weight: float  # in kg
    dimensions: Tuple[float, float, float]  # length, width, height in cm
    fragile: bool = False
    temperature_sensitive: bool = False
    hazardous: bool = False
    value: float = 0.0  # package value for insurance
    
    @property
    def volume(self) -> float:
        """Calculate package volume in cubic cm"""
        return self.dimensions[0] * self.dimensions[1] * self.dimensions[2]
    
    @property
    def size_category(self) -> PackageSize:
        """Determine package size category"""
        max_dimension = max(self.dimensions)
        if self.weight < 1 and max_dimension < 30:
            return PackageSize.SMALL
        elif self.weight < 5 and max_dimension < 60:
            return PackageSize.MEDIUM
        elif self.weight < 20 and max_dimension < 100:
            return PackageSize.LARGE
        else:
            return PackageSize.EXTRA_LARGE

@dataclass
class DeliveryOrder:
    """Complete delivery order information"""
    order_id: str
    customer_id: str
    customer_location: Tuple[float, float]  # lat, lng
    delivery_address: str
    priority: Priority
    time_window: Tuple[datetime, datetime]  # earliest, latest delivery time
    packages: List[Package]
    special_instructions: str = ""
    
    @property
    def total_weight(self) -> float:
        """Total weight of all packages in the order"""
        return sum(pkg.weight for pkg in self.packages)
    
    @property
    def total_volume(self) -> float:
        """Total volume of all packages in the order"""
        return sum(pkg.volume for pkg in self.packages)
    
    @property
    def requires_special_handling(self) -> bool:
        """Check if order requires special handling"""
        return any(pkg.fragile or pkg.temperature_sensitive or pkg.hazardous 
                  for pkg in self.packages)

@dataclass
class Vehicle:
    """Delivery vehicle information"""
    vehicle_id: str
    capacity_weight: float  # max weight in kg
    capacity_volume: float  # max volume in cubic cm
    driver_id: str
    current_location: Tuple[float, float]
    available_from: datetime
    special_equipment: List[str]  # e.g., "refrigeration", "fragile_handling"
    
    def can_handle_order(self, order: DeliveryOrder) -> bool:
        """Check if vehicle can handle the order"""
        if order.total_weight > self.capacity_weight:
            return False
        if order.total_volume > self.capacity_volume:
            return False
        
        # Check special handling requirements
        if order.requires_special_handling:
            for pkg in order.packages:
                if pkg.temperature_sensitive and "refrigeration" not in self.special_equipment:
                    return False
                if pkg.fragile and "fragile_handling" not in self.special_equipment:
                    return False
                if pkg.hazardous and "hazardous_handling" not in self.special_equipment:
                    return False
        
        return True

class SmartPackingSystem:
    """Intelligent packing and loading optimization system"""
    
    def __init__(self, depot_location: Tuple[float, float]):
        self.depot_location = depot_location
        self.orders = []
        self.vehicles = []
        self.packing_plans = []
        
    def add_order(self, order: DeliveryOrder):
        """Add a delivery order to the system"""
        self.orders.append(order)
    
    def add_vehicle(self, vehicle: Vehicle):
        """Add a delivery vehicle to the system"""
        self.vehicles.append(vehicle)
    
    def calculate_distance(self, loc1: Tuple[float, float], loc2: Tuple[float, float]) -> float:
        """Calculate Haversine distance between two coordinates"""
        lat1, lon1 = loc1
        lat2, lon2 = loc2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Earth's radius in kilometers
        
        return c * r
    
    def create_geographical_clusters(self, orders: List[DeliveryOrder], max_cluster_size: int = 8) -> List[List[DeliveryOrder]]:
        """Create geographical clusters of orders for efficient routing"""
        if not orders:
            return []
        
        clusters = []
        remaining_orders = orders.copy()
        
        while remaining_orders:
            # Start new cluster with the order closest to depot
            distances_to_depot = [
                (self.calculate_distance(self.depot_location, order.customer_location), order)
                for order in remaining_orders
            ]
            distances_to_depot.sort()
            
            cluster = [distances_to_depot[0][1]]
            remaining_orders.remove(distances_to_depot[0][1])
            
            # Add nearby orders to the cluster
            while len(cluster) < max_cluster_size and remaining_orders:
                cluster_center = self._calculate_cluster_center(cluster)
                
                # Find closest order to cluster center
                closest_order = None
                min_distance = float('inf')
                
                for order in remaining_orders:
                    distance = self.calculate_distance(cluster_center, order.customer_location)
                    if distance < min_distance:
                        min_distance = distance
                        closest_order = order
                
                if closest_order and min_distance < 10:  # Within 10km radius
                    cluster.append(closest_order)
                    remaining_orders.remove(closest_order)
                else:
                    break
            
            clusters.append(cluster)
        
        return clusters
    
    def _calculate_cluster_center(self, cluster: List[DeliveryOrder]) -> Tuple[float, float]:
        """Calculate the geographical center of a cluster"""
        if not cluster:
            return self.depot_location
        
        avg_lat = sum(order.customer_location[0] for order in cluster) / len(cluster)
        avg_lng = sum(order.customer_location[1] for order in cluster) / len(cluster)
        
        return (avg_lat, avg_lng)
    
    def optimize_loading_sequence(self, orders: List[DeliveryOrder]) -> List[DeliveryOrder]:
        """Optimize the loading sequence for a set of orders"""
        # Priority-based sorting with multiple criteria
        def sort_key(order: DeliveryOrder):
            priority_weight = order.priority.value
            
            # Time window urgency (earlier deadlines first)
            time_urgency = order.time_window[1].timestamp()
            
            # Distance from depot (closer deliveries loaded last for easy access)
            distance_from_depot = self.calculate_distance(
                self.depot_location, order.customer_location
            )
            
            # Package handling complexity (fragile/special items loaded carefully)
            handling_complexity = sum(
                1 for pkg in order.packages 
                if pkg.fragile or pkg.temperature_sensitive or pkg.hazardous
            )
            
            # Size and weight (heavier items loaded first, at the bottom)
            size_weight = order.total_weight + (order.total_volume / 1000)  # Normalize volume
            
            return (
                priority_weight,           # Primary: Priority
                time_urgency,             # Secondary: Time urgency
                -size_weight,             # Tertiary: Heavier items first (negative for reverse)
                handling_complexity,      # Quaternary: Special handling
                distance_from_depot       # Quinary: Distance (closer last)
            )
        
        return sorted(orders, key=sort_key)
    
    def create_loading_plan(self, vehicle: Vehicle, orders: List[DeliveryOrder]) -> Dict:
        """Create detailed loading plan for a vehicle"""
        # Filter orders that can be handled by this vehicle
        compatible_orders = [order for order in orders if vehicle.can_handle_order(order)]
        
        # Optimize loading sequence
        optimized_orders = self.optimize_loading_sequence(compatible_orders)
        
        # Create detailed loading instructions
        loading_plan = {
            'vehicle_id': vehicle.vehicle_id,
            'driver_id': vehicle.driver_id,
            'total_orders': len(optimized_orders),
            'total_weight': sum(order.total_weight for order in optimized_orders),
            'total_volume': sum(order.total_volume for order in optimized_orders),
            'capacity_utilization': {
                'weight': sum(order.total_weight for order in optimized_orders) / vehicle.capacity_weight * 100,
                'volume': sum(order.total_volume for order in optimized_orders) / vehicle.capacity_volume * 100
            },
            'loading_sequence': [],
            'special_instructions': []
        }
        
        # Generate loading sequence with detailed instructions
        current_weight = 0
        current_volume = 0
        
        for i, order in enumerate(optimized_orders):
            current_weight += order.total_weight
            current_volume += order.total_volume
            
            # Determine loading zone based on delivery sequence
            loading_zone = self._determine_loading_zone(i, len(optimized_orders))
            
            # Create package-level instructions
            package_instructions = []
            for pkg in order.packages:
                instruction = {
                    'package_id': f"{order.order_id}_{pkg.order_id}",
                    'weight': pkg.weight,
                    'dimensions': pkg.dimensions,
                    'handling': self._get_handling_instructions(pkg)
                }
                package_instructions.append(instruction)
            
            loading_instruction = {
                'sequence': i + 1,
                'order_id': order.order_id,
                'customer_id': order.customer_id,
                'delivery_address': order.delivery_address,
                'priority': order.priority.name,
                'time_window': f"{order.time_window[0].strftime('%H:%M')} - {order.time_window[1].strftime('%H:%M')}",
                'loading_zone': loading_zone,
                'total_packages': len(order.packages),
                'order_weight': order.total_weight,
                'order_volume': order.total_volume,
                'packages': package_instructions,
                'cumulative_weight': current_weight,
                'cumulative_volume': current_volume,
                'special_requirements': order.special_instructions
            }
            
            loading_plan['loading_sequence'].append(loading_instruction)
            
            # Add special instructions if needed
            if order.requires_special_handling:
                loading_plan['special_instructions'].append(
                    f"Order {order.order_id}: {self._get_special_handling_note(order)}"
                )
        
        return loading_plan
    
    def _determine_loading_zone(self, sequence: int, total_orders: int) -> str:
        """Determine optimal loading zone based on delivery sequence"""
        # Last third of deliveries go in front (easy access)
        if sequence >= total_orders * 2 // 3:
            return "FRONT"
        # Middle third goes in middle
        elif sequence >= total_orders // 3:
            return "MIDDLE"
        # First third goes in back (delivered last)
        else:
            return "BACK"
    
    def _get_handling_instructions(self, package: Package) -> List[str]:
        """Generate handling instructions for a package"""
        instructions = []
        
        if package.fragile:
            instructions.append("FRAGILE - Handle with care")
        if package.temperature_sensitive:
            instructions.append("TEMPERATURE SENSITIVE - Keep cool")
        if package.hazardous:
            instructions.append("HAZARDOUS - Follow safety protocols")
        if package.weight > 20:
            instructions.append("HEAVY - Use proper lifting technique")
        if max(package.dimensions) > 100:
            instructions.append("OVERSIZED - May require team lift")
        
        return instructions
    
    def _get_special_handling_note(self, order: DeliveryOrder) -> str:
        """Generate special handling note for an order"""
        notes = []
        
        for pkg in order.packages:
            if pkg.fragile:
                notes.append("Contains fragile items")
            if pkg.temperature_sensitive:
                notes.append("Requires temperature control")
            if pkg.hazardous:
                notes.append("Contains hazardous materials")
        
        return "; ".join(set(notes))  # Remove duplicates
    
    def generate_master_packing_plan(self) -> Dict:
        """Generate complete packing plan for all orders and vehicles"""
        # Sort orders by priority and time constraints
        sorted_orders = sorted(self.orders, key=lambda x: (x.priority.value, x.time_window[1]))
        
        # Create geographical clusters
        clusters = self.create_geographical_clusters(sorted_orders)
        
        # Assign vehicles to clusters
        vehicle_assignments = []
        unassigned_orders = []
        
        # Sort vehicles by capacity (largest first for efficiency)
        sorted_vehicles = sorted(self.vehicles, key=lambda v: v.capacity_weight, reverse=True)
        
        for cluster_idx, cluster in enumerate(clusters):
            best_vehicle = None
            best_utilization = 0
            
            # Find best vehicle for this cluster
            for vehicle in sorted_vehicles:
                if vehicle in [va['vehicle'] for va in vehicle_assignments]:
                    continue  # Vehicle already assigned
                
                compatible_orders = [order for order in cluster if vehicle.can_handle_order(order)]
                if not compatible_orders:
                    continue
                
                # Calculate utilization efficiency
                total_weight = sum(order.total_weight for order in compatible_orders)
                total_volume = sum(order.total_volume for order in compatible_orders)
                
                weight_util = total_weight / vehicle.capacity_weight
                volume_util = total_volume / vehicle.capacity_volume
                
                # Prefer balanced utilization
                utilization_score = min(weight_util, volume_util) * 100
                
                if utilization_score > best_utilization and utilization_score <= 100:
                    best_utilization = utilization_score
                    best_vehicle = vehicle
            
            if best_vehicle:
                compatible_orders = [order for order in cluster if best_vehicle.can_handle_order(order)]
                loading_plan = self.create_loading_plan(best_vehicle, compatible_orders)
                
                vehicle_assignments.append({
                    'cluster_id': f"CLUSTER_{cluster_idx + 1}",
                    'vehicle': best_vehicle,
                    'orders': compatible_orders,
                    'loading_plan': loading_plan
                })
            else:
                # No suitable vehicle found, add to unassigned
                unassigned_orders.extend(cluster)
        
        # Generate summary statistics
        total_orders = len(self.orders)
        assigned_orders = sum(len(va['orders']) for va in vehicle_assignments)
        
        master_plan = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_orders': total_orders,
                'assigned_orders': assigned_orders,
                'unassigned_orders': len(unassigned_orders),
                'assignment_rate': (assigned_orders / total_orders * 100) if total_orders > 0 else 0,
                'total_vehicles_used': len(vehicle_assignments),
                'total_vehicles_available': len(self.vehicles)
            },
            'vehicle_assignments': [],
            'unassigned_orders': [order.order_id for order in unassigned_orders],
            'optimization_metrics': self._calculate_optimization_metrics(vehicle_assignments)
        }
        
        # Add detailed vehicle assignments
        for assignment in vehicle_assignments:
            assignment_detail = {
                'cluster_id': assignment['cluster_id'],
                'vehicle_id': assignment['vehicle'].vehicle_id,
                'driver_id': assignment['vehicle'].driver_id,
                'vehicle_capacity': {
                    'weight': assignment['vehicle'].capacity_weight,
                    'volume': assignment['vehicle'].capacity_volume
                },
                'assigned_orders_count': len(assignment['orders']),
                'loading_plan': assignment['loading_plan'],
                'route_optimization': self._generate_route_suggestions(assignment['orders'])
            }
            master_plan['vehicle_assignments'].append(assignment_detail)
        
        self.packing_plans = master_plan
        return master_plan
    
    def _calculate_optimization_metrics(self, vehicle_assignments: List[Dict]) -> Dict:
        """Calculate optimization metrics for the packing plan"""
        if not vehicle_assignments:
            return {}
        
        total_capacity_weight = sum(va['vehicle'].capacity_weight for va in vehicle_assignments)
        total_capacity_volume = sum(va['vehicle'].capacity_volume for va in vehicle_assignments)
        
        total_used_weight = sum(
            sum(order.total_weight for order in va['orders']) 
            for va in vehicle_assignments
        )
        total_used_volume = sum(
            sum(order.total_volume for order in va['orders']) 
            for va in vehicle_assignments
        )
        
        # Calculate priority distribution
        priority_distribution = defaultdict(int)
        for va in vehicle_assignments:
            for order in va['orders']:
                priority_distribution[order.priority.name] += 1
        
        # Calculate average distance per route
        avg_distances = []
        for va in vehicle_assignments:
            if va['orders']:
                distances = [
                    self.calculate_distance(self.depot_location, order.customer_location)
                    for order in va['orders']
                ]
                avg_distances.append(sum(distances) / len(distances))
        
        return {
            'capacity_utilization': {
                'weight_percentage': (total_used_weight / total_capacity_weight * 100) if total_capacity_weight > 0 else 0,
                'volume_percentage': (total_used_volume / total_capacity_volume * 100) if total_capacity_volume > 0 else 0
            },
            'priority_distribution': dict(priority_distribution),
            'average_delivery_distance_km': sum(avg_distances) / len(avg_distances) if avg_distances else 0,
            'load_balancing_score': self._calculate_load_balance_score(vehicle_assignments)
        }
    
    def _calculate_load_balance_score(self, vehicle_assignments: List[Dict]) -> float:
        """Calculate how balanced the load distribution is across vehicles"""
        if not vehicle_assignments:
            return 0
        
        utilizations = []
        for va in vehicle_assignments:
            total_weight = sum(order.total_weight for order in va['orders'])
            utilization = total_weight / va['vehicle'].capacity_weight
            utilizations.append(utilization)
        
        # Calculate coefficient of variation (lower is better balanced)
        if len(utilizations) < 2:
            return 100
        
        mean_util = sum(utilizations) / len(utilizations)
        variance = sum((u - mean_util) ** 2 for u in utilizations) / len(utilizations)
        std_dev = math.sqrt(variance)
        
        cv = (std_dev / mean_util) if mean_util > 0 else 0
        
        # Convert to score (100 = perfect balance, 0 = very unbalanced)
        balance_score = max(0, 100 - (cv * 100))
        return balance_score
    
    def _generate_route_suggestions(self, orders: List[DeliveryOrder]) -> Dict:
        """Generate route optimization suggestions for a set of orders"""
        if not orders:
            return {}
        
        # Calculate total distance if delivered in current order
        current_distance = 0
        current_location = self.depot_location
        
        for order in orders:
            current_distance += self.calculate_distance(current_location, order.customer_location)
            current_location = order.customer_location
        
        # Add return to depot
        current_distance += self.calculate_distance(current_location, self.depot_location)
        
        # Simple nearest neighbor optimization
        optimized_order = self._nearest_neighbor_route(orders)
        optimized_distance = 0
        current_location = self.depot_location
        
        for order in optimized_order:
            optimized_distance += self.calculate_distance(current_location, order.customer_location)
            current_location = order.customer_location
        
        optimized_distance += self.calculate_distance(current_location, self.depot_location)
        
        return {
            'original_sequence': [order.order_id for order in orders],
            'optimized_sequence': [order.order_id for order in optimized_order],
            'distance_improvement': {
                'original_km': current_distance,
                'optimized_km': optimized_distance,
                'savings_km': current_distance - optimized_distance,
                'improvement_percentage': ((current_distance - optimized_distance) / current_distance * 100) if current_distance > 0 else 0
            },
            'estimated_time_savings_minutes': (current_distance - optimized_distance) * 2  # Assume 2 min per km
        }
    
    def _nearest_neighbor_route(self, orders: List[DeliveryOrder]) -> List[DeliveryOrder]:
        """Simple nearest neighbor algorithm for route optimization"""
        if not orders:
            return []
        
        unvisited = orders.copy()
        route = []
        current_location = self.depot_location
        
        while unvisited:
            nearest_order = min(
                unvisited,
                key=lambda order: self.calculate_distance(current_location, order.customer_location)
            )
            
            route.append(nearest_order)
            unvisited.remove(nearest_order)
            current_location = nearest_order.customer_location
        
        return route
    
    def export_loading_instructions(self, format_type: str = "detailed") -> str:
        """Export loading instructions in various formats"""
        if not self.packing_plans:
            self.generate_master_packing_plan()
        
        if format_type == "detailed":
            return self._export_detailed_instructions()
        elif format_type == "summary":
            return self._export_summary_instructions()
        elif format_type == "driver_sheet":
            return self._export_driver_sheets()
        else:
            return json.dumps(self.packing_plans, indent=2, default=str)
    
    def _export_detailed_instructions(self) -> str:
        """Export detailed loading instructions"""
        instructions = []
        instructions.append("=== SMART PACKING SYSTEM - DETAILED LOADING INSTRUCTIONS ===")
        instructions.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        instructions.append(f"Total Orders: {self.packing_plans['summary']['total_orders']}")
        instructions.append(f"Assignment Rate: {self.packing_plans['summary']['assignment_rate']:.1f}%")
        instructions.append("")
        
        for assignment in self.packing_plans['vehicle_assignments']:
            instructions.append(f"VEHICLE: {assignment['vehicle_id']} | DRIVER: {assignment['driver_id']}")
            instructions.append(f"Cluster: {assignment['cluster_id']}")
            instructions.append(f"Orders: {assignment['assigned_orders_count']}")
            instructions.append("")
            
            loading_plan = assignment['loading_plan']
            instructions.append("LOADING SEQUENCE:")
            instructions.append("-" * 80)
            
            for seq in loading_plan['loading_sequence']:
                instructions.append(f"{seq['sequence']:2d}. ORDER {seq['order_id']} - {seq['customer_id']}")
                instructions.append(f"    Priority: {seq['priority']} | Zone: {seq['loading_zone']}")
                instructions.append(f"    Time Window: {seq['time_window']}")
                instructions.append(f"    Weight: {seq['order_weight']:.1f}kg | Volume: {seq['order_volume']:.0f}cm³")
                instructions.append(f"    Packages: {seq['total_packages']}")
                
                for pkg in seq['packages']:
                    instructions.append(f"      - {pkg['package_id']}: {pkg['weight']:.1f}kg")
                    if pkg['handling']:
                        instructions.append(f"        Instructions: {', '.join(pkg['handling'])}")
                
                if seq['special_requirements']:
                    instructions.append(f"    Special: {seq['special_requirements']}")
                instructions.append("")
            
            # Add capacity utilization
            util = loading_plan['capacity_utilization']
            instructions.append(f"CAPACITY UTILIZATION:")
            instructions.append(f"Weight: {util['weight']:.1f}% | Volume: {util['volume']:.1f}%")
            instructions.append("")
            
            # Add route optimization
            route_opt = assignment['route_optimization']
            if route_opt:
                instructions.append(f"ROUTE OPTIMIZATION:")
                instructions.append(f"Distance Savings: {route_opt['distance_improvement']['savings_km']:.1f}km")
                instructions.append(f"Time Savings: {route_opt['estimated_time_savings_minutes']:.0f} minutes")
                instructions.append("")
            
            instructions.append("=" * 80)
            instructions.append("")
        
        if self.packing_plans['unassigned_orders']:
            instructions.append("UNASSIGNED ORDERS:")
            for order_id in self.packing_plans['unassigned_orders']:
                instructions.append(f"- {order_id}")
            instructions.append("")
        
        return "\n".join(instructions)
    
    def _export_summary_instructions(self) -> str:
        """Export summary loading instructions"""
        summary = []
        summary.append("=== PACKING SUMMARY REPORT ===")
        summary.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        summary.append("")
        
        metrics = self.packing_plans['optimization_metrics']
        summary.append(f"Total Orders Processed: {self.packing_plans['summary']['total_orders']}")
        summary.append(f"Assignment Success Rate: {self.packing_plans['summary']['assignment_rate']:.1f}%")
        summary.append(f"Vehicles Utilized: {self.packing_plans['summary']['total_vehicles_used']}")
        summary.append(f"Average Capacity Utilization: {metrics.get('capacity_utilization', {}).get('weight_percentage', 0):.1f}%")
        summary.append(f"Load Balance Score: {metrics.get('load_balancing_score', 0):.1f}/100")
        summary.append("")
        
        summary.append("PRIORITY DISTRIBUTION:")
        priority_dist = metrics.get('priority_distribution', {})
        for priority, count in priority_dist.items():
            summary.append(f"  {priority}: {count} orders")
        summary.append("")
        
        return "\n".join(summary)
    
    def _export_driver_sheets(self) -> str:
        """Export individual driver instruction sheets"""
        sheets = []
        
        for assignment in self.packing_plans['vehicle_assignments']:
            sheet = []
            sheet.append(f"DRIVER LOADING SHEET")
            sheet.append(f"Driver: {assignment['driver_id']}")
            sheet.append(f"Vehicle: {assignment['vehicle_id']}")
            sheet.append(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            sheet.append("")
            
            loading_plan = assignment['loading_plan']
            sheet.append("LOADING CHECKLIST:")
            
            for seq in loading_plan['loading_sequence']:
                sheet.append(f"☐ {seq['sequence']}. {seq['order_id']} → {seq['loading_zone']}")
                sheet.append(f"    Packages: {seq['total_packages']} | Weight: {seq['order_weight']:.1f}kg")
                
                special_handling = []
                for pkg in seq['packages']:
                    if pkg['handling']:
                        special_handling.extend(pkg['handling'])
                
                if special_handling:
                    sheet.append(f"    ⚠️  {', '.join(set(special_handling))}")
                sheet.append("")
            
            sheet.append("FINAL CHECK:")
            sheet.append("☐ All packages loaded according to sequence")
            sheet.append("☐ Heavy items at bottom, fragile items secure")
            sheet.append("☐ Easy access items loaded last")
            sheet.append("☐ All special handling requirements met")
            sheet.append("")
            sheet.append("Driver Signature: _________________ Time: _______")
            sheet.append("")
            sheet.append("-" * 50)
            sheet.append("")
            
            sheets.extend(sheet)
        
        return "\n".join(sheets)

# Example usage and testing
def main():
    """Example implementation of the smart packing system"""
    
    # Initialize the system
    packing_system = SmartPackingSystem(depot_location=(19.0760, 72.8777))  # Mumbai
    
    # Add sample vehicles
    vehicles = [
        Vehicle(
            vehicle_id="VEH_001",
            capacity_weight=1000,  # 1000 kg
            capacity_volume=10000000,  # 10 cubic meters in cm³
            driver_id="DRV_001",
            current_location=(19.0760, 72.8777),
            available_from=datetime.now(),
            special_equipment=["fragile_handling", "refrigeration"]
        ),
        Vehicle(
            vehicle_id="VEH_002",
            capacity_weight=750,
            capacity_volume=7500000,
            driver_id="DRV_002",
            current_location=(19.0760, 72.8777),
            available_from=datetime.now(),
            special_equipment=["fragile_handling"]
        ),
        Vehicle(
            vehicle_id="VEH_003",
            capacity_weight=500,
            capacity_volume=5000000,
            driver_id="DRV_003",
            current_location=(19.0760, 72.8777),
            available_from=datetime.now(),
            special_equipment=["hazardous_handling"]
        )
    ]
    
    for vehicle in vehicles:
        packing_system.add_vehicle(vehicle)
    
    # Add sample orders with packages
    sample_orders = [
        DeliveryOrder(
            order_id="ORD_001",
            customer_id="CUST_001",
            customer_location=(19.0896, 72.8656),  # Bandra
            delivery_address="Bandra West, Mumbai",
            priority=Priority.URGENT,
            time_window=(datetime.now() + timedelta(hours=2), datetime.now() + timedelta(hours=4)),
            packages=[
                Package("PKG_001", "CUST_001", 5.0, (30, 20, 15), fragile=True),
                Package("PKG_002", "CUST_001", 2.5, (25, 15, 10))
            ]
        ),
        DeliveryOrder(
            order_id="ORD_002",
            customer_id="CUST_002",
            customer_location=(19.0544, 72.8322),  # Churchgate
            delivery_address="Churchgate, Mumbai",
            priority=Priority.HIGH,
            time_window=(datetime.now() + timedelta(hours=3), datetime.now() + timedelta(hours=6)),
            packages=[
                Package("PKG_003", "CUST_002", 15.0, (50, 40, 30)),
                Package("PKG_004", "CUST_002", 8.0, (35, 25, 20), temperature_sensitive=True)
            ]
        ),
        DeliveryOrder(
            order_id="ORD_003",
            customer_id="CUST_003",
            customer_location=(19.1136, 72.8697),  # Andheri
            delivery_address="Andheri West, Mumbai",
            priority=Priority.NORMAL,
            time_window=(datetime.now() + timedelta(hours=4), datetime.now() + timedelta(hours=8)),
            packages=[
                Package("PKG_005", "CUST_003", 3.0, (20, 15, 10)),
                Package("PKG_006", "CUST_003", 12.0, (45, 35, 25), fragile=True)
            ]
        )
    ]
    
    for order in sample_orders:
        packing_system.add_order(order)
    
    # Generate master packing plan
    print("Generating smart packing plan...")
    master_plan = packing_system.generate_master_packing_plan()
    
    # Export detailed instructions
    detailed_instructions = packing_system.export_loading_instructions("detailed")
    print(detailed_instructions)
    
    # Export summary
    summary = packing_system.export_loading_instructions("summary")
    print("\n" + "="*60)
    print(summary)
    
    return packing_system, master_plan

if __name__ == "__main__":
    system, plan = main()
