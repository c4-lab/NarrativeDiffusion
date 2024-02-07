from simulation import Simulation
import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
import json




def build_lattice_graph(n):
    colorset = ['red','blue']
    G = nx.watts_strogatz_graph(n = n, k=4, p = 0)
    for nodeid in G.nodes():
        #G.nodes[nodeid]["color"] = colorset[nodeid%2]
        G.nodes[nodeid]["color"] = "blue"
    return G



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

def build_linear_graph(size):
    """
    Generate a linear graph with the given number of nodes.
    
    :param size: Number of nodes in the graph.
    :return: A networkx Graph object representing the linear graph.
    """
    
    # Create an empty graph
    G = nx.Graph()
    
    # Add nodes and edges to create a linear structure
    # If the size is 1, add only one node and return

    if size == 1:
        G.add_node(0)
    else:
        for i in range(size - 1):
            G.add_edge(i, i+1)
        
    return G

def generate_tree(n, b):
    """
    Generates a tree graph with n nodes and branching factor b.
    
    Parameters:
    - n: Total number of nodes.
    - b: Branching factor.

    Returns:
    - G: A networkx graph.
    """
    if n < 1:
        raise ValueError("The number of nodes, n, should be at least 1.")
    if b < 1:
        raise ValueError("The branching factor, b, should be at least 1.")

    G = nx.Graph()
    node_counter = 1
    queue = [(0, 0)]  # (node, depth)
    
    while queue and node_counter < n:
        current_node, depth = queue.pop(0)
        for i in range(b):
            if node_counter >= n:
                break
            child_node = node_counter
            G.add_edge(current_node, child_node)
            queue.append((child_node, depth + 1))
            node_counter += 1

    return G


#G,colors = build_lattice_graph(30)
#nx.draw(G, with_labels=True, node_color=[colors[node] for node in G.nodes()])
# G = nx.read_edgelist("story.edgelist",delimiter=",")
# nx.draw(G,with_labels = True)
# plt.show()

# TODO: Need to fix this up to get rid of alignments
# def main_loom():
#     story_graph = nx.read_edgelist("config/story.edgelist",delimiter = ",")
   
#     with open("config/storynodeprops.json") as f:
#         storyprops = json.load(f)
#     G = build_lattice_graph(30)
#     alignment_df = pd.DataFrame()
#     for sn in story_graph.nodes():
        
#         alignments = []
#         for agentid, data in G.nodes(data=True):
#             if str(sn) in storyprops:
#                 if storyprops[str(sn)] == data['color']:
#                     alignments.append(1.0)
#                 else:
#                     alignments.append(-1.0)
#             else:
#                 alignments.append(0)
#         alignment_df[sn] = alignments
    
#     Simulation(story_graph=story_graph,social_graph=G,agent_alignments=alignment_df).run(50)


def main_linear():
    story_graph = generate_tree(10, 2)
    G = build_lattice_graph(50)
    alignment_df = pd.DataFrame()
    for sn in story_graph.nodes():
        alignments = [0]*G.number_of_nodes()
        alignment_df[sn] = alignments
    
    Simulation(story_graph=story_graph,social_graph=G).run(100)


main_linear()