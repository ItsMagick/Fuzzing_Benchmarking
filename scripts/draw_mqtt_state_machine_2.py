from graphviz import Digraph

# Create a Digraph object
dot = Digraph()

# Define the states
dot.node('s0', 'Init')
dot.node('s1', 'Connected')
dot.node('s2', 'Subscribed')
dot.node('s3', 'Publishing')

# Define the transitions
dot.edge('s1', 's2', label='Sub / S_Ack')
dot.edge('s2', 's1', label='UnSub / US_Ack')
dot.edge('s2', 's3', label='+ / +')
dot.edge('s3', 's2', label='+ / +')
dot.edge('s3', 's0', label='Discon(TCP) / Closed')
dot.edge('s1', 's0', label='Discon(TCP) / Closed')
dot.edge('s0', 's1', label='Con / C_Ack')
dot.edge('s2', 's0', label='Discon(TCP) / Closed')

# Render and save the state machine diagram
dot.render('state_machine', format='png', view=True)
