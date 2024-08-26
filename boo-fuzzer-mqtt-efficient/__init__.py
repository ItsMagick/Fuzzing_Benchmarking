from boofuzz import *
import threading

MQTT_BROKER_HOST = "127.0.0.1"
MQTT_BROKER_PORT = 1884
FIXED_TOPIC = "fuzzing/topic"  # Fixed topic that should not be fuzzed


def publisher_session():
    session = Session(target=Target(connection=SocketConnection(MQTT_BROKER_HOST, MQTT_BROKER_PORT, proto="tcp")))

    # MQTT CONNECT Packet
    s_initialize("MQTT Connect")
    with s_block("Connect Header"):
        s_byte(0x10)  # MQTT Control Packet Type for CONNECT

    with s_block("Protocol Name"):
        s_string("MQTT", fuzzable=False)
        s_size("Protocol Name Length", 2, fuzzable=False, endian='big')

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
        s_string("ClientID", fuzzable=True)
        s_size("Client Identifier Length", 2, fuzzable=False, endian='big')

    session.connect(s_get("MQTT Connect"))

    # MQTT PUBLISH Packet
    s_initialize("MQTT Publish")
    with s_block("Publish Header"):
        s_byte(0x30)  # MQTT Control Packet Type for PUBLISH

    with s_block("Topic Name"):
        s_string(FIXED_TOPIC, fuzzable=False)
        s_size("Topic Name Length", 2, fuzzable=False, endian='big')

    s_string("Fuzzing Payload", name="Payload", fuzzable=True)  # Fuzz the payload

    session.connect(s_get("MQTT Publish"))

    # Start fuzzing
    session.fuzz()


def subscriber_session():
    session = Session(target=Target(connection=SocketConnection(MQTT_BROKER_HOST, MQTT_BROKER_PORT, proto="tcp")))

    # MQTT CONNECT Packet
    s_initialize("MQTT Connect")
    with s_block("Connect Header"):
        s_byte(0x10)  # MQTT Control Packet Type for CONNECT

    with s_block("Protocol Name"):
        s_string("MQTT", fuzzable=False)
        s_size("Protocol Name Length", 2, fuzzable=False, endian='big')

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
        s_size("Client Identifier Length", 2, fuzzable=False, endian='big')

    session.connect(s_get("MQTT Connect"))
    s_initialize("MQTT Subscribe")
    with s_block("Subscribe Header"):
        s_byte(0x82)  # MQTT Control Packet Type for SUBSCRIBE

    s_word(1, name="Packet Identifier", fuzzable=True)

    with s_block("Topic Filters"):
        with s_block("Topic Filter"):
            s_string(FIXED_TOPIC, fuzzable=False)
            s_size("Topic Filter Length", 2, fuzzable=False, endian='big')
            s_byte(0x00, name="Requested QoS", fuzzable=True)

    session.connect(s_get("MQTT Subscribe"))

    session.fuzz()


if __name__ == "__main__":
    # Run publisher and subscriber in parallel
    pub_thread = threading.Thread(target=publisher_session)
    sub_thread = threading.Thread(target=subscriber_session)

    pub_thread.start()
    sub_thread.start()

    pub_thread.join()
    sub_thread.join()
