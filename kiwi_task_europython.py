# Initialize an empty graph as a dictionary
import csv
from datetime import datetime, timedelta
import argparse

graph = {}
MIN_LAYOVER_MINUTES = 60
MAX_LAYOVER_MINUTES = 360 

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description='Takes arguments from the user and handles it')
# Add positional arguments (in this case, 'csv_file' and 'arg1' and 'arg2')
parser.add_argument('csv_file', help='Path to the CSV file')
parser.add_argument('origin', help='Origin Airport')
parser.add_argument('destination', help='Final Destination')

# Add optional arguments (in this case, '--bags' and '--return')
parser.add_argument('--bags', type=int, default=0, help='Number of bags')
parser.add_argument('--return', action='store_true', help='Include --return flag')

# Parse the command line arguments
args = parser.parse_args()
# Now, you can access the arguments in separate variables
CSV_FILE = args.csv_file
ORIGIN = args.origin.upper()
DESTINATION = args.destination.upper()
NUM_BAGS = args.bags

# print(CSV_FILE)
# print(ORIGIN)
# print(DESTINATION)
# print(NUM_BAGS)

def read_csv_into_graph():
    with open(CSV_FILE, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        # Read the CSV file and populate the graph below
        for row in csv_reader:
            origin = row['origin']
            destination = row['destination']
            # Create nodes for origin and destination if they don't exist
            if origin not in graph:
                graph[origin] = []
            if destination not in graph:
                graph[destination] = []

            # Create an edge between origin and destination
            flight_info = {
                'flight_no': row['flight_no'],
                'departure': row['departure'],
                'arrival': row['arrival'],
                'base_price': float(row['base_price']),
                'bag_price': int(row['bag_price']),
                'bags_allowed': int(row['bags_allowed'])
            }
            graph[origin].append((destination, flight_info))

# Print the graph
def print_graph():
    """ Optional if you want to print the graph """
    for airport, flights in graph.items():
        print(f'Airport: {airport}')
        for destination, flight_info in flights:
            print(f'  -> Destination: {destination}')
            print(f'     Flight No: {flight_info["flight_no"]}')
            print(f'     Departure: {flight_info["departure"]}')
            print(f'     Arrival: {flight_info["arrival"]}')
            print(f'     Base Price: {flight_info["base_price"]}')
            print(f'     Bag Price: {flight_info["bag_price"]}')
            print(f'     Bags Allowed: {flight_info["bags_allowed"]}')
            print("\n")

def calculate_total_price(flight_combination, num_bags):
    if isinstance(flight_combination, dict):
        total_price = flight_combination['base_price'] + num_bags * flight_combination['bag_price']
    else:
        min_bags_allowed = min(flight['bags_allowed'] for flight in flight_combination)
        # Calculate the bag price for each flight based on the minimum bags_allowed
        total_bag_price = sum(flight['bag_price'] * flight['bags_allowed'] for flight in flight_combination)
        # Calculate the total price
        total_price = sum(connecting_flight['base_price']  for connecting_flight in flight_combination) + total_bag_price
    return total_price

def calculate_total_hours(flight_combination):
    if isinstance(flight_combination, dict):
        start_time = datetime.strptime(flight_combination['departure'], "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(flight_combination['arrival'], "%Y-%m-%dT%H:%M:%S")
        total_hours = end_time - start_time
    else:
        total_travel_time = timedelta()  
        start_time = datetime.strptime(flight_combination[0]['departure'], "%Y-%m-%dT%H:%M:%S")
        end_time = datetime.strptime(flight_combination[-1]['arrival'], "%Y-%m-%dT%H:%M:%S")
        flight_travel_time = end_time - start_time
        return str(flight_travel_time)
    return str(total_hours)

def print_direct_flights(direct_flights):
    for flight_info in direct_flights:
        print(f"Flight: {flight_info['flight_no']}")
        print(f"Departure: {flight_info['departure']}")
        print(f"Arrival: {flight_info['arrival']}")
        print(f"Base Price: {flight_info['base_price']}")
        print(f"Bag Price: {flight_info['bag_price']}")
        print(f"Bags Allowed: {flight_info['bags_allowed']}")


def find_valid_connecting_flights(graph, start, end, min_layover_minutes, max_layover_minutes):
    direct_flights = []
    connecting_flights = []

    if start in graph and end in graph:
        for destination, flight_info_list in graph[start]:
                flight_info_list['origin'] = start
                flight_info_list['destination'] = destination
                
                if destination == end:
                    flight_info_list['destination'] = destination
                    direct_flights.append((flight_info_list))
                else:
                    arrival_time = datetime.strptime(flight_info_list['arrival'], "%Y-%m-%dT%H:%M:%S")
                    for next_destination, next_flight_info_list in graph.get(destination, []):
                        next_departure_time = datetime.strptime(next_flight_info_list['departure'], "%Y-%m-%dT%H:%M:%S")
                        next_flight_info_list['origin'] = destination
                        next_flight_info_list['destination'] = next_destination
                        layover = (next_departure_time - arrival_time).total_seconds() / 60
                        if next_destination == end and min_layover_minutes <= layover <= max_layover_minutes:
                            connecting_flights.append((flight_info_list, next_flight_info_list))

    return direct_flights, connecting_flights

read_csv_into_graph()
# print_graph() 
direct_flights, connecting_flights = find_valid_connecting_flights(graph, ORIGIN, DESTINATION, MIN_LAYOVER_MINUTES, MAX_LAYOVER_MINUTES)

if direct_flights:
    print(f"flights found {ORIGIN} to {DESTINATION}:")
    # print_direct_flights(direct_flights)

else:
    print(f"Nothing found, please recheck your {ORIGIN} and/or {DESTINATION}.")

full_flights = []
# Loop through the current data and convert it to the format needed
for more_flights in connecting_flights:
    flights = []
    for flight_data in more_flights:
        flight = {
            "flight_no": flight_data["flight_no"],
            "origin": flight_data["origin"],
            "destination": flight_data["destination"],
            "departure": flight_data["departure"],
            "arrival": flight_data["arrival"],
            "base_price": float(flight_data["base_price"]), 
            "bag_price": float(flight_data["bag_price"]),   
            "bags_allowed": int(flight_data["bags_allowed"]) 
        }
        flights.append(flight)
    # Create the final dictionary with the "flights" list
    full_flights.append(flights)

# doing the same as above but for direct_flights (This could have been better)
direct_flights_list = []
for flight_data in direct_flights:
    flight = {
            "flight_no": flight_data["flight_no"],
            "origin": flight_data["origin"],
            "destination": flight_data["destination"],
            "departure": flight_data["departure"],
            "arrival": flight_data["arrival"],
            "base_price": float(flight_data["base_price"]), 
            "bag_price": float(flight_data["bag_price"]), 
            "bags_allowed": int(flight_data["bags_allowed"])
            }
    direct_flights_list.append(flight)

final_connecting_list = []

for i in range(len(full_flights)):
    final_dict = {"flights": full_flights[i], 
                  "bags_allowed": full_flights[i][0]['bags_allowed'],  
                  "bags_count": NUM_BAGS,
                  "destination": DESTINATION,
                  "origin": full_flights[i][0]['origin'],
                  "total_price": calculate_total_price(full_flights[i], min(NUM_BAGS,full_flights[i][0]['bags_allowed'])),
                  "travel_time": calculate_total_hours(full_flights[i]) }
    final_connecting_list.append(final_dict)

final_direct_list = []
for i in range(len(direct_flights_list)):
    final_dict = {"flights": direct_flights_list[i], 
                  "bags_allowed":  direct_flights_list[i]['bags_allowed'],  
                  "bags_count": NUM_BAGS,
                  "destination": direct_flights_list[i]['destination'],
                  "origin": direct_flights_list[i]['origin'],
                  "total_price": calculate_total_price(direct_flights_list[i], min(NUM_BAGS,direct_flights_list[i]['bags_allowed'])),
                  "travel_time": calculate_total_hours(direct_flights_list[i])}
    final_direct_list.append(final_dict)

# Combine both lists into a single list
all_flights = final_direct_list + final_connecting_list

def sort_by_total_price(flight):
    return flight['total_price']  # Using the total_price of the connecting flight
# Sort the combined list based on 'total_price'
sorted_flights = sorted(all_flights, key=sort_by_total_price)

# Print the sorted list of flights (Final output)
for flight in sorted_flights:
    print(flight)

    