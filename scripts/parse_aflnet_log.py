import re
import os
import matplotlib.pyplot as plt
from datetime import datetime

# Define the path to the log file in the parent directory
log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "lesser_log.log")

# Define the faulty connection patterns
faulty_connection_pattern1 = r'\[(.*?)\] .*: Client .* disconnected due to malformed packet.'
faulty_connection_pattern2 = r'\[(.*?)\] .*: Client .* disconnected due to protocol error.'
faulty_connection_pattern3 = r'\[(.*?)\] .*: Bad Client .* sending multiple CONNECT messages.'

# Define the successful connection pattern
successful_connection_pattern = r'\[(.*?)\] .*: Reused message ID .* from .* detected\. Clearing from storage\.'

# List to hold all faulty patterns
faulty_patterns = [faulty_connection_pattern1, faulty_connection_pattern2, faulty_connection_pattern3]

# Initialize dictionaries to hold timestamps and connection counts
success_count = {}
failure_count = {}

# Read the log file with Latin-1 encoding
with open(log_file_path, 'r', encoding='latin-1') as file:
    log_data = file.read()

# Split the log data into chunks using "mosquitto version 2.0.18 starting" as the delimiter
chunks = log_data.split("mosquitto version 2.0.18 starting")

# Process each chunk to determine if it contains a failure or a success
for chunk in chunks:
    if not chunk.strip():
        continue  # Skip empty chunks

    # Find the first timestamp in the chunk
    timestamp_match = re.search(r'\[(.*?)\]', chunk)
    if timestamp_match:
        timestamp = datetime.strptime(timestamp_match.group(1), '%Y-%m-%d %H:%M:%S')

        # Assume success, but this will change if an error is found
        connection_success = True

        # Check if any of the faulty patterns are found in this chunk
        for pattern in faulty_patterns:
            if re.search(pattern, chunk):
                # If a failure is found, increment the failure count for this timestamp
                failure_count[timestamp] = failure_count.get(timestamp, 0) + 1
                connection_success = False
                break  # No need to check further if an error is found

        # If no errors were found, check for success pattern and increment the success count
        if connection_success and re.search(successful_connection_pattern, chunk):
            success_count[timestamp] = success_count.get(timestamp, 0) + 1

# Convert dictionaries to sorted lists of tuples (timestamp, count)
sorted_success = sorted(success_count.items())
sorted_failure = sorted(failure_count.items())

# Separate the data into timestamps and counts for plotting
success_times, success_values = zip(*sorted_success) if sorted_success else ([], [])
failure_times, failure_values = zip(*sorted_failure) if sorted_failure else ([], [])

# Plotting the number of successful connections over time
plt.figure(figsize=(12, 8))

# Plot for Successful Connections
plt.subplot(2, 1, 1)  # 2 rows, 1 column, first plot
plt.plot(success_times, success_values, 'g-', label='Successful Connections')
plt.title('Rate of Successful Connections Over Time')
plt.xlabel('Time')
plt.ylabel('Number of Successful Connections')
plt.gcf().autofmt_xdate()  # Format the x-axis for timestamps
plt.legend()

# Plot for Failed Connections
plt.subplot(2, 1, 2)  # 2 rows, 1 column, second plot
plt.plot(failure_times, failure_values, 'r-', label='Failed Connections')
plt.title('Rate of Failed Connections Over Time')
plt.xlabel('Time')
plt.ylabel('Number of Failed Connections')
plt.gcf().autofmt_xdate()  # Format the x-axis for timestamps
plt.legend()

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plots
plt.show()
