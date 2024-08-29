Magic AI
Magic AI is a project designed to train agents to play a custom Magic: The Gathering environment using reinforcement learning. The environment leverages PettingZoo, a library for multi-agent reinforcement learning environments, and Stable-Baselines3 (SB3) to implement training with action masking.

Table of Contents
Overview
Features
Installation
Usage
Environment Details
Training
Acknowledgements
Overview
The Magic AI project simulates a Magic: The Gathering environment where agents are trained to play against each other using reinforcement learning. This environment is set up using the PettingZoo API, with SB3 for training the agents. Action masking is implemented to handle invalid actions, making the training process more efficient and effective.

Features
Custom Magic: The Gathering environment using PettingZoo.
Action masking for handling invalid actions during training.
Integration with SB3 for reinforcement learning.
Custom reward functions to optimize gameplay strategy.
Installation
To run this project, you need to have Python installed. The project dependencies are listed in the requirements.txt file. You can install the necessary packages using pip:

bash
Copy code
pip install -r requirements.txt
This will install all the required packages, including PettingZoo, Stable-Baselines3, and other dependencies.

Usage
Setup the Environment: Make sure all dependencies are installed using the command above.

Running the Training Script: The main training script is train.py, which initializes the environment, sets up the reward function, and trains the agent.

To start training, run:

bash
Copy code
python train.py
This will initiate the training process using the MaskablePPO algorithm from SB3, with action masking enabled.

Play Against the AI: After training, you can use the play_game.py script to interact with the trained agent. This script allows you to test the AI's performance in a simulated game environment.

Environment Details
The environment is defined in mtg_env_v0.py, which creates a custom multi-agent environment for Magic: The Gathering using PettingZoo. Key components include:

Deck Initialization: Decks are created using functions from deck.py.
Game Logic: The logic for handling game states, actions, and transitions is defined in game.py and logic.py.
Rendering: The game state can be rendered using render_game.py.
Action Masking
Action masking is implemented using a custom wrapper class SB3ActionMaskWrapper to integrate PettingZoo environments with SB3's masking functionality. This prevents agents from selecting invalid actions, thereby improving learning efficiency.

Reward Function
The reward function is defined in train.py as rewardFn. It calculates rewards based on the agent's life, mana, and cards, providing feedback that helps the agent learn optimal strategies.

Training
The training process utilizes the MaskablePPO algorithm from SB3, allowing the agent to learn over time by simulating thousands of games. The training script automatically saves the model after training, which can then be loaded for further evaluation or gameplay.

Acknowledgements
PettingZoo: For providing a robust API for multi-agent reinforcement learning environments.
Stable-Baselines3: For the reinforcement learning algorithms and the MaskablePPO implementation.
This README provides a basic overview of the project setup and usage. For more detailed information, refer to the code comments and documentation links provided within the scripts.