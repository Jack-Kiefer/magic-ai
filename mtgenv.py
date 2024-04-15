import gym
from gym import spaces
import numpy as np
import random
import game
import rungame
from gym.spaces import Tuple, Discrete, MultiBinary, MultiDiscrete, Dict
from gym.spaces.utils import flatten, unflatten
from playerAPI import playerAPI
class MTGEnv(gym.Env):
    def __init__(self):
        def __init__(self):
            super(MTGEnv, self).__init__()
            self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])

            # Define action spaces
            self.num_cards = 60  # Assume the deck has 60 cards
            self.num_creatures = 20  # Assume up to 20 creatures can be in play
            self.num_distinct_cards = 17
            self.num_attackers = 20

            # Action space includes choosing a card to play, attacking options, blocking options
            self.action_space = Dict({
                "play_card": Discrete(self.num_distinct_cards + 1),
                "attackers": MultiBinary(self.num_creatures),
                "blockers": MultiDiscrete([self.num_creatures+1]*self.num_attackers),
                "player": Discrete(2)
            })

            self.observation_space = Dict({
                "hand": MultiBinary(self.num_cards),  # Representation of the hand
                "creatures": MultiBinary(self.num_cards),
                "opponent_creatures": MultiBinary(self.num_cards),
                "lands": spaces.Discrete(20),
                "life": spaces.Discrete(21),
                "opponent_life": spaces.Discrete(21)
            })

    def reset(self):
        self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])
        return self._get_obs()


    def _get_obs(self, pl):
        obs = {
            "hand": self.state.hands[pl],
            "creatures": self.state.creatures[pl],
            "opponent_creatures": self.state.creatures[1 - pl],
            "lands": self.state.totalLands[pl],
            "life": self.state.life[pl],
            "opponent_life": self.state.life[pl]
        }
        return obs


    def step(self, action, pl):
        # Unpack the action tuple
        card_to_play, attackers, blockers = action

        # Process the action in the game logic
        reward, done = self.state(card_to_play, attackers, blockers)

        # Get the new observation after the action
        obs = self._get_obs()

        # Additional info could include more details about the state if necessary
        info = {}

        return obs, reward, done, info



    def render(self, mode='human'):
        pass
