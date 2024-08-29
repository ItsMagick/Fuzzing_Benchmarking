import re
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

faulty_connection_pattern1 = r'\[(.*?)\] .*: Client .* disconnected due to malformed packet.'
faulty_connection_pattern2 = r'\[(.*?)\] .*: Client .* disconnected due to protocol error.'


def extract_and_aggregate_fail_states(log_file_path):
    with open(log_file_path, 'r', encoding='latin-1') as file:
        content = file.read()

    chunks = re.split(r'\n.*mosquitto version 2.0.18 starting.*\n', content)

    cumulative_counts = {
        'Malformed Packet': [],
        'Protocol Error': [],
        'Timestamps': []
    }

    malformed_count = 0
    protocol_error_count = 0

    for chunk in chunks:
        if chunk.strip() == "":
            continue

        timestamp_match = re.search(r'\[(.*?)\]', chunk)
        if timestamp_match:
            chunk_start_time = timestamp_match.group(1)
            cumulative_counts['Timestamps'].append(parse_timestamp(chunk_start_time))

            if re.search(faulty_connection_pattern1, chunk):
                malformed_count += 1
            if re.search(faulty_connection_pattern2, chunk):
                protocol_error_count += 1

            cumulative_counts['Malformed Packet'].append(malformed_count)
            cumulative_counts['Protocol Error'].append(protocol_error_count)

    return cumulative_counts


def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')


def plot_fail_states(cumulative_counts):
    timestamps = cumulative_counts['Timestamps']
    malformed_packet_counts = cumulative_counts['Malformed Packet']
    protocol_error_counts = cumulative_counts['Protocol Error']

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.plot(timestamps, malformed_packet_counts, marker='o', color='r', linestyle='-', label='Malformed Packet')
    ax.plot(timestamps, protocol_error_counts, marker='x', color='b', linestyle='--', label='Protocol Error')

    ax.set_xlabel('Timestamp')
    ax.set_ylabel('Total Number of Errors')
    ax.set_title('Cumulative Error Counts Over Time')
    ax.legend()
    ax.grid(True)

    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    ax.xaxis.set_major_locator(plt.matplotlib.dates.AutoDateLocator())
    plt.gcf().autofmt_xdate()

    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.ticklabel_format(style='plain', axis='y')

    total_malformed = malformed_packet_counts[-1] if malformed_packet_counts else 0
    total_protocol_error = protocol_error_counts[-1] if protocol_error_counts else 0

    fig.text(0.5, 0.05, (
        f"Total Malformed Packet Errors: {total_malformed}; "
        f"Total Protocol Error Failures: {total_protocol_error}; "
        f"Total Errors: {total_malformed + total_protocol_error}"
    ), fontsize=12, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'),
             transform=fig.transFigure)

    plt.subplots_adjust(bottom=0.3)
    plt.show()


# Example usage
log_file_path = 'mqtt_aflnet_stdout.log'
cumulative_counts = extract_and_aggregate_fail_states(log_file_path)
plot_fail_states(cumulative_counts)
