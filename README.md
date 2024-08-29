# Magic AI

Magic AI is a project designed to train agents to play a custom Magic: The Gathering environment using reinforcement learning. The environment leverages PettingZoo, a library for multi-agent reinforcement learning environments, and Stable-Baselines3 (SB3) to implement training with action masking.

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Environment Details](#environment-details)
6. [Action and Observation Spaces](#action-and-observation-spaces)
7. [Training](#training)
8. [Acknowledgements](#acknowledgements)

## Overview

Magic AI simulates a Magic: The Gathering environment where agents are trained to play against each other using reinforcement learning. This environment is set up using the PettingZoo API, with SB3 for training the agents. Action masking is implemented to handle invalid actions, making the training process more efficient and effective.

## Features

- Custom Magic: The Gathering environment using PettingZoo.
- Action masking for handling invalid actions during training.
- Integration with SB3 for reinforcement learning.
- Custom reward functions to optimize gameplay strategy.
- Command-line flags for customizable training parameters (steps, seed, learning rate).
- Modes for playing against the AI or having the AI play autonomously.

## Installation

To run this project, you need to have Python installed. The project dependencies are listed in the `requirements.txt` file. You can install the necessary packages using pip:

```bash
pip install -r requirements.txt
```

This will install all the required packages, including PettingZoo, Stable-Baselines3, and other dependencies.

## Usage

1. **Setup the Environment**: Make sure all dependencies are installed using the command above.
2. **Running the Training Script**: The main training script is `train.py`, which initializes the environment, sets up the reward function, and trains the agent.

   To start training with default parameters, run:

   ```bash
   python train.py
   ```

   This will initiate the training process using the MaskablePPO algorithm from SB3, with action masking enabled.

   You can also customize training parameters using command-line flags:

   ```bash
   python train.py --steps 50000 --learning_rate 0.001
   ```

   - `--steps`: Number of training steps (default: 10,000).
   - `--learning_rate`: Initial learning rate for the training (default: 0.002).

3. **Playing Against the AI**: After training, you can use the `play_game.py` script to interact with the trained agent. This script allows you to test the AI's performance in a simulated game environment. You can specify whether to run in "human" mode (where you play against the AI) or "ai" mode (where AI plays against itself) using command-line flags:

   ```bash
   python play_game.py --mode human --speed 0.01
   ```

   - `--mode`: Set to `human` for human vs. AI mode or `ai` for AI vs. AI mode.
   - `--speed`: Number of seconds to wait between steps (default: 0.01).

## Environment Details

The environment is defined in `mtg_env_v0.py`, which creates a custom multi-agent environment for Magic: The Gathering using PettingZoo. Key components include:

- **Deck Initialization**: Decks are created using functions from `deck.py`.
- **Game Logic**: The logic for handling game states, actions, and transitions is defined in `game.py` and `logic.py`.
- **Rendering**: The game state can be rendered using `render_game.py`.

## Action and Observation Spaces

The Magic AI environment uses discrete and multi-discrete spaces to represent possible actions and observations:

### Action Space

The action space is defined using a `Discrete` space that allows agents to perform a variety of actions:

- **0**: Pass priority.
- **1-17**: Play a card from the hand.
- **18-33**: Attack with a creature.
- **34-289**: Block with a creature on another creature.

The size of the action space is calculated based on the number of unique cards and creatures, including combinations for attacking and blocking. This setup ensures that all possible actions in a Magic: The Gathering game are covered.

### Observation Space

The observation space is a `MultiDiscrete` space, which provides a comprehensive view of the game state for each agent. Key components include:

- **Hand and Deck Representation**: The number and type of cards in hand and deck.
- **Creatures in Play**: Information about creatures on the battlefield, their states (tapped/untapped), and any special conditions (e.g., summoning sickness).
- **Life Points**: Current life points of both players.
- **Mana Availability**: Number of lands in play and how many are untapped.
- **Game Phases**: Information about the current phase of the game.

These elements are encoded into a numerical format that agents can use to make informed decisions about their actions.

### Action Masking

Action masking is implemented to filter out invalid actions based on the current game state. This helps improve the training efficiency by preventing agents from selecting actions that are not possible or legal at a given time.

### Reward Function

The reward function is defined in `train.py` as `rewardFn`. It calculates rewards based on the agent's life, mana, and cards, providing feedback that helps the agent learn optimal strategies.

## Training

The training process utilizes the MaskablePPO algorithm from SB3, allowing the agent to learn over time by simulating thousands of games. The training script automatically saves the model after training, which can then be loaded for further evaluation or gameplay.

## Acknowledgements

- **PettingZoo**: For providing a robust API for multi-agent reinforcement learning environments.
- **Stable-Baselines3**: For the reinforcement learning algorithms and the MaskablePPO implementation.

---
