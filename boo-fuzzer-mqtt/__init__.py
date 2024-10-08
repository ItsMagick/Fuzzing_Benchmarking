import os
import socket
import subprocess
import threading
import time

import psutil

import helpers
from boofuzz import Session, Target, TCPSocketConnection
from boofuzz import ProcessMonitor


def init_connection():
    """
    Initialize a session for the Fuzzer
    :return:
    """
    broker_proc = start_mosquitto_broker()

    wait_for_ready_signal()
    ip = '127.0.0.1'
    mqtt_port = 1883
    ProcessMonitor(host=ip, port=mqtt_port)
    target = Target(connection=TCPSocketConnection(ip, mqtt_port))
    try:
        sock = socket.socket()
        sock.settimeout(10)
        sock.connect((ip, mqtt_port))
        return Session(target=target), broker_proc
    except (ConnectionRefusedError, socket.timeout):
        print(f"Connection refused or timed out on {ip} with port {mqtt_port}")
    raise Exception("No connection could be established to any IP")


def wait_for_ready_signal():
    """
    Wait for the Mosquitto broker to signal that it is ready.
    """
    ready_file = 'mosquitto_ready.signal'
    while not os.path.exists(ready_file):
        print("Waiting for Mosquitto broker to be ready...")
        time.sleep(1)  # Check every second

    print("Mosquitto broker is ready.")


def start_mosquitto_broker():
    """
    Starts the Mosquitto broker.
    """
    terminal_command = [
        'gnome-terminal',
        '--',
        'bash', '-c',
        'bash scripts/capture_asan_messages.sh; exec bash'  # Run script and keep terminal open
    ]

    # Launch the terminal with the command
    return subprocess.Popen(terminal_command)


def kill_process(pid):
    """
    Terminate a process with the given PID.
    """
    try:
        process = psutil.Process(pid)
        process.terminate()  # Terminate the process gracefully
        process.wait()  # Wait for the process to terminate
        print(f"Process {pid} terminated gracefully.")
    except psutil.NoSuchProcess:
        print(f"No such process with PID {pid}.")
    except psutil.AccessDenied:
        print(f"Permission denied to terminate process with PID {pid}.")
    except Exception as e:
        print(f"Error: {e}")


def read_pid_from_file(pid_file):
    """
    Read the PID from the given file.
    :param pid_file: Path to the file containing the PID.
    :return: The PID read from the file.
    """
    try:
        with open(pid_file, 'r') as file:
            pid = int(file.read().strip())
        return pid
    except FileNotFoundError:
        print(f"PID file {pid_file} not found.")
        return None
    except ValueError:
        print(f"Invalid PID value in {pid_file}.")
        return None


def monitor_broker(broker_process):
    """
    Keep the Mosquitto broker running, restarting it if it terminates.
    """
    while True:
        if broker_process.poll() is not None:
            print("Broker process terminated. Restarting...")
            broker_process = start_mosquitto_broker()

        time.sleep(5)


if __name__ == '__main__':
    try:
        session, broker_proc = init_connection()
        print("Connection established")
        monitor_thread = threading.Thread(target=monitor_broker, args=(broker_proc,), daemon=True)
        monitor_thread.start()
        helpers.init_structure(session)
        session.fuzz()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down and terminating procs...")
        pid = read_pid_from_file('pid_file.txt')
        if pid:
            kill_process(pid)
        exit(0)
