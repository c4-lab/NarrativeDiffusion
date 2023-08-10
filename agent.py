import networkx as nx
import numpy as np
import math

class Agent:
    def __init__(self, agent_id, alpha, beta, gamma, tau, xi, I_scale, I_shift, alignments,seed_adoptions=None):
        self.agent_id = agent_id
        # Alignment values for each story item.
        self.alignment = alignments

        # Config params
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.tau = tau
        self.xi = xi
        self.I_scale = I_scale
        self.I_shift = I_shift

        # Track adopted story items.
        self.adopted_items = {k:False for k in alignments.keys()}
        if seed_adoptions is not None:
            for item in seed_adoptions:
                self.adopted_items[item] = True
        
    def adoptions(self):
        return [idx for idx, adopted in self.adopted_items.items() if adopted]

    def narrative_influence(self, story_item, content_graph):
        """Calculate the narrative influence for a story item."""
        adopted_nodes =self.adoptions()
        if adopted_nodes:
            distances = [nx.shortest_path_length(content_graph, source=story_item, target=adopted_node) for adopted_node in adopted_nodes]
            W_si = sum([np.exp(-d) for d in distances]) 
            W_prime = 1/(1+math.exp(-self.xi*(W_si - self.tau)))
            #print(f"Agent:{self.agent_id} dist:{distances} wsi:{W_si} w_prime:{W_prime}")
        else:
            W_prime = 0
        
        return W_prime

    def social_influence(self, story_item, social_graph):
        """Calculate the social influence for a story item."""
        neighbors_adopted = sum([1 for neighbor in social_graph[self.agent_id] if social_graph.nodes[neighbor]['agent'].adopted_items[story_item]])
        I_raw = np.log(1 + neighbors_adopted)
        # Sigmoid squashing
        I_norm = 1 / (1 + np.exp(-self.I_scale * (I_raw - self.I_shift)))
        return I_norm


    def alignment_factor(self, story_item):
        """Calculate the alignment factor for a story item."""
        return (1+self.alignment[story_item])/2

    def adoption_probability(self, story_item, content_graph, social_graph):
        """Calculate the adoption probability for a story item."""
        W_prime = self.narrative_influence(story_item, content_graph)
        I = self.social_influence(story_item, social_graph)
        A = self.alignment_factor(story_item)
        
        # Combining all influences with their weights.
        total_influence = self.gamma * W_prime + self.alpha * I + self.beta * A
        normalization = self.gamma + self.alpha + self.beta
        
        return total_influence / normalization,W_prime,I,A

    def decide_adoption(self, story_item, content_graph, social_graph):
        """Decide whether to adopt a story item based on its adoption probability."""
        if self.adopted_items[story_item]:
            return True
        else:
            prob,W_prime,I,A = self.adoption_probability(story_item, content_graph, social_graph)
            return np.random.rand() <= prob,prob,W_prime,I,A
        
    def all_adopted(self): 
        return all(self.adopted_items.values())
