import re
import matplotlib.pyplot as plt
from datetime import datetime

# Define the log file path
logfile_path = "mqtt_boofuzz_stdout.log"

# Initialize lists to store the timestamps of successful and failed connections
failed_timestamps = []
successful_timestamps = []

# Define regex patterns for successful and failed connections
success_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \d+: New client connected from .* as .*')
failure_pattern = re.compile(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \d+: Client .* disconnected due to protocol error\.')

# Open and read the log file
with open(logfile_path, "r") as logfile:
    for line in logfile:
        # Check for successful connections
        success_match = success_pattern.search(line)
        if success_match:
            timestamp_str = success_match.group(1)
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            successful_timestamps.append(timestamp)

        # Check for failed connections
        failure_match = failure_pattern.search(line)
        if failure_match:
            timestamp_str = failure_match.group(1)
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            failed_timestamps.append(timestamp)

# Sort the timestamps
successful_timestamps.sort()
failed_timestamps.sort()

# Combine timestamps for plotting
all_timestamps = sorted(set(successful_timestamps + failed_timestamps))

# Calculate cumulative totals
cumulative_successful = []
cumulative_failed = []
success_count = 0
fail_count = 0

for timestamp in all_timestamps:
    success_count += successful_timestamps.count(timestamp)
    fail_count += failed_timestamps.count(timestamp)
    cumulative_successful.append(success_count)
    cumulative_failed.append(fail_count)

# Plot the results
plt.figure(figsize=(10, 6))
plt.plot(all_timestamps, cumulative_failed, marker='o', color='red', linestyle='-', label='Cumulative Failed Connections')
plt.plot(all_timestamps, cumulative_successful, marker='o', color='green', linestyle='-', label='Cumulative Successful Connections')
plt.title('Evaluation of Connection success rate over time (boofuzz)')
plt.xlabel('Timestamp')
plt.ylabel('Number of Connections')
plt.xticks(rotation=45)
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()
