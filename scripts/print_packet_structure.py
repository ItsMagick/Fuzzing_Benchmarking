import matplotlib.pyplot as plt
import matplotlib.patches as patches

fig, ax = plt.subplots(figsize=(14, 4))
ax.set_xlim(0, 28)
ax.set_ylim(0, 6)

sections = [
    ("Fixed Header", [(0, 1), (1, 1)], ["Packet \nType\n", "Remaining \nLength\n"]),
    ("Variable Header", [(2, 2), (4, 4), (8, 1), (9, 1), (10, 2)],
     ["Protocol Name \nLength\n", "Protocol Name \n('MQTT')\n", "Protocol \nVersion\n", "Connect \nFlags\n", "Keep Alive"]),
    ("Payload", [(12, 2), (14, 14)], ["Client Identifier \nLength\n", "Client Identifier\n('my_mqtt_client')\n"])
]

section_boundaries = {
    "Fixed Header": (0, 2),
    "Variable Header": (2, 10),
    "Payload": (12, 28)
}

for section_name, (start, end) in section_boundaries.items():
    rect = patches.Rectangle((start, 3.5), end - start, 1.5, linewidth=0, edgecolor=None, facecolor='lightgray', alpha=0.3)
    ax.add_patch(rect)
    ax.text((start + end) / 2, 5, section_name, ha='center', va='center', fontsize=12, fontweight='bold', color='darkblue')

for section_name, positions, labels in sections:
    for (x, w), label in zip(positions, labels):
        rect = patches.Rectangle((x, 2), w, 1, linewidth=1, edgecolor='black', facecolor='lightblue')
        ax.add_patch(rect)
        ax.text(x + w / 2, 3.1, label, ha='center', va='center', fontsize=9)

byte_values = [
    "0x10", "0x13",
    "0x00", "0x04", "0x4D", "0x51", "0x54", "0x54", "0x04", "0x02", "0x00", "0x3C",
    "0x00", "0x0E", "0x6D", "0x79", "0x5F", "0x6D", "0x71", "0x74", "0x74", "0x5F", "0x63", "0x6C", "0x69", "0x65", "0x6E", "0x74"
]

for i, byte in enumerate(byte_values):
    ax.text(i + 0.5, 2.5, byte, ha='center', va='center', fontsize=9)
    ax.text(i + 0.5, 1.6, str(i), ha='center', va='center', fontsize=8, color='black')

ax.axis('off')
plt.savefig("mqtt_packet_structure_final.png", bbox_inches='tight', dpi=300)
plt.show()
