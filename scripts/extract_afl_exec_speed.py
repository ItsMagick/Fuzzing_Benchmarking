import os
import sys
import csv
from datetime import datetime


def extract_exec_speed(fuzzer_stats_path):
    exec_speed = None
    try:
        with open(fuzzer_stats_path, 'r') as f:
            for line in f:
                if line.startswith('execs_per_sec'):
                    exec_speed = float(line.strip().split(':')[1])
                    break
    except FileNotFoundError:
        print(f"File {fuzzer_stats_path} not found.")
    except Exception as e:
        print(f"Error reading file {fuzzer_stats_path}: {e}")
    return exec_speed


def log_exec_speed(csv_file, fuzzer_stats_path):
    # Check if the CSV file exists to determine if we need to write headers
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, 'a', newline='') as csvfile:
        fieldnames = ['timestamp', 'execs_per_sec']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write headers if the file doesn't exist
        if not file_exists:
            writer.writeheader()

        # Extract execution speed
        exec_speed = extract_exec_speed(fuzzer_stats_path)
        # Log the timestamp and execution speed if available
        if exec_speed is not None:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer.writerow({'timestamp': timestamp, 'execs_per_sec': exec_speed})
            print(f"{timestamp} - Execution Speed: {exec_speed} execs/sec")
        # Wait for the specified interval before checking again


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <afl_output_directory>")
        sys.exit(1)
    # Usage
    fuzzer_stats_path = sys.argv[1]
    csv_file = 'afl_exec_speed_log.csv'
    log_exec_speed(csv_file, fuzzer_stats_path)
