import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

# Define a flexible pattern for successful connections
successful_connection_pattern = (r'\[.*?\] \d+: New client connected from \d+\.\d+\.\d+\.\d+:\d+ as .+ \(p\d+, c\d+, '
                                 r'k\d+\)\.')


# Function to extract and evaluate successful and unsuccessful connections
def extract_connections(log_file_path):
    with open(log_file_path, 'r', encoding="latin-1") as file:
        content = file.read()

    # Split the content into chunks
    chunks = re.split(r'\n.*mosquitto version 2.0.18 starting.*\n', content)

    # Store timestamps, cumulative success counts, and unsuccessful counts
    timestamp_cumulative_success = {}
    timestamp_cumulative_unsuccessful = {}

    cumulative_success = 0
    cumulative_unsuccessful = 0

    for chunk in chunks:
        if chunk.strip() == "":
            continue

        # Extract timestamp of the chunk
        timestamp_match = re.search(r'\[(.*?)\]', chunk)
        if timestamp_match:
            chunk_start_time = timestamp_match.group(1)

            # Check for successful connection messages in the chunk
            successful_messages = re.findall(successful_connection_pattern, chunk)
            new_successes = len(successful_messages)

            if new_successes > 0:
                cumulative_success += new_successes
                timestamp_cumulative_success[chunk_start_time] = cumulative_success
                timestamp_cumulative_unsuccessful[chunk_start_time] = cumulative_unsuccessful
            else:
                cumulative_unsuccessful += 1
                timestamp_cumulative_success[chunk_start_time] = cumulative_success
                timestamp_cumulative_unsuccessful[chunk_start_time] = cumulative_unsuccessful

    # Calculate total connections
    total_connections = cumulative_success + cumulative_unsuccessful

    return (timestamp_cumulative_success, timestamp_cumulative_unsuccessful, total_connections, cumulative_success,
            cumulative_unsuccessful)


# Convert timestamp to datetime object
def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')


# Plotting function
def plot_connections(cumulative_success, cumulative_unsuccessful, total_connections, successful_connections,
                     unsuccessful_connections):
    # Prepare data
    timestamps_success = sorted(cumulative_success.keys())
    success_counts = [cumulative_success[t] for t in timestamps_success]

    timestamps_unsuccessful = sorted(cumulative_unsuccessful.keys())
    unsuccessful_counts = [cumulative_unsuccessful[t] for t in timestamps_unsuccessful]

    # Convert timestamps to datetime objects
    times_success = [parse_timestamp(t) for t in timestamps_success]
    times_unsuccessful = [parse_timestamp(t) for t in timestamps_unsuccessful]

    # Create the plot
    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(times_success, success_counts, marker='o', color='g', linestyle='-',
            label='Cumulative Successful Connections')
    ax.plot(times_unsuccessful, unsuccessful_counts, marker='x', color='r', linestyle='--',
            label='Cumulative Unsuccessful Connections')

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Number of Connections')
    ax.set_title('Successful and Unsuccessful Connections Over Time')
    ax.legend()
    ax.grid(True)

    # Format x-axis to show timestamps in human-readable form
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.AutoDateLocator())
    plt.gcf().autofmt_xdate()  # Rotate date labels for better readability

    # Set y-axis to display whole numbers and avoid scientific notation
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ticklabel_format(style='plain', axis='y')  # Turn off scientific notation

    # Add text annotations for summary statistics using figtext
    fig.text(0.5, 0.05,
             f"Total Connections: {total_connections}; "
             f"Successful Connections: {successful_connections}; "
             f"Unsuccessful Connections: {unsuccessful_connections}"
             , fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'),
             transform=fig.transFigure)

    # Adjust layout to make space for text
    plt.subplots_adjust(bottom=0.3)  # Increase bottom margin to accommodate text
    plt.show()


# Example usage
log_file_path = 'mqtt_aflnet_stdout.log'
cumulative_success, cumulative_unsuccessful, total_connections, successful_connections, unsuccessful_connections \
    = extract_connections(log_file_path)
plot_connections(cumulative_success, cumulative_unsuccessful, total_connections, successful_connections,
                 unsuccessful_connections)
