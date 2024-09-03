import datetime
import os.path
import sqlite3
import matplotlib.pyplot as plt

# TODO: Think of a way to get the current database path and get the data directly from the database as soon as the fuzzer
#  ends the campaign.

db_path = 'boofuzz-results/run-2024-08-30T17-14-45.db'
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


def calculate_average_exec_speed():
    timestamps = get_timestamps()
    exec_times = calculate_exec_time(timestamps)
    exec_speeds = [1000 / execution_time for execution_time in exec_times]
    average_exec_speed = sum(exec_speeds) / len(exec_speeds)
    return average_exec_speed


def plot_exec_speeds():
    timestamps = get_timestamps()
    exec_times = calculate_exec_time(timestamps)
    exec_speeds = [1000 / execution_time for execution_time in exec_times]

    filtered_exec_speeds = exec_speeds[::1000]

    # Calculate the midpoints of each timestamp pair
    datetime_objects = convert_timestamp_to_mills(timestamps)
    midpoints = [(datetime_objects[i] + (datetime_objects[i + 1] - datetime_objects[i]) / 2)
                 for i in range(len(datetime_objects) - 1)]
    filtered_midpoints = midpoints[::1000]

    plt.plot(filtered_midpoints, filtered_exec_speeds)
    plt.ylabel('Execution Speed (Commands per Second)')
    plt.xlabel('Time')
    plt.title('Execution Speed Over Time')
    plt.savefig('plots/execution_speed_boofuzz_normal.png')
    plt.show()



def plot_average_exec_speed_over_time():
    timestamps = get_timestamps()
    exec_times = calculate_exec_time(timestamps)
    exec_speeds = [1000 / execution_time for execution_time in exec_times]

    cumulative_exec_speeds = []
    cumulative_sum = 0
    for speed in exec_speeds:
        cumulative_sum += speed
        cumulative_exec_speeds.append(cumulative_sum)
    average_exec_speeds = [cumulative_exec_speeds[i] / (i + 1) for i in range(len(cumulative_exec_speeds))]

    datetime_objects = convert_timestamp_to_mills(timestamps)
    midpoints = [(datetime_objects[i] + (datetime_objects[i + 1] - datetime_objects[i]) / 2)
                 for i in range(len(datetime_objects) - 1)]
    overall_average_exec_speed = sum(exec_speeds) / len(exec_speeds)

    plt.plot(midpoints, average_exec_speeds)
    plt.ylabel('Average Execution Speed (Commands per Second)')
    plt.xlabel('Time')
    plt.title('Average Execution Speed Over Time')
    plt.figtext(0.5, 0.01, f"Overall Average Execution Speed: {overall_average_exec_speed:.2f} commands per second",
                ha='center', fontsize=12, bbox=dict(facecolor='white', alpha=0.8, edgecolor='black'))
    plt.savefig('plots/average_execution_speed_boofuzz_efficient.png')
    plt.show()

plot_average_exec_speed_over_time()
conn.close()
