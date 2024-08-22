import re

total_connections = 0
successful_connections_count = 0
faulty_connections_count = 0

log_file = "mqtt_output.log"
faulty_connection_pattern = r'Client <unknown> disconnected due to protocol error'
successful_connection_pattern = r'New client connected from'

with open(log_file, 'r') as file:
    log_data = file.read()

chunks = log_data.split("mosquitto version 2.0.18 starting")

for i, chunk in enumerate(chunks):
    if not chunk.strip():
        continue

    chunk = "mosquitto version 2.0.18 starting" + chunk

    print(f"Processing chunk {i + 1}...\n{chunk}\n")

    # Search for faulty connections
    faulty_connections = re.findall(faulty_connection_pattern, chunk)
    successful_connections = re.findall(successful_connection_pattern, chunk)
    faulty_connections_count += len(faulty_connections)
    successful_connections_count += len(successful_connections)
    total_connections += len(faulty_connections) + len(successful_connections)

print(f"Total connections: {total_connections}")
print(f"Successful connections: {successful_connections_count}")
print(f"Unsuccessful connections: {faulty_connections_count}")
