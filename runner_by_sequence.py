from simulation_combined_saving import Simulation
import networkx as nx
import matplotlib.pyplot as plt
import random
import pandas as pd
import json
import itertools
from datetime import datetime
import os


def build_lattice_graph(n):
    colorset = ['red','blue']
    G = nx.watts_strogatz_graph(n = n, k=4, p = 0)
    for nodeid in G.nodes():
        #G.nodes[nodeid]["color"] = colorset[nodeid%2]
        G.nodes[nodeid]["color"] = "blue"
    return G


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


def main_linear():
    story_graph = build_linear_graph(5)
    social_graph = build_linear_graph(1)

    # Generate all permutations of the revelation vector R
    num_nodes = story_graph.number_of_nodes()
    all_R_permutations = itertools.permutations(range(num_nodes))
    
    all_results = []

    for R_permutation in all_R_permutations:
        # Create custom parameters with the current permutation of R
        custom_params = {
            "R": list(R_permutation)
        }
        # Run the simulation with the current permutation of R
        print(f"Running simulation with R = {custom_params['R']}")
        results = Simulation(story_graph=story_graph, social_graph=social_graph, params=custom_params).run(1000)
        all_results.extend(results)  # Append these results
        
    # Save all results to a CSV file
    # Filename format
    social_nodes = social_graph.number_of_nodes()
    story_nodes = story_graph.number_of_nodes()
    filename_base = f"data/combined_results_social{social_nodes}_story{story_nodes}"
    filename = filename_base + ".csv"
    counter = 1

    # Check if the file exists and modify the filename accordingly
    while os.path.exists(filename):
        filename = f"{filename_base}_{counter}.csv"
        counter += 1

    # Save all results to the CSV file with a unique filename
    pd.DataFrame(all_results).to_csv(filename, index=False)


main_linear()