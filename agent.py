import networkx as nx
import numpy as np


class Agent:
    def __init__(self, agent_id, alpha, beta, gamma, delta, I_scale, x_0, x_s, story_nodes, broadcast_schedule, seed_adoptions=None, current_timestep=0):
        self.agent_id = agent_id
        self.story_nodes = story_nodes
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.I_scale = I_scale
        self.x_0 = x_0
        self.x_s = x_s
        self.current_timestep = current_timestep

        # Initialize broadcast_schedule as a dictionary mapping items to their last broadcast timestep
        self.last_broadcast_time = {item: times for item, times in broadcast_schedule.items()}

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

    def update_current_timestep(self, timestep):
        """Update the current timestep of the simulation."""
        self.current_timestep = timestep
    
    def calculate_theta(self, story_item):
        """Calculate theta for a story item considering all its broadcast times."""
        broadcast_times = [time for time in self.last_broadcast_time.get(story_item, []) if time <= self.current_timestep]

        if not broadcast_times:
            # If the item has not been broadcasted by now, it retains its initial influence
            return self.beta

        # Find the most recent broadcast time
        most_recent_broadcast = max(broadcast_times)
        time_since_last_broadcast = self.current_timestep - most_recent_broadcast

        # Calculate theta based on the time since the last broadcast, applying decay if time has passed
        if time_since_last_broadcast == 0:
            # If the item was broadcasted at the current timestep, it has full influence
            theta = self.beta
        else:
            # Apply decay based on the time since the last broadcast
            theta = max(self.beta - time_since_last_broadcast * self.delta, 0)

        return theta


    def narrative_influence(self, story_item, content_graph):
        """Calculate the narrative influence for a story item based on visibility."""
        theta = self.calculate_theta(story_item)
        if theta <= 0:  # Skip narrative influence calculation if theta is 0
            return 0
        adopted_nodes = self.adoptions()
        unscaled_W = sum([1/nx.shortest_path_length(content_graph, source=story_item, target=adopted_node) for adopted_node in adopted_nodes]) if adopted_nodes else 0
        theta = self.calculate_theta(story_item)
        W = 1 / (1 + np.exp(-self.x_s * (theta + self.gamma * unscaled_W - self.x_0)))
        return W

    def adoption_probability(self, story_item, is_broadcasting, content_graph, social_graph):
        """Calculate the adoption probability for a story item."""
        W = self.narrative_influence(story_item, content_graph) if is_broadcasting else 0
        I = self.social_influence(story_item, social_graph)

        total_influence = self.alpha * W + (1-self.alpha) * I
        return total_influence, W, I

    def decide_adoption(self, story_item, is_broadcasting, content_graph, social_graph):
        """Decide whether to adopt a story item based on its adoption probability."""
        if self.adopted_items[story_item]:
            return True, 1.0, 1.0, 1.0
        else:
            prob, W, I = self.adoption_probability(story_item, is_broadcasting, content_graph, social_graph)
            return np.random.rand() <= prob, prob, W, I

    def all_adopted(self): 
        return all(self.adopted_items.values())
