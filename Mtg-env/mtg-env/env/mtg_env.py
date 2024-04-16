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
        self._agent_selector = None
        self.agent_selection = None
        self.possible_agents = [0, 1]
        self.agents = [0, 1]

        # Define action spaces
        self.num_cards = 60
        self.num_distinct_creatures = 16
        self.num_distinct_cards = 17
        self.cards = rungame.create_mono_green_deck()
        self.distinct_cards = rungame.generateDistinctCards()
        self.distinct_creatures = rungame.generateDistinctCreatures()
        self.creatures = rungame.generateCreatures()
        self.num_creatures = 32

        # action masking
        # 0 - pass priority
        # 1-17 - play card
        # 18-33 - attack with creature
        # 34-289 - block with creature on a creature
        # self.action_space = Discrete(1 + self.num_distinct_cards + self.num_distinct_creatures + self.num_distinct_creatures^2)
        self._action_spaces = {
            agent: Discrete(
                1 + self.num_distinct_cards + self.num_distinct_creatures + self.num_distinct_creatures ** 2)
            for agent in self.agents}

        max_values = np.array([25] + [3] * 3 * self.num_distinct_creatures + [25] + [21] + [21])
        self._observation_spaces = {
            agent: MultiDiscrete(max_values)
            for agent in self.agents
        }

    def generate_action_mask(self, agent):
        # No legal action if not your play
        if not self.state.priority:
            return np.zeros(self._action_spaces[agent].n, dtype=np.int8)
        mask = np.zeros(self._action_spaces[agent].n, dtype=np.int8)
        mask[0] = 1
        last = 1
        if self.state.phase in [0, 3]:
            for i in range(self.num_distinct_cards):
                card = self.distinct_cards[i]
                if (card in self.state.hands[agent] and
                        ((isinstance(card, game.Creature) and card.cost <= self.state.untappedLands[agent])
                         or (isinstance(card, game.Land) and self.state.landDrops[agent] > 0))):
                    mask[i + last] = 1
        last += self.num_distinct_cards
        if self.state.phase == 1:
            for i in range(self.num_distinct_creatures):
                # need to care if creatures are tapped / summoning sick
                if self.distinct_creatures[i] in self.state.creatures[agent]:
                    mask[i + last] = 1
        last += self.num_distinct_creatures
        if self.state.phase == 2:
            for i in range(self.num_distinct_creatures):
                for j in range(self.num_distinct_creatures):
                    if self.distinct_creatures[i] in self.state.attackers and self.distinct_creatures[
                        j] in self.state.untappedCreatures():
                        mask[i + last] = 1
        return mask

    def mask_to_action(self, action):
        action_index = 0
        c = action
        if c == 0:
            return "pass_priority", 0
        c -= 1
        if c < self.num_distinct_cards:
            return "play_card", c
        c -= self.num_distinct_cards
        if c < self.num_distinct_creatures:
            return "attack", action_index
        c -= self.num_distinct_creatures
        return "block", action_index

    def reset(self, seed=None, options=None):
        self.agents = copy(self.possible_agents)
        self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])
        self.rewards = {agent: 0 for agent in self.agents}
        self._cumulative_rewards = {agent: 0 for agent in self.agents}
        self.terminations = {agent: False for agent in self.agents}
        self.truncations = {a: False for a in self.agents}
        self.infos = {agent: {"action_mask": self.generate_action_mask(agent)} for agent in self.agents}
        self._agent_selector = self.state.priority
        self.agent_selection = self.state.priority

        self.observations = {agent: self.observe(agent) for agent in self.agents}

    def convert_to_multidiscrete(self, cards, total_cards):
        obs = np.zeros(len(total_cards), dtype=int)
        for card in cards:
            index = self.distinct_cards.index(card)
            obs[index] += 1
        return obs

    def observe(self, agent):
        return np.concatenate([
            self.convert_to_multidiscrete(self.state.hands[agent], self.distinct_cards),
            self.convert_to_multidiscrete(self.state.creatures[agent], self.distinct_creatures),
            self.convert_to_multidiscrete(self.state.creatures[1 - agent], self.distinct_creatures),
            np.array([self.state.totalLands[agent], self.state.life[agent], self.state.life[1 - agent]])
            ])

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
            self.rewards[1 - pl] += 1
        if self.state.life[1 - pl] <= 0:
            self.rewards[1 - pl] = 1
            self.rewards[pl] = 0
        self.terminations = {0: True, 1: True}
        self.observations = {agent: self.observe(agent) for agent in self.agents}
        self.infos = {agent: {"action_mask": self.generate_action_mask(agent)} for agent in self.agents}
        self._agent_selector = self.state.priority
        self._accumulate_rewards()

    def render(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self._observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self._action_spaces[agent]
