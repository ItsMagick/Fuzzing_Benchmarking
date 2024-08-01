import socket

from boofuzz import Session, Target, TCPSocketConnection
import helpers
import importlib.util
from pathlib import Path

"""
As structure of the binary protocol it is necessary to know how the messages are structured.
The binary protocol is implemented in the scripts/binary_protocol.py file.
The bytes are structured as follows:
    
    |  0x03  |   0x9A  | 0x00 0x00|  0x01  |   0x00  |   0x9E   |
    <Handler> <No idea> <Padding?> <Length> <Payload> <Checksum>
    
    1st Byte:         0x03, 0x02, 0x01, 0x00: Handlers where 0x00 stands for the general information request handler, 
                                                            0x01 for ??? handler,
                                                            0x02 for control handler that changes the state of the machine,
                                                            0x03 for the (specific-)information request handler
    2nd Byte:         No idea
    3rd & 4th Byte:   filled with 0x00, might be padding to fill a specified frame in the protocol
    5th Byte:         The length of the command in bytes
    6th - n-th Byte:  Semester Clubkarte: 1€The payload of the command (some of which are hardcoded and some are variable)
                        Note: The Payload has to be the same length as the length given in the 5th Byte 
                              but can also be 0 (no Byte)
    last Byte:        The checksum of the command that consists of the sum of all Bytes 
                      modulo 256(the last byte of the sum).

Each Command (Sequence of Bytes) terminates with a new line character ('\n')
"""


def import_binary_prot_module():
    """
    Import the binary_protocol.py file to not have to copy the code here.
    :return:
    """
    # Import the binary_protocol.py file
    script_dir = Path(__file__).parent.joinpath('..', '..', '..', 'scripts', 'binary_protocol.py').resolve()
    if not script_dir.is_file():
        raise FileNotFoundError(f"No file found at {script_dir}")
    spec = importlib.util.spec_from_file_location('binary_protocol', str(script_dir))
    if not script_dir.is_file():
        raise FileNotFoundError(f"No file found at {script_dir}")
    mymodule = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mymodule)
    return mymodule


def init_connection(binary_prot_module):
    """
    Initialize a session for the Fuzzer
    :param binary_prot_module:
    :return:
    """
    # can be replaced by binary_prot_module.ips for ALL Projectors
    ips = ['127.0.0.1', binary_prot_module.ip_new, binary_prot_module.ip_old]
    for ip in ips:
        try:
            sock = socket.socket()
            sock.settimeout(5)
            sock.connect((ip, binary_prot_module.PJ_CMD_PORT))
            return Session(target=Target(
                connection=TCPSocketConnection(ip, binary_prot_module.PJ_CMD_PORT)), sleep_time=0.03)
        except (ConnectionRefusedError, socket.timeout):
            print(f"Connection refused or timed out on {ip}")
            continue
    raise Exception("No connection could be established to any IP")


if __name__ == '__main__':
    module = import_binary_prot_module()
    session = init_connection(module)
    helpers.init_request_structure(session)
    # Start the fuzzing session
    session.fuzz()
