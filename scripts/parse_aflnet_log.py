import re
import os

total_connections = 0
successful_connections_count = 0
faulty_connections_count = 0

log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mqtt_output.log")
successful_connection_pattern = r'New client connected from'

with open(log_file_path, 'r') as file:
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

# TODO: Das skript wurde geschrieben um die Anzahl der Fehlerhaften und Erfolgreichen Verbindungen zu zählen um sie
#  abhängig von timestamps zu analysieren.
#  Behauptung: AFLNets fehlerrate sinkt mit der Zeit
#  Statistik machen wie effizient/WAHRSCHEINLICH es ist, dass die Mutation des Inputs zu einem (nutzlosen) Fehler führt
#  -> Wie effizient ist AFLNets Erkennung von Wichtigen Bits/bytes?