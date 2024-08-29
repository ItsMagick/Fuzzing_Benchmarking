import re
from datetime import datetime
import matplotlib.pyplot as plt
from collections import defaultdict

faulty_patterns = [
    r'\[(.*?)\] .*: Client .* disconnected due to malformed packet.',
    r'\[(.*?)\] .*: Client .* disconnected due to protocol error.',
    r'\[(.*?)\] .*: Bad Client .* sending multiple CONNECT messages.'
]
successful_pattern = r'\[(.*?)\] .*: Reused message ID .* from .* detected\. Clearing from storage\.'


def extract_connections(log_file_path):
    with open(log_file_path, 'r') as file:
        content = file.read()

    # Split the content into chunks
    chunks = re.split(r'mosquitto version 2.0.18 starting.', content)

    timestamp_counts = defaultdict(lambda: {'successful': 0, 'faulty': 0})

    last_timestamp = None
    running_counts = {'successful': 0, 'faulty': 0}

    for chunk in chunks:
        if chunk.strip() == "":
            continue

        for line in chunk.splitlines():
            timestamp_match = re.search(r'\[(.*?)\]', line)
            if timestamp_match:
                timestamp = timestamp_match.group(1)
                if last_timestamp is not None and timestamp != last_timestamp:
                    timestamp_counts[last_timestamp] = running_counts.copy()

                for pattern in faulty_patterns:
                    if re.search(pattern, line):
                        running_counts['faulty'] += 1
                        break

                    else:
                        running_counts['successful'] += 1
                last_timestamp = timestamp

    if last_timestamp:
        timestamp_counts[last_timestamp] = running_counts

    return timestamp_counts


def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')


# Plotting function
def plot_connections(timestamp_counts):
    # Prepare data
    timestamps = sorted(timestamp_counts.keys())
    successful_counts = [timestamp_counts[t]['successful'] for t in timestamps]
    faulty_counts = [timestamp_counts[t]['faulty'] for t in timestamps]

    times = [parse_timestamp(t) for t in timestamps]

    # Create the plot
    plt.figure(figsize=(12, 6))

    plt.plot(times, successful_counts, marker='o', color='g', linestyle='-', label='Successful Connections')
    plt.plot(times, faulty_counts, marker='x', color='r', linestyle='-', label='Faulty Connections')

    plt.xlabel('Timestamp')
    plt.ylabel('Number of Connections')
    plt.title('Connections Over Time')
    plt.legend()
    plt.grid(True)

    # Format x-axis to show timestamps in human-readable form
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gca().xaxis.set_major_locator(plt.matplotlib.dates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    plt.tight_layout()
    plt.show()


# Example usage
log_file_path = 'lesser_log.log'
timestamp_counts = extract_connections(log_file_path)
plot_connections(timestamp_counts)
