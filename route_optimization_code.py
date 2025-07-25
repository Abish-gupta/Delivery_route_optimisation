import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import math
import random

class DeliveryOptimizer:
    """
    Advanced Route Optimization System for Delivery Management
    Solves Vehicle Routing Problem (VRP) with time windows and capacity constraints
    """
    
    def __init__(self, depot_location: Tuple[float, float], vehicle_capacity: int = 50):
        self.depot = depot_location
        self.vehicle_capacity = vehicle_capacity
        self.customers = []
        self.distance_matrix = None
        self.optimized_routes = []
        
    def add_customer(self, customer_id: str, location: Tuple[float, float], 
                    time_window: Tuple[int, int], service_time: int, demand: int):
        """Add customer with location, time window, service time, and demand"""
        customer = {
            'id': customer_id,
            'location': location,
            'time_window': time_window,
            'service_time': service_time,
            'demand': demand,
            'lat': location[0],
            'lng': location[1]
        }
        self.customers.append(customer)
    
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
    
    def build_distance_matrix(self):
        """Build distance matrix for all locations including depot"""
        all_locations = [self.depot] + [c['location'] for c in self.customers]
        n = len(all_locations)
        self.distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    self.distance_matrix[i][j] = self.calculate_distance(
                        all_locations[i], all_locations[j]
                    )
    
    def nearest_neighbor_heuristic(self) -> List[List[int]]:
        """Nearest Neighbor algorithm for initial route construction"""
        unvisited = list(range(1, len(self.customers) + 1))  # Customer indices (depot is 0)
        routes = []
        
        while unvisited:
            route = [0]  # Start from depot
            current_location = 0
            current_capacity = 0
            current_time = 0
            
            while unvisited:
                # Find nearest unvisited customer that fits constraints
                best_customer = None
                min_distance = float('inf')
                
                for customer_idx in unvisited:
                    customer = self.customers[customer_idx - 1]
                    
                    # Check capacity constraint
                    if current_capacity + customer['demand'] > self.vehicle_capacity:
                        continue
                    
                    # Check time window constraint
                    travel_time = self.distance_matrix[current_location][customer_idx] * 2  # Assume 2 min per km
                    arrival_time = current_time + travel_time
                    
                    if arrival_time > customer['time_window'][1]:  # Too late
                        continue
                    
                    # Calculate distance
                    distance = self.distance_matrix[current_location][customer_idx]
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_customer = customer_idx
                
                if best_customer is None:
                    break  # No more customers can be added to this route
                
                # Add customer to route
                route.append(best_customer)
                unvisited.remove(best_customer)
                current_location = best_customer
                current_capacity += self.customers[best_customer - 1]['demand']
                
                # Update time
                travel_time = min_distance * 2
                arrival_time = current_time + travel_time
                service_start = max(arrival_time, self.customers[best_customer - 1]['time_window'][0])
                current_time = service_start + self.customers[best_customer - 1]['service_time']
            
            route.append(0)  # Return to depot
            routes.append(route)
        
        return routes
    
    def calculate_route_cost(self, route: List[int]) -> float:
        """Calculate total cost (distance + time penalty) for a route"""
        total_distance = 0
        time_penalty = 0
        current_time = 0
        
        for i in range(len(route) - 1):
            from_idx = route[i]
            to_idx = route[i + 1]
            
            # Add travel distance
            distance = self.distance_matrix[from_idx][to_idx]
            total_distance += distance
            
            # Update time and calculate penalties
            if to_idx != 0:  # Not returning to depot
                travel_time = distance * 2  # 2 minutes per km
                current_time += travel_time
                
                customer = self.customers[to_idx - 1]
                earliest, latest = customer['time_window']
                
                if current_time < earliest:
                    current_time = earliest  # Wait
                elif current_time > latest:
                    time_penalty += (current_time - latest) * 10  # Penalty for lateness
                
                current_time += customer['service_time']
        
        return total_distance + time_penalty
    
    def optimize_with_genetic_algorithm(self, generations: int = 100, population_size: int = 50):
        """Genetic Algorithm for route optimization"""
        if not self.distance_matrix.any():
            self.build_distance_matrix()
        
        # Generate initial population
        population = []
        for _ in range(population_size):
            routes = self.nearest_neighbor_heuristic()
            population.append(routes)
        
        best_solution = None
        best_cost = float('inf')
        
        for generation in range(generations):
            # Evaluate fitness
            fitness_scores = []
            for individual in population:
                total_cost = sum(self.calculate_route_cost(route) for route in individual)
                fitness_scores.append(1 / (1 + total_cost))  # Higher fitness for lower cost
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_solution = individual.copy()
            
            # Selection and crossover
            new_population = []
            for _ in range(population_size):
                # Tournament selection
                parent1 = self.tournament_selection(population, fitness_scores)
                parent2 = self.tournament_selection(population, fitness_scores)
                
                # Crossover and mutation
                child = self.crossover(parent1, parent2)
                child = self.mutate(child)
                new_population.append(child)
            
            population = new_population
        
        self.optimized_routes = best_solution
        return best_solution, best_cost
    
    def tournament_selection(self, population, fitness_scores, tournament_size=3):
        """Tournament selection for genetic algorithm"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        best_idx = max(tournament_indices, key=lambda i: fitness_scores[i])
        return population[best_idx]
    
    def crossover(self, parent1, parent2):
        """Order crossover for route optimization"""
        # Simplified crossover - in practice, this would be more sophisticated
        if random.random() < 0.8:  # Crossover probability
            # Select random route from each parent
            if parent1 and parent2:
                route1 = random.choice(parent1)
                route2 = random.choice(parent2)
                # Simple combination
                return [route1, route2]
        return parent1.copy()
    
    def mutate(self, individual, mutation_rate=0.1):
        """Mutation operator for genetic algorithm"""
        if random.random() < mutation_rate:
            for route in individual:
                if len(route) > 3:  # Has customers (not just depot-depot)
                    # Swap two customers in the route
                    i, j = random.sample(range(1, len(route)-1), 2)
                    route[i], route[j] = route[j], route[i]
        return individual
    
    def generate_delivery_schedule(self) -> Dict:
        """Generate detailed delivery schedule with times and instructions"""
        if not self.optimized_routes:
            self.optimize_with_genetic_algorithm()
        
        schedule = {
            'routes': [],
            'summary': {
                'total_routes': len(self.optimized_routes),
                'total_distance': 0,
                'total_customers': len(self.customers),
                'estimated_completion_time': 0
            }
        }
        
        for route_idx, route in enumerate(self.optimized_routes):
            route_info = {
                'route_id': f"ROUTE_{route_idx + 1}",
                'vehicle_id': f"VEH_{route_idx + 1}",
                'stops': [],
                'total_distance': self.calculate_route_cost(route),
                'total_demand': 0,
                'estimated_duration': 0
            }
            
            current_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
            
            for i, location_idx in enumerate(route):
                if location_idx == 0:  # Depot
                    stop_info = {
                        'stop_number': i,
                        'location': 'DEPOT',
                        'address': 'Distribution Center',
                        'coordinates': self.depot,
                        'arrival_time': current_time.strftime("%H:%M"),
                        'departure_time': (current_time + timedelta(minutes=15)).strftime("%H:%M"),
                        'activity': 'Load/Unload' if i == 0 else 'Return'
                    }
                else:  # Customer
                    customer = self.customers[location_idx - 1]
                    route_info['total_demand'] += customer['demand']
                    
                    stop_info = {
                        'stop_number': i,
                        'customer_id': customer['id'],
                        'address': f"Customer {customer['id']} Location",
                        'coordinates': customer['location'],
                        'arrival_time': current_time.strftime("%H:%M"),
                        'departure_time': (current_time + timedelta(minutes=customer['service_time'])).strftime("%H:%M"),
                        'time_window': f"{customer['time_window'][0]:02d}:00 - {customer['time_window'][1]:02d}:00",
                        'demand': customer['demand'],
                        'activity': 'Delivery'
                    }
                    current_time += timedelta(minutes=customer['service_time'])
                
                route_info['stops'].append(stop_info)
                
                # Add travel time to next stop
                if i < len(route) - 1:
                    next_idx = route[i + 1]
                    travel_time = self.distance_matrix[location_idx][next_idx] * 2
                    current_time += timedelta(minutes=travel_time)
            
            route_info['estimated_duration'] = (current_time - datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)).total_seconds() / 3600
            schedule['routes'].append(route_info)
            schedule['summary']['total_distance'] += route_info['total_distance']
        
        schedule['summary']['estimated_completion_time'] = max(route['estimated_duration'] for route in schedule['routes'])
        
        return schedule
    
    def export_to_gps_format(self, filename: str = "optimized_routes.csv"):
        """Export routes to GPS-compatible CSV format"""
        schedule = self.generate_delivery_schedule()
        
        gps_data = []
        for route in schedule['routes']:
            for stop in route['stops']:
                gps_data.append({
                    'Route_ID': route['route_id'],
                    'Vehicle_ID': route['vehicle_id'],
                    'Stop_Number': stop['stop_number'],
                    'Customer_ID': stop.get('customer_id', 'DEPOT'),
                    'Latitude': stop['coordinates'][0],
                    'Longitude': stop['coordinates'][1],
                    'Arrival_Time': stop['arrival_time'],
                    'Departure_Time': stop['departure_time'],
                    'Activity': stop['activity'],
                    'Demand': stop.get('demand', 0)
                })
        
        df = pd.DataFrame(gps_data)
        df.to_csv(filename, index=False)
        print(f"Routes exported to {filename}")
        
        return df

# Example Usage
def main():
    """Example implementation of the delivery optimization system"""
    
    # Initialize optimizer with depot location (Mumbai coordinates)
    optimizer = DeliveryOptimizer(depot_location=(19.0760, 72.8777), vehicle_capacity=30)
    
    # Add sample customers with Mumbai area coordinates
    customers_data = [
        ("CUST_001", (19.0896, 72.8656), (9, 12), 15, 5),   # Bandra
        ("CUST_002", (19.0544, 72.8322), (10, 14), 20, 8),  # Churchgate
        ("CUST_003", (19.1136, 72.8697), (11, 15), 10, 3),  # Andheri
        ("CUST_004", (19.0176, 72.8562), (9, 13), 25, 12),  # Colaba
        ("CUST_005", (19.0330, 72.8903), (12, 16), 18, 7),  # Powai
        ("CUST_006", (19.1197, 72.9046), (10, 14), 12, 4),  # Malad
        ("CUST_007", (18.9750, 72.8258), (13, 17), 30, 15), # Worli
        ("CUST_008", (19.0284, 72.8980), (11, 15), 22, 9),  # Vikhroli
    ]
    
    for customer_data in customers_data:
        optimizer.add_customer(*customer_data)
    
    # Optimize routes
    print("Optimizing delivery routes...")
    best_routes, best_cost = optimizer.optimize_with_genetic_algorithm(generations=50)
    
    # Generate schedule
    schedule = optimizer.generate_delivery_schedule()
    
    # Print results
    print(f"\nOptimization Complete!")
    print(f"Total Routes: {schedule['summary']['total_routes']}")
    print(f"Total Distance: {schedule['summary']['total_distance']:.2f} km")
    print(f"Estimated Completion Time: {schedule['summary']['estimated_completion_time']:.2f} hours")
    
    # Export to GPS format
    gps_data = optimizer.export_to_gps_format("mumbai_delivery_routes.csv")
    
    return optimizer, schedule

if __name__ == "__main__":
    optimizer, schedule = main()