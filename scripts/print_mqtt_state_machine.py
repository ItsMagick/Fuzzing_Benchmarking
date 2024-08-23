from graphviz import Digraph

# Create a new directed graph
dot = Digraph(comment='Mosquitto MQTT Broker State Machine')

# Define states
states = [
    "Start", "Initialization", "Listening", "Processing",
    "Publishing", "Subscribing", "Terminating", "Stopped"
]

# Add states to the graph
for state in states:
    dot.node(state)

# Define transitions
transitions = [
    ("Start", "Initialization", "Start MQTT Broker"),
    ("Initialization", "Listening", "Initialize Network Interface"),
    ("Listening", "Processing", "Receive MQTT Message"),
    ("Processing", "Publishing", "Publish Message"),
    ("Processing", "Subscribing", "Subscribe to Topic"),
    ("Processing", "Listening", "Idle"),
    ("Listening", "Terminating", "Shutdown Request"),
    ("Terminating", "Stopped", "Cleanup Resources")
]

# Add transitions to the graph
for start, end, label in transitions:
    dot.edge(start, end, label)

# Render the graph
dot.render('mosquitto_state_machine', view=True, format='png')

# Print the dot source code
print(dot.source)
