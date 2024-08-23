import os
import struct

MQTT_CONNECT = 0x10
MQTT_PUBLISH = 0x30
MQTT_SUBSCRIBE = 0x82
MQTT_UNSUBSCRIBE = 0xA2
MQTT_PINGREQ = 0xC0
MQTT_DISCONNECT = 0xE0

output_dir = "../aflnet_in"


def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def write_to_file(data, filename):
    safe_filename = filename.replace('\x00', '').replace('/', '_')
    with open(os.path.join(output_dir, safe_filename), 'wb') as f:
        f.write(data)


def generate_connect(client_id="aflnet", clean_session=True, keep_alive=10):
    protocol_name = b'\x00\x04MQTT'
    protocol_level = b'\x04'
    connect_flags = b'\x02' if clean_session else b'\x00'
    keep_alive = struct.pack("!H", keep_alive)
    client_id = struct.pack("!H", len(client_id)) + client_id.encode()
    payload = protocol_name + protocol_level + connect_flags + keep_alive + client_id
    remaining_length = len(payload)
    connect_message = struct.pack("B", MQTT_CONNECT) + struct.pack("B", remaining_length) + payload
    write_to_file(connect_message, f"connect_{client_id}.bin")
    return connect_message


def generate_publish(topic="test", message="Hello, MQTT!", qos=0, retain=False):
    topic = struct.pack("!H", len(topic)) + topic.encode()
    message_id = b'' if qos == 0 else struct.pack("!H", 1)
    payload = topic + message_id + message.encode()
    qos_shift = qos << 1
    retain_flag = 1 if retain else 0
    fixed_header = MQTT_PUBLISH | qos_shift | retain_flag
    remaining_length = len(payload)
    publish_message = struct.pack("B", fixed_header) + struct.pack("B", remaining_length) + payload
    topic_safe = topic.decode(errors='ignore').replace('\x00', '').replace('/', '_')
    filename = f"publish_{topic_safe}_{qos}.bin"
    write_to_file(publish_message, filename)
    return publish_message


def generate_subscribe(topic="test", qos=0):
    message_id = struct.pack("!H", 1)
    topic = struct.pack("!H", len(topic)) + topic.encode()
    qos = struct.pack("B", qos)
    payload = message_id + topic + qos
    remaining_length = len(payload)
    subscribe_message = struct.pack("B", MQTT_SUBSCRIBE) + struct.pack("B", remaining_length) + payload
    topic_safe = topic.decode(errors='ignore').replace('\x00', '').replace('/', '_')
    write_to_file(subscribe_message, f"subscribe_{topic_safe}_{qos.decode()}.bin")
    return subscribe_message


def generate_unsubscribe(topic="test"):
    message_id = struct.pack("!H", 1)
    topic = struct.pack("!H", len(topic)) + topic.encode()
    payload = message_id + topic
    remaining_length = len(payload)
    unsubscribe_message = struct.pack("B", MQTT_UNSUBSCRIBE) + struct.pack("B", remaining_length) + payload
    topic_safe = topic.decode(errors='ignore').replace('\x00', '').replace('/', '_')
    write_to_file(unsubscribe_message, f"unsubscribe_{topic_safe}.bin")
    return unsubscribe_message


def generate_pingreq():
    pingreq_message = struct.pack("B", MQTT_PINGREQ) + struct.pack("B", 0x00)
    write_to_file(pingreq_message, "pingreq.bin")
    return pingreq_message


def generate_disconnect():
    disconnect_message = struct.pack("B", MQTT_DISCONNECT) + struct.pack("B", 0x00)
    write_to_file(disconnect_message, "disconnect.bin")
    return disconnect_message


def generate_malformed_messages():
    malformed_connect = b'\x10\x00'
    write_to_file(malformed_connect, "malformed_connect.bin")
    malformed_publish = struct.pack("B", MQTT_PUBLISH) + struct.pack("B", 0x01) + b'\x00'
    write_to_file(malformed_publish, "malformed_publish.bin")
    malformed_subscribe = struct.pack("B", MQTT_SUBSCRIBE) + struct.pack("B", 0x02) + b'\x00'
    write_to_file(malformed_subscribe, "malformed_subscribe.bin")


def generate_sequence():
    connect_message = generate_connect(client_id="aflnet_seq", clean_session=True, keep_alive=60)
    publish_message = generate_publish(topic="topic_seq", message="Sequence Message", qos=1, retain=True)
    subscribe_message = generate_subscribe(topic="topic_seq", qos=1)
    pingreq_message = generate_pingreq()
    disconnect_message = generate_disconnect()
    sequence = b''.join([connect_message, publish_message, subscribe_message, pingreq_message, disconnect_message])
    write_to_file(sequence, "sequence.bin")


def generate_inputs():
    create_directory(output_dir)
    generate_connect(client_id="aflnet1", clean_session=True, keep_alive=10)
    generate_connect(client_id="aflnet2", clean_session=False, keep_alive=0)
    generate_connect(client_id="aflnet_longid", clean_session=True, keep_alive=300)
    generate_publish(topic="test", message="Short", qos=0, retain=False)
    generate_publish(topic="test/long", message="This is a longer message with special characters !@#$%^&*", qos=1,
                     retain=False)
    generate_publish(topic="test/retain", message="Retained Message", qos=2, retain=True)
    generate_subscribe(topic="test", qos=0)
    generate_subscribe(topic="test/multitopic", qos=1)
    generate_subscribe(topic="test/edgecase", qos=2)
    generate_unsubscribe(topic="test")
    generate_unsubscribe(topic="test/multitopic")
    generate_pingreq()
    generate_disconnect()
    generate_malformed_messages()
    generate_sequence()


if __name__ == "__main__":
    generate_inputs()
