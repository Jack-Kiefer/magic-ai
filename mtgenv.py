import gym
from gym import spaces
import numpy as np
import random
import game
import rungame
from gym.spaces import Tuple, Discrete, MultiBinary, MultiDiscrete
class MTGEnv(gym.Env):
    def __init__(self):
        def __init__(self):
            super(MTGEnv, self).__init__()

            # Define action spaces
            self.num_cards = 60  # Assume the deck has 60 cards
            self.num_creatures = 20  # Assume up to 20 creatures can be in play
            self.num_distinct_cards = 17
            self.num_attackers = 20

            # Action space includes choosing a card to play, attacking options, blocking options
            self.action_space = Tuple((
                Discrete(self.num_distinct_cards + 1),  # +1 for choosing not to play a card
                MultiBinary(self.num_creatures),  # Each bit represents a creature attacking
                MultiDiscrete([self.num_creatures+1]*self.num_attackers)  # Each bit represents a creature blocking another
            ))

            self.observation_space = spaces.Dict({
                "hand": MultiBinary(self.num_cards),  # Representation of the hand
                "creatures": MultiBinary(self.num_cards),
                "opponent_creatures": MultiBinary(self.num_cards),
                "lands": spaces.Discrete(20),
                "life": spaces.Discrete(21)
            })

            self.deck = rungame.create_mono_green_deck()
            self.state = game.GameState(self.deck, "AI Player", seed=0, scorefn=lambda x: x.life)

    def reset(self):
        self.state = game.GameState(self.deck, "AI Player", seed=random.randint(0, 1000), scorefn=lambda x: x.life)
        return self._get_obs()

    def _get_obs(self):
        # Simplified observation (one-hot encode hand and other elements)
        hand_representation = [0] * 40
        for card in self.state.hand:
            index = self.deck.index(card)
            hand_representation[index] = 1

        creature_info = np.zeros((20, 3))
        for i, creature in enumerate(self.state.creatures):
            creature_info[i] = [creature.power, creature.toughness, creature.tapped]

        return {
            "hand": np.array(hand_representation),
            "creatures": creature_info,
            "lands": self.state.totalLands,
            "life": self.state.life
        }

    def step(self, action):
        card = self.deck[action]  # Translate action to card
        self.state.playCard(card)
        done = self.state.life <= 0 or len(self.state.deck) == 0
        reward = self.state.scorefn(self.state)
        return self._get_obs(), reward, done, {}

    def render(self, mode='human'):
        print(f"Player Life: {self.state.life}")
        print("Hand:", self.state.hand)
        print("Creatures on Field:", self.state.creatures)

env = MTGEnv()