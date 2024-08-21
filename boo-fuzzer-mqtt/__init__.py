import socket
import subprocess
import threading
import time

import helpers
from boofuzz import Session, Target, TCPSocketConnection
from boofuzz import ProcessMonitor


def init_connection():
    """
    Initialize a session for the Fuzzer
    :return:
    """
    broker_proc = start_mosquitto_broker()

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


def start_mosquitto_broker():
    """
    Starts the Mosquitto broker.
    """
    return subprocess.Popen(['../binaries/mosquitto'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def monitor_broker(broker_process):
    """
    Keep the Mosquitto broker running, restarting it if it terminates.
    """
    while True:
        # Check if the broker process has terminated
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
        # Start the fuzzing session
        session.fuzz()
    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Shutting down and terminating procs...")
        broker_proc.terminate()
        exit(0)
