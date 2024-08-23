import struct


def create_connect_packet(client_id, keep_alive=60):
    packet_type = 0x10
    remaining_length = 2 + 4 + len(client_id)

    fixed_header = struct.pack('!BB', packet_type, remaining_length)

    protocol_name = b'\x00\x04MQTT'
    protocol_version = 0x04
    connect_flags = 0x02
    keep_alive = struct.pack('!H', keep_alive)

    variable_header = protocol_name + struct.pack('!BB', protocol_version, connect_flags) + keep_alive

    client_id_length = struct.pack('!H', len(client_id))
    payload = client_id_length + client_id.encode('utf-8')

    mqtt_packet = fixed_header + variable_header + payload
    return mqtt_packet


def print_packet(packet):
    print("MQTT Packet Explanation:")
    for i, byte in enumerate(packet):
        print(f"{i:02d}: {byte:02x} - ", end='')
        if i == 0:
            print("Fixed Header: Packet Type (0x10 = CONNECT)")
        elif i == 1:
            print("Fixed Header: Remaining Length")
        elif i == 2:
            print("Variable Header: Protocol Name Length MSB (0x00)")
        elif i == 3:
            print("Variable Header: Protocol Name Length LSB (0x04)")
        elif 4 <= i <= 7:
            print(f"Variable Header: Protocol Name ('MQTT' byte {i - 4})")
        elif i == 8:
            print("Variable Header: Protocol Version (0x04 = MQTT 3.1.1)")
        elif i == 9:
            print("Variable Header: Connect Flags (0x02 = Clean Session)")
        elif i == 10:
            print("Variable Header: Keep Alive MSB (Most Significant Byte)")
        elif i == 11:
            print("Variable Header: Keep Alive LSB (Least Significant Byte)")
        elif i == 12:
            print("Payload: Client Identifier Length MSB")
        elif i == 13:
            print("Payload: Client Identifier Length LSB")
        else:
            print(f"Payload: Client Identifier ('{chr(byte)}' byte {i - 14})")


# Example usage
client_id = "my_mqtt_client"
packet = create_connect_packet(client_id)
print_packet(packet)
