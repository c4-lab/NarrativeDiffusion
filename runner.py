from simulation import Simulation
import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
import json

def main():
    story_graph = nx.read_edgelist("story.edgelist",delimiter = ",")
   
    with open("storynodeprops.json") as f:
        storyprops = json.load(f)
    G = build_lattice_graph(30)
    alignment_df = pd.DataFrame()
    for sn in story_graph.nodes():
        
        alignments = []
        for agentid, data in G.nodes(data=True):
            if str(sn) in storyprops:
                if storyprops[str(sn)] == data['color']:
                    alignments.append(1.0)
                else:
                    alignments.append(-1.0)
            else:
                alignments.append(0)
        alignment_df[sn] = alignments
    
    Simulation(story_graph=story_graph,social_graph=G,agent_alignments=alignment_df).run(100)


def build_lattice_graph(n):
    colorset = ['red','blue']
    G = nx.watts_strogatz_graph(n = n, k=4, p = 0)
    for nodeid in G.nodes():
        #G.nodes[nodeid]["color"] = colorset[nodeid%2]
        G.nodes[nodeid]["color"] = "blue"
    return G

main()

# This doesn't work
def unfriendly_partition(G):
    nodes = list(G.nodes())
    random.shuffle(nodes)
    
    # Assign initial colors
    colors = {node: 'red' if idx < len(nodes) // 2 else 'blue' for idx, node in enumerate(nodes)}
    
    for _ in range(1000):  # Iterate many times to try to get a good partition
        swapped = False
        for node in nodes:
            neighbors = list(G[node])
            same_color_neighbors = sum(1 for neighbor in neighbors if colors[neighbor] == colors[node])
            if same_color_neighbors != 1:
                # Try to find a swap
                for other_node in nodes:
                    if colors[other_node] != colors[node]:
                        other_neighbors = list(G[other_node])
                        other_same_color_neighbors = sum(1 for neighbor in other_neighbors if colors[neighbor] == colors[other_node])
                        
                        # Check if the swap is beneficial for the other node
                        if other_same_color_neighbors != 1:
                            colors[node], colors[other_node] = colors[other_node], colors[node]
                            swapped = True
                            break
        if not swapped:
            break

    return colors

def build_cubic_graph(n):
    G = nx.random_regular_graph(d=3, n=30)
    colors = unfriendly_partition(G)
    return G,colors



#G,colors = build_lattice_graph(30)
#nx.draw(G, with_labels=True, node_color=[colors[node] for node in G.nodes()])
# G = nx.read_edgelist("story.edgelist",delimiter=",")
# nx.draw(G,with_labels = True)
# plt.show()
