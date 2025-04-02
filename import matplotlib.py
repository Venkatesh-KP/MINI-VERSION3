import matplotlib.pyplot as plt
import networkx as nx

# Create a directed graph
G = nx.DiGraph()

# Define nodes for diseases, symptoms, and test results
disease = "Pneumonia"
symptoms = ["Cough", "Fever"]
test_results = ["Positive X-ray"]

# Add nodes and edges to the graph
G.add_node(disease, color='lightblue')
for symptom in symptoms:
    G.add_node(symptom, color='lightgreen')
    G.add_edge(disease, symptom)
for test in test_results:
    G.add_node(test, color='lightcoral')
    G.add_edge(disease, test)

# Define position for nodes
pos = nx.spring_layout(G, seed=42)

# Draw the graph
colors = [G.nodes[node].get('color', 'lightblue') for node in G.nodes()]
nx.draw(G, pos, with_labels=True, node_color=colors, node_size=3000, font_size=10, font_color='black', font_weight='bold', arrows=True, arrowsize=20)

# Display the plot
plt.title("Bayesian Network for Medical Diagnosis")
plt.show()
