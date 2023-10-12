import networkx as nx
import numpy as np


class Agent:
    def __init__(self, alpha, agent_id, beta, gamma, I_scale, k, story_nodes, seed_adoptions=None):
        self.agent_id = agent_id
        self.story_nodes = story_nodes
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.I_scale = I_scale
        self.k = k  # Field of vision

        # Track adopted story items.
        self.adopted_items = {k: False for k in story_nodes}
        if seed_adoptions is not None:
            for item in seed_adoptions:
                self.adopted_items[item] = True

    def adoptions(self):
        return [idx for idx, adopted in self.adopted_items.items() if adopted]

    def social_influence(self, story_item, social_graph):
        """Calculate the social influence for a story item."""
        neighbors_adopted = sum([1 for neighbor in social_graph[self.agent_id] if social_graph.nodes[neighbor]['agent'].adopted_items[story_item]])
        # Sigmoid squashing
        I = 2 / (1 + np.exp(-self.I_scale * neighbors_adopted)) -1
        return I

    def narrative_influence(self, story_item, content_graph):
        """Calculate the narrative influence for a story item based on visibility."""
        adopted_nodes = self.adoptions()
        if adopted_nodes:
            inverse_distances = [1/nx.shortest_path_length(content_graph, source=story_item, target=adopted_node) 
                                 for adopted_node in adopted_nodes 
                                 if nx.shortest_path_length(content_graph, source=story_item, target=adopted_node) <= self.k]
            unscaled_W = sum(inverse_distances) 
        else:
            unscaled_W = 0
        W =  1 / (1 + np.exp(- (self.beta + self.gamma * unscaled_W)))
        return W

    def adoption_probability(self, story_item, content_graph, social_graph):
        """Calculate the adoption probability for a story item."""
        W = self.narrative_influence(story_item, content_graph)
        I = self.social_influence(story_item, social_graph)

        total_influence = self.alpha * W + (1-self.alpha) * I
        return total_influence, W, I

    def decide_adoption(self, story_item, content_graph, social_graph):
        """Decide whether to adopt a story item based on its adoption probability."""
        if self.adopted_items[story_item]:
            return True
        else:
            prob, W, I = self.adoption_probability(story_item, content_graph, social_graph)
            return np.random.rand() <= prob, prob, W, I

    def all_adopted(self): 
        return all(self.adopted_items.values())
