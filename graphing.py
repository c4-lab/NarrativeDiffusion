import networkx as nx
import matplotlib.pyplot as plt

def build_cubic_graph(n):
    G = nx.random_regular_graph(d=3, n=n)
    #colors = unfriendly_partition(G)
    return G


G = build_cubic_graph(26)
nx.draw(G,with_labels = True)
plt.show()