import networkx as nx
import numpy as np


class Agent:
    def __init__(self, agent_id, alpha, beta, gamma, phi, max_item_relevance, I_scale, x_0, x_s, story_nodes, seed_adoptions=None, current_timestep=0):

        self.agent_id = agent_id
        self.story_nodes = story_nodes
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.max_item_relevance = max_item_relevance
        self.I_scale = I_scale
        self.x_0 = x_0
        self.x_s = x_s
        self.phi=phi
        #self.current_timestep = current_timestep



        # Track adopted story items.
        self.adopted_items = {k: False for k in story_nodes}
        if seed_adoptions is not None:
            for item in seed_adoptions:
                self.adopted_items[item] = True

    def adoptions(self):
        return [idx for idx, adopted in self.adopted_items.items() if adopted]
    
    def adoption_status(self,item):
        return self.adopted_items[item]

    def social_influence(self, story_item, social_graph):
        """Calculate the social influence for a story item."""
        neighbors_adopted = sum([1 for neighbor in social_graph[self.agent_id] if social_graph.nodes[neighbor]['agent'].adopted_items[story_item]])
        # Sigmoid squashing
        I = 2 / (1 + np.exp(-self.I_scale * neighbors_adopted)) -1
        return I

    # def update_current_timestep(self, timestep):
    #     """Update the current timestep of the simulation."""
    #     self.current_timestep = timestep
    
    def calculate_theta(self, item_age):
        """Calculate theta (baseline probability of adoption) for item given its age."""
        # Note the +1 is just to keep the semantics in line with the parameter age
        # That is, the item will be relevant up to and including max_item_relevance timesteps
        scaling = max(1 - (item_age / (self.max_item_relevance+1)),0)
        theta = self.beta*scaling

        return theta


    def narrative_influence(self, story_item, content_graph, theta):
        """Calculate the narrative influence for a story item based on visibility."""
        adopted_nodes = self.adoptions()
        unscaled_W = sum([1/nx.shortest_path_length(content_graph, source=story_item, target=adopted_node)**self.phi for adopted_node in adopted_nodes]) if adopted_nodes else 0
        W = 1 / (1 + np.exp(-self.x_s * (theta + self.gamma * unscaled_W - self.x_0)))
        return W

    def adoption_probability(self, story_item, item_age, content_graph, social_graph):
        """Calculate the adoption probability for a story item."""
        theta = self.calculate_theta(item_age)
        # This shouldn't happen, but just in case
        if not theta:
            return 0,0,0
        
        W = self.narrative_influence(story_item, content_graph, theta)
        I = self.social_influence(story_item, social_graph)

        total_influence = self.alpha * W + (1-self.alpha) * I
        return total_influence, W, I

    def decide_adoption(self, story_item, item_age, content_graph, social_graph):
        """Decide whether to adopt a story item based on its adoption probability."""
        if self.adopted_items[story_item]:
            return True, 1.0, 1.0, 1.0
        else:
            prob, W, I = self.adoption_probability(story_item, item_age, content_graph, social_graph)
            return np.random.rand() <= prob, prob, W, I

    def all_adopted(self): 
        return all(self.adopted_items.values())
