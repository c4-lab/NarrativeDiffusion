import configparser
import os
import pandas as pd
import json
import networkx as nx
from datetime import datetime
from agent import Agent
import random
import pickle

class Simulation:
    def __init__(self, params=None, story_graph=None, social_graph=None, config_path="./config/simulation.properties"):
        
            # Use configparser to load parameters from a properties file
        self.params = self._load_params_from_file(config_path)
        if params:
            for k,v in params.items():
                self.params[k]=v

        # Setting up graphs and agent alignments
        self.story_graph = story_graph
        self.social_graph = social_graph
        self.release_time = self.params["R"]
        print("Story nodes",[n for n in self.story_graph.nodes()])
        if len(self.release_time) < self.story_graph.number_of_nodes():
            delta = (self.story_graph.number_of_nodes()-len(self.release_time))

            self.release_time += delta * [self.params["R"][-1]]
            print("Release time ",self.release_time)

        
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
                I_scale=self.params['I_scale'],
                x_0 = self.params["x_0"],
                x_s = self.params["x_s"],
                story_nodes=list(self.story_graph.nodes()),
                seed_adoptions = story_nodes[:self.params['seed']]
            )
            # Attach the agent to the node in the social graph
            del story_nodes[:self.params['seed']]
            self.social_graph.nodes[agent_id]["agent"] = agent

    def _load_params_from_file(self, config_path):
        """Load parameters from a properties file using configparser."""
        config = configparser.ConfigParser()
        config.read(config_path)
        
        # Extract parameters and return as a dictionary
        params = {
            "alpha": config.getfloat("DEFAULT", "alpha"),
            "beta": config.getfloat("DEFAULT", "beta"),
            "gamma": config.getfloat("DEFAULT", "gamma"),
            "I_scale": config.getfloat("DEFAULT", "I_scale"),
            "x_0": config.getfloat("DEFAULT","x_0"),
            "x_s": config.getfloat("DEFAULT","x_s"),
            "filestub": config.get("DEFAULT", "filestub"),
            "seed" : config.getint("DEFAULT", "seed"),
            #"viral" : config.getboolean("DEFAULT","viral"),
            "N": config.getint("DEFAULT", "N"),
            "R": json.loads(config.get("DEFAULT","R"))
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
                all_adopted = True  # Start with the assumption that all items have been adopted
                
                # Iterate over agents
                for agent_id, data in self.social_graph.nodes(data=True):
                    agent = data['agent']
                    for story_item in self.story_graph.nodes():
                        # Decide adoption and store the result
                        if agent.adopted_items[story_item]: 
                            self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': True,
                                            'prob':None,'Narrative':None,"Social":None, "Trial":trial})
                            continue
                        if self.params['R'][story_item] > timestep:
                            self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': False,
                                            'prob':None,'Narrative':None,"Social":None, "Trial":trial})

                            continue
                        # if self.params['viral']:
                        #     if not any([story_item in neighbor.adoptions() for neighbor in self.neighbors_of(agent_id)]):
                        #         self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': False,
                        #                     'prob':None,'Narrative':None,"Social":None, "Trial":trial})

                        #         continue
                        
                        
                        adopted,prob,W,I = agent.decide_adoption(story_item, self.story_graph, self.social_graph)
                        if adopted:
                            agent.adopted_items[story_item] = True  # Update the adopted_items list of the agent.
                        self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': adopted,
                                            'prob':prob,'Narrative':W,"Social":I, "Trial":trial})

                # Check if all items are adopted by checking the adopted_items list
                all_adopted = all([data['agent'].all_adopted() for _, data in self.social_graph.nodes(data=True)])

                if all_adopted:
                    break
                
                timestep += 1
            
        self.save_results()

    def save_results(self):
        """Save the results, parameters, networks, and agent alignments."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        directory = f"data/{self.params['filestub']}_{timestamp}"
        
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
        with open(os.path.join(directory, "story_graph.gpickle"),'wb') as f:
            pickle.dump(self.story_graph, f, pickle.HIGHEST_PROTOCOL)

        with open(os.path.join(directory, "social_graph.gpickle"),'wb') as f:
            pickle.dump(self.social_graph, f, pickle.HIGHEST_PROTOCOL)
        
