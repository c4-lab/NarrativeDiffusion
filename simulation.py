import configparser
import os
import pandas as pd
import json
import networkx as nx
from datetime import datetime
from agent import Agent
import random
import pickle
import time
from collections import defaultdict

class Simulation:
    def __init__(self, params=None, story_graph=None, social_graph=None, config_path="./config/simulation.properties"):
        
            # Use configparser to load parameters from a properties file
        self.params = self._load_params_from_file(config_path)
        if params:
            for k,v in params.items():
                self.params[k]=v

        # Convert the R parameter from JSON string to list of tuples
        self.params["R"] = json.loads(self.params["R"])

        # Setting up graphs and agent alignments
        self.story_graph = story_graph
        self.social_graph = social_graph

        # Convert list of tuples into broadcasting schedule dictionary
        self.broadcast_schedule = defaultdict(list)
        for item, timestep in self.params["R"]:
            self.broadcast_schedule[timestep].append(item)
        
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
                phi = self.params["phi"],
                max_item_relevance=self.params["max_item_relevance"],
                I_scale=self.params['I_scale'],
                x_0 = self.params["x_0"],
                x_s = self.params["x_s"],
                story_nodes=list(self.story_graph.nodes()),
                seed_adoptions = story_nodes[:self.params['seed']],
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
            "phi": config.getfloat("DEFAULT","phi"),
            "max_item_relevance": config.getfloat("DEFAULT", "max_item_relevance"),
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
        print(f"Running {num_trials} trials.")
        for trial in range(num_trials):
            print(".",end="")
            self._initialize_agents()  # Reinitialize agents with new seed stories for each trial
            relevant_items = dict()
            for timestep in range(self.params["N"]):


                # Temporary structure to store adoption decisions
                adoption_decisions = {}  # Temporary structure to store adoption decisions

                relevant_items.update({item:timestep for item in self.broadcast_schedule.get(timestep, [])})
                #print(f"Relevant items are: {relevant_items}")
                # Step 1: Collect Decisions
                for story_item in self.story_graph.nodes():
                    if story_item in relevant_items and timestep - relevant_items[story_item] > self.params['max_item_relevance']:
                        del relevant_items[story_item]
                    
                    for agent_id, data in self.social_graph.nodes(data=True):
                        agent = data['agent']
                        if agent_id not in adoption_decisions:
                            adoption_decisions[agent_id] = {}
                        
                        if story_item not in relevant_items:
                            #print(f"Not relevant: {story_item}")
                            adoption_decisions[agent_id][story_item] = (agent.adoption_status(story_item),0,0,0)
                        else:
                            item_age = timestep - relevant_items[story_item]
                            #print(f"Relevant: {story_item} - age {item_age}")
                            
                            adopt, prob, W, I = agent.decide_adoption(story_item, item_age, self.story_graph, self.social_graph)
                            adoption_decisions[agent_id][story_item] = (adopt, prob, W, I)

                # Step 2: Apply Decisions
                for agent_id, decisions in adoption_decisions.items():
                    for story_item, (adopt, _, _, _) in decisions.items():
                        if adopt:
                            self.social_graph.nodes[agent_id]['agent'].adopted_items[story_item] = True

                # Record results after decisions are applied
                for agent_id, decisions in adoption_decisions.items():
                    for story_item, (adopt, prob, W, I) in decisions.items():
                        self.results.append({'agent': agent_id, 'timestep': timestep, 'story_item': story_item, 'adopted': adopt, 
                                             'prob': prob, 'Narrative': W, "Social": I, "Trial": trial})


                # Check if all items are adopted
                all_adopted = all([data['agent'].all_adopted() for _, data in self.social_graph.nodes(data=True)])
                if all_adopted:
                    break

        self.save_results()

    def save_results(self):
        """Save the results, parameters, networks, and agent alignments."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        directory = f"data/{self.params['filestub']}_{timestamp}"
        
        # Create the directory
        os.makedirs(directory, exist_ok=True)

        # # Save results
        # start = time.time()
        # df = pd.DataFrame(self.results)
        # print(f"Created dataframe in {time.time()-start} seconds")
        
        # start = time.time()
        # df.to_feather(os.path.join(directory, "results.feather"), index=False)
        # print(f"Wrote file in {time.time()-start} seconds")

        with open(os.path.join(directory, "results.pkl"), 'wb') as file:
            pickle.dump(self.results, file)
        
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
        
