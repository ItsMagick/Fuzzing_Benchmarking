import datetime
import os.path
import sqlite3
import matplotlib.pyplot as plt

# TODO: Think of a way to get the current database path and get the data directly from the database as soon as the fuzzer
#  ends the campaign.

db_path = 'fuzz/net/fuzzer/boofuzz-results/run-2024-06-18T11-29-03.db'
if not os.path.isfile(db_path):
    raise FileNotFoundError(f"No file found at {db_path}")

conn = sqlite3.connect(db_path)


def get_timestamps():
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp FROM cases")
    # Fetch all rows from the query
    return cursor.fetchall()


def convert_timestamp_to_mills(timestamps: list):
    return [datetime.datetime.strptime(timestamp[0][1:-1],
                                       '%Y-%m-%d %H:%M:%S,%f') for timestamp in timestamps]


def calculate_exec_time(timestamps: list):
    datetime_objects = convert_timestamp_to_mills(timestamps)
    return [(datetime_objects[i + 1] - datetime_objects[i]).total_seconds() * 1000
            for i in range(len(datetime_objects) - 1)]


def calculate_exec_speeds():
    timestamps = get_timestamps()
    exec_times = calculate_exec_time(timestamps)
    return [1000 / execution_time for execution_time in exec_times]


def plot_exec_speeds():
    timestamps = get_timestamps()
    exec_times = calculate_exec_time(timestamps)
    exec_speeds = [1000 / execution_time for execution_time in exec_times]

    # Calculate the midpoints of each timestamp pair
    datetime_objects = convert_timestamp_to_mills(timestamps)
    midpoints = [(datetime_objects[i] + (datetime_objects[i + 1] - datetime_objects[i]) / 2)
                 for i in range(len(datetime_objects) - 1)]

    plt.plot(midpoints, exec_speeds)
    plt.ylabel('Execution Speed (Commands per Second)')
    plt.xlabel('Time')
    plt.title('Execution Speed Over Time')
    plt.savefig('fuzz/net/fuzzer/res/execution_speed_over_time.png')
    plt.show()


plot_exec_speeds()
conn.close()
