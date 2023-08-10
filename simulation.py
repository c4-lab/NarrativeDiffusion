import configparser
import os
import pandas as pd
import networkx as nx
from datetime import datetime
from agent import Agent
import random

class Simulation:
    def __init__(self, params=None, story_graph=None, social_graph=None, agent_alignments=None):
        if params:
            # Directly assign parameters from the dictionary
            self.params = params
        else:
            # Use configparser to load parameters from a properties file
            self.params = self._load_params_from_file()

        # Setting up graphs and agent alignments
        self.story_graph = story_graph
        self.social_graph = social_graph
        self.agent_alignments = agent_alignments

        # Create a results dataframe
        self.results = []
        self._initialize_agents()

    def _initialize_agents(self):
        """Initialize agents and add them to the nodes of the social_graph."""
        story_nodes = []
        
        for agent_id in self.social_graph.nodes():
            if len(story_nodes)<self.params['seed']:
                new_nodes = list(self.story_graph.nodes())
                random.shuffle(new_nodes)
                story_nodes = story_nodes+ new_nodes
            # Create an agent instance
            agent = Agent(
                agent_id=agent_id,
                alpha=self.params["alpha"],
                beta=self.params["beta"],
                gamma=self.params["gamma"],
                tau=self.params["tau"],
                xi=self.params["xi"],
                I_scale = self.params["I_scale"],
                I_shift = self.params["I_shift"],
                alignments=self.agent_alignments.iloc[agent_id].to_dict(),
                seed_adoptions = story_nodes[:self.params['seed']]
            )
            # Attach the agent to the node in the social graph
            del story_nodes[:self.params['seed']]
            self.social_graph.nodes[agent_id]["agent"] = agent

    def _load_params_from_file(self, filename="simulation.properties"):
        """Load parameters from a properties file using configparser."""
        config = configparser.ConfigParser()
        config.read(filename)
        
        # Extract parameters and return as a dictionary
        params = {
            "alpha": config.getfloat("DEFAULT", "alpha"),
            "beta": config.getfloat("DEFAULT", "beta"),
            "gamma": config.getfloat("DEFAULT", "gamma"),
            "tau": config.getfloat("DEFAULT", "tau"),
            "xi": config.getfloat("DEFAULT", "xi"),
            "filestub": config.get("DEFAULT", "filestub"),
            "I_scale": config.getfloat("DEFAULT","I_scale"),
            "I_shift": config.getfloat("DEFAULT","I_shift"),
            "viral" : config.getboolean("DEFAULT","viral"),
            "seed" : config.getint("DEFAULT", "seed"),
            "N": config.getint("DEFAULT", "N")
        }
        return params

    def neighbors_of(self,agent_id):
         return [self.social_graph.nodes[neighbor]['agent'] for neighbor in self.social_graph[agent_id]]

    def run(self,num_trials =1):
        """Run the simulation for N timesteps or until all agents have adopted all story items."""
        
        for trial in range(num_trials):
            print(f"Running trial {trial+1}...")
            self._initialize_agents()  # Reinitialize agents with new seed stories for each trial

            timestep = 0
            while timestep < self.params["N"]:
                # if (timestep %100 == 0):
                #     print("#",end=None)
                all_adopted = True  # Start with the assumption that all items have been adopted
                
                # Iterate over agents
                for agent_id, data in self.social_graph.nodes(data=True):
                    agent = data['agent']
                    for story_item in self.agent_alignments.columns:
                        # Decide adoption and store the result
                        if agent.adopted_items[story_item]: 
                            self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': True,
                                            'prob':None,'Narrative':None,"Social":None,"Alignment":None, "Trial":trial})
                            continue
                        if self.params['viral']:
                            if not any([story_item in neighbor.adoptions() for neighbor in self.neighbors_of(agent_id)]):
                                self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': False,
                                            'prob':None,'Narrative':None,"Social":None,"Alignment":None, "Trial":trial})

                                continue
                        
                        
                        adopted,prob,W_prime,I,A = agent.decide_adoption(story_item, self.story_graph, self.social_graph)
                        if adopted:
                            agent.adopted_items[story_item] = True  # Update the adopted_items list of the agent.
                        self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': adopted,
                                            'prob':prob,'Narrative':W_prime,"Social":I,"Alignment":A, "Trial":trial})

                # Check if all items are adopted by checking the adopted_items list
                all_adopted = all([data['agent'].all_adopted() for _, data in self.social_graph.nodes(data=True)])

                if all_adopted:
                    break
                
                timestep += 1
            
        self.save_results()

    def save_results(self):
        """Save the results, parameters, networks, and agent alignments."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        directory = f"{self.params['filestub']}_{timestamp}"
        
        # Create the directory
        os.makedirs(directory, exist_ok=True)

        # Save results
        pd.DataFrame(self.results).to_csv(os.path.join(directory, "results.csv"), index=False)
        
        # Save parameters
        with open(os.path.join(directory, "parameters.txt"), "w") as f:
            for key, value in self.params.items():
                f.write(f"{key}={value}\n")

        # Save networks and alignments (assuming these are networkx graphs and pandas dataframes respectively)
        # Note: You might need more sophisticated saving mechanisms depending on the actual data structure
        nx.write_gpickle(self.story_graph, os.path.join(directory, "story_graph.gpickle"))
        nx.write_gpickle(self.social_graph, os.path.join(directory, "social_graph.gpickle"))
        self.agent_alignments.to_csv(os.path.join(directory, "agent_alignments.csv"), index=False)
