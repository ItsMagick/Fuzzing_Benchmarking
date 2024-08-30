import os
import socket
import subprocess
import time

import psutil
from boofuzz import *
import threading

MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1883
FIXED_TOPIC = "fuzzing/topic"  # Fixed topic that should not be fuzzed


def publisher_session():
    session = Session(target=Target(connection=SocketConnection(MQTT_BROKER_HOST, MQTT_BROKER_PORT, proto="tcp")))

    s_initialize("MQTT Connect")
    with s_block("Connect Header"):
        s_byte(0x10)  # MQTT Control Packet Type for CONNECT
    with s_block("Remaining Length"):
        s_byte(0x00, name="Remaining Length", fuzzable=True)
    s_size("Remaining Length", 1, 1, fuzzable=False)
    with s_block("Protocol Name Length"):
        s_bit_field(19, 2, name="Protocol Name Length", fuzzable=False)
    with s_block("Protocol Name"):
        s_string("MQTT", fuzzable=False)
        s_size("Protocol Name Length", 2, fuzzable=False, endian='big')

    s_byte(0x04, name="Protocol Version", fuzzable=False)

    with s_block("Connect Flags"):
        s_bit_field(0, 1, name="Reserved", fuzzable=False)
        s_bit_field(0, 1, name="Clean Session", fuzzable=True)
        s_bit_field(0, 1, name="Will Flag", fuzzable=True)
        s_bit_field(0, 2, name="Will QoS", fuzzable=True)
        s_bit_field(0, 1, name="Will Retain", fuzzable=True)
        s_bit_field(0, 1, name="Password Flag", fuzzable=True)
        s_bit_field(0, 1, name="Username Flag", fuzzable=True)

    s_word(60, name="Keep Alive", fuzzable=True)

    with s_block("Client Identifier"):
        s_string("ClientID", fuzzable=True)
        s_size("Client Identifier", 2, fuzzable=False, endian='big')

    session.connect(s_get("MQTT Connect"))

    # MQTT PUBLISH Packet
    s_initialize("MQTT Publish")
    with s_block("Publish Header"):
        s_byte(0x30)  # MQTT Control Packet Type for PUBLISH

    with s_block("Topic Name"):
        s_string(FIXED_TOPIC, fuzzable=False)
        s_size("Topic Name", 2, fuzzable=False, endian='big')

    s_string("Fuzzing Payload", name="Payload", fuzzable=True)  # Fuzz the payload

    session.connect(s_get("MQTT Publish"))

    # Start fuzzing
    session.fuzz()


def subscriber_session():
    session = Session(target=Target(connection=SocketConnection(MQTT_BROKER_HOST, MQTT_BROKER_PORT, proto="tcp")))

    with s_block("Connect Header"):
        s_byte(0x10)  # MQTT Control Packet Type for CONNECT

    with s_block("Protocol Name"):
        s_string("MQTT", fuzzable=False)

    s_byte(0x04, name="Protocol Level", fuzzable=False)

    with s_block("Connect Flags"):
        s_bit_field(0, 1, name="Reserved", fuzzable=False)
        s_bit_field(0, 1, name="Clean Session", fuzzable=True)
        s_bit_field(0, 1, name="Will Flag", fuzzable=True)
        s_bit_field(0, 2, name="Will QoS", fuzzable=True)
        s_bit_field(0, 1, name="Will Retain", fuzzable=True)
        s_bit_field(0, 1, name="Password Flag", fuzzable=True)
        s_bit_field(0, 1, name="Username Flag", fuzzable=True)

    s_word(60, name="Keep Alive", fuzzable=True)

    with s_block("Client Identifier"):
        s_string("ClientID_Subscriber", fuzzable=True)
        s_size("Client Identifier", 2, fuzzable=False, endian='big')

    session.connect(s_get("MQTT Connect"))
    s_initialize("MQTT Subscribe")
    with s_block("Subscribe Header"):
        s_byte(0x82)  # MQTT Control Packet Type for SUBSCRIBE

    s_word(1, name="Packet Identifier", fuzzable=True)

    with s_block("Topic Filters"):
        with s_block("Topic Filter"):
            s_string(FIXED_TOPIC, fuzzable=False)
            s_size("Topic Filter", 2, fuzzable=False, endian='big')
            s_byte(0x00, name="Requested QoS", fuzzable=True)

    session.connect(s_get("MQTT Subscribe"))

    session.fuzz()


def wait_for_ready_signal():
    ready_file = 'mosquitto_ready.signal'
    while not os.path.exists(ready_file):
        print("Waiting for Mosquitto broker to be ready...")
        time.sleep(1)  # Check every second

    print("Mosquitto broker is ready.")


def start_mosquitto_broker():
    terminal_command = [
        'gnome-terminal',
        '--',
        'bash', '-c',
        'bash scripts/capture_asan_messages.sh; exec bash'  # Run script and keep terminal open
    ]

    return subprocess.Popen(terminal_command)


def init_connection():
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


def monitor_broker(broker_process):
    while True:
        if broker_process.poll() is not None:
            print("Broker process terminated. Restarting...")
            broker_process = start_mosquitto_broker()

        time.sleep(5)


def kill_process(pid):
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


if __name__ == "__main__":
    try:
        session, broker_proc = init_connection()
        monitor_thread = threading.Thread(target=monitor_broker, args=(broker_proc,), daemon=True)
        # Run publisher and subscriber in parallel
        pub_thread = threading.Thread(target=publisher_session)
        sub_thread = threading.Thread(target=subscriber_session)

        pub_thread.start()
        sub_thread.start()

        pub_thread.join()
        sub_thread.join()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down and terminating procs...")
        pid = read_pid_from_file('pid_file.txt')
        if pid:
            kill_process(pid)
        exit(0)
