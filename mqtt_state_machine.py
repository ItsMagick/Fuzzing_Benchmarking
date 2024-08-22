import matplotlib.pyplot as plt
import networkx as nx

G = nx.DiGraph()

# Define the states
states = [
    "Initial State",
    "Client Connecting",
    "Connected",
    "Subscribed",
    "Publishing",
    "Disconnecting",
    "Disconnected"
]

# Add nodes
for state in states:
    G.add_node(state)

# Define transitions
transitions = [
    ("Initial State", "Client Connecting", "Incoming connection request"),
    ("Client Connecting", "Connected", "Successful authentication"),
    ("Connected", "Subscribed", "Subscription request"),
    ("Subscribed", "Publishing", "Publish request"),
    ("Publishing", "Connected", "Publish complete"),
    ("Connected", "Disconnecting", "Disconnect request"),
    ("Disconnecting", "Disconnected", "Disconnection complete"),
    ("Disconnected", "Initial State", "Re-initialization")
]

# Add edges with labels
for (start, end, label) in transitions:
    G.add_edge(start, end, label=label)

# Draw the graph
pos = nx.spring_layout(G, seed=42)  # Positions for all nodes
plt.figure(figsize=(12, 8))

# Draw nodes
nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue')

# Draw edges
nx.draw_networkx_edges(G, pos, edgelist=G.edges(), arrows=True, arrowstyle='->', arrowsize=30,
                       min_source_margin=15, min_target_margin=25)

# Draw labels
nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

# Draw edge labels
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.title('Mosquitto MQTT Broker State Machine')
plt.axis('off')
plt.show()
