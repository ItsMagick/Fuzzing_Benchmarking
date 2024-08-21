from boofuzz import *


def init_request_structure(session):
    """
    Initialize the request structure for the fuzzer
    :param session:
    :return:
    """
    # Initialize the request structure
    request = session.connect("mqtt", request_template="mqtt")
    # Add the request structure
    request.add_header(name="header", value=b"\x10", fuzzable=False)
    request.add_header(name="length", value=b"\x00", fuzzable=True)
    request.add_header(name="client_id", value=b"\x00", fuzzable=True)
    request.add_header(name="topic", value=b"\x00", fuzzable=True)
    request.add_header(name="message", value=b"\x00", fuzzable=True)
    request.add_header(name="qos", value=b"\x00", fuzzable=True)
    request.add_header(name="retain", value=b"\x00", fuzzable=True)
    request.add_header(name="payload", value=b"\x00", fuzzable=True)
    return request


def init_structure(session):
    s_initialize("MQTT Connect")
    with s_block("MQTT Connect Header"):
        s_byte(0x10, name="Control Packet Type")

    with s_block("Protocol Name"):
        s_string("MQTT", name="Protocol Name", fuzzable=False)

    s_byte(0x04, name="Protocol Level", fuzzable=True)

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
        s_string("ClientID", name="Client Identifier", fuzzable=True)
    session.connect(s_get("MQTT Connect"))
