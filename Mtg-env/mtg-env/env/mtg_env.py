import functools
from copy import copy

import numpy as np
from gymnasium.spaces import Discrete, Dict, MultiBinary, MultiDiscrete

import rungame
import game

from pettingzoo import AECEnv


class mtg_env(AECEnv):
    metadata = {
        "name": "mtg_env_v0",
    }

    def __init__(self):
        super().__init__()
        self.observations = None
        self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])
        self.possible_agents = [0, 1]
        self.agents = [0, 1]

        # Define action spaces
        self.num_cards = 60
        self.num_distinct_creatures = 16
        self.num_distinct_cards = 17
        self.distinct_cards = rungame.generateDistinctCards()
        self.distinct_creatures = rungame.generateDistinctCreatures()

        # action masking
        # 0 - pass priority
        # 1-17 - play card
        # 18-33 - attack with creature
        # 34-289 - block with creature on a creature
        # self.action_space = Discrete(1 + self.num_distinct_cards + self.num_distinct_creatures + self.num_distinct_creatures^2)
        self.action_spaces = {agent: Discrete(1 + self.num_distinct_cards + self.num_distinct_creatures + self.num_distinct_creatures^2) for agent in self.agents}

        self.observation_spaces = {agent: Dict({
            "hand": MultiBinary(self.num_cards),
            "creatures": MultiBinary(self.num_cards),
            "opponent_creatures": MultiBinary(self.num_cards),
            "lands": Discrete(20),
            "life": Discrete(21),
            "opponent_life": Discrete(21)
        }) for agent in self.agents}

    def generate_action_mask(self, pl):
        # No legal action if not your play
        if not self.state.priority:
            return None
        mask = [0]*self.action_space.n
        mask[0] = 1
        last = 1
        if self.state.phase in [0, 3]:
            for i in range(self.num_distinct_cards):
                card = self.distinct_cards[i]
                if (card in self.state.hands[pl] and
                        ((isinstance(card,game.Creature) and card.cost <= self.state.untappedLands[pl])
                         or (isinstance(card,game.Land) and self.state.landDrops[pl] > 0))):
                    mask[i+last] = 1
        last += self.num_distinct_cards
        if self.state.phase == 1:
            for i in range(self.num_distinct_creatures):
                # need to care if creatures are tapped / summoning sick
                if self.distinct_creatures[i] in self.state.creatures[pl]:
                    mask[i+last] = 1
        last += self.num_distinct_creatures
        if self.state.phase == 2:
            for i in range(self.num_distinct_creatures):
                for j in range(self.num_distinct_creatures):
                    if self.distinct_creatures[i] in self.state.attackers and self.distinct_creatures[j] in self.state.untappedCreatures():
                        mask[i + last] = 1
        return mask

    def mask_to_action(self, action):
        action_type = ""
        action_index = 0
        c = action
        if c == 0:
            action_type = "pass_priority"
            return action_type, 0
        c -= 1
        if c < self.num_distinct_cards:
            action_type = "play_card"
            return action_type, c
        c -= self.num_distinct_cards
        if c < self.num_distinct_creatures:
            action_type = "attack"
            return action_type, action_index
        c -= self.num_distinct_creatures
        action_type = "block"
        return action_type, action_index

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {a: False for a in self.agents}
        self.infos = {agent: {} for agent in self.agents}

        self.agent_selection = self.state.priority
        self.observations = {agent: self.observe(agent) for agent in self.agents}

    def observe(self, agent):
        return {
            "hand": self.state.hands[agent],
            "creatures": self.state.creatures[agent],
            "opponent_creatures": self.state.creatures[1 - agent],
            "lands": self.state.totalLands[agent],
            "life": self.state.life[agent],
            "opponent_life": self.state.life[1 - agent]
        }


    def step(self, action):
        action_type, action_index = self.mask_to_action(action)
        pl = self.state.priority
        if action_type == "pass_priority":
            self.state.passPriority(pl)
        elif action_type == "play_card":
            self.state.playCard(self.distinct_cards[action_index], pl)
        elif action_type == "attack":
            self.state.addAttacker(self.distinct_creatures[action_index])
        elif action_type == "block":
            attacker_index = action_index % self.num_distinct_creatures
            blocker_index = action_index // self.num_distinct_creatures
            self.state.addBlocker(self.distinct_creatures[attacker_index], self.distinct_creatures[blocker_index])
        if self.state.life[pl] <= 0:
            self.rewards[pl] += -1
            self.rewards[1-pl] += 1
        if self.state.life[1 - pl] <= 0:
            self.rewards[1 - pl] = 1
            self.rewards[pl] = 0
        self.terminations = {0:True, 1:True}
        self.observations = {agent: self.observe(agent) for agent in self.agents}
        self._accumulate_rewards()



    def render(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self.action_spaces[agent]
