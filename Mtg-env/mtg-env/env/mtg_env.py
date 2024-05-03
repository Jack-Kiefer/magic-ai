import functools
from copy import copy

import numpy as np
from gymnasium.spaces import Discrete, MultiDiscrete
from pettingzoo.utils import wrappers

import rungame
import game

from pettingzoo import AECEnv


def flatten(matrix):
    flat_set = set()
    for row in matrix:
        flat_set = flat_set.union(set(row))
    return flat_set

def env(**kwargs):
    env = raw_env(**kwargs)
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env


class raw_env(AECEnv):
    metadata = {
        "render_modes": ["human", "rgb_array"],
        "name": "mtg_env_v0",
        "is_parallelizable": False,
        "render_fps": 2,
    }

    def __init__(self):
        super().__init__()
        self.observations = None
        self.state = game.GameState([rungame.create_mono_green_deck(), rungame.create_mono_green_deck()])
        self._agent_selector = None
        self.agent_selection = None
        self.possible_agents = [0, 1]
        self.agents = [0, 1]

        self.num_distinct_creatures = 16
        self.num_distinct_cards = 17
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

        max_values = np.array([29] + [3] * 4 * self.num_distinct_creatures + 2*[29] + [21] + [21] + [2])
        self._observation_spaces = {
            agent: MultiDiscrete(max_values)
            for agent in self.agents
        }
        self.reset()

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

        self.observations = {agent: self.observe(agent)["observation"] for agent in self.agents}

    def generate_action_mask(self, agent):
        # No legal action if not your play
        if self.state.priority != agent:
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
                # if there is an element in the creatures that has the same name, is not untapped, not summoning_sick, and not already attacking
                # need to care if creatures are tapped / summoning sick
                for creature in self.state.creatures[agent]:
                    if all([
                        creature == self.distinct_creatures[i],
                        not creature.tapped,
                        not creature.summoning_sick,
                    ]):
                        mask[i + last] = 1

        last += self.num_distinct_creatures
        if self.state.phase == 2:
            for i in range(self.num_distinct_creatures):
                for j in range(self.num_distinct_creatures):
                    if all([
                        self.distinct_creatures[i] in self.state.attackingCreatures,
                        self.distinct_creatures[j] in self.state.untappedCreatures(agent),
                    ]):
                        mask[j + self.num_distinct_creatures*i+ last] = 1
        return mask

    def mask_to_action(self, action):
        if action == 0:
            return "pass_priority", 0
        action -= 1  # Adjust index to start at 0 for actions following pass_priority

        if action < self.num_distinct_cards:
            return "play_card", action  # Direct mapping for play card actions

        action -= self.num_distinct_cards  # Adjust index for creature actions

        if action < self.num_distinct_creatures:
            return "attack", action  # Each creature has a unique index for attack

        action -= self.num_distinct_creatures  # Adjust index for block actions

        # For block actions, you need to determine the attacker and blocker index
        # Assuming a linear mapping: attacker_index * num_creatures + blocker_index
        attacker_index = action // self.num_distinct_creatures
        blocker_index = action % self.num_distinct_creatures
        return "block", (attacker_index, blocker_index)

    def convert_to_multidiscrete(self, cards, total_cards):
        obs = np.zeros(len(total_cards), dtype=int)
        for card in cards:
            index = total_cards.index(card)
            obs[index] += 1
        return obs

    def observe(self, agent):
        obs = np.concatenate([
            self.convert_to_multidiscrete(self.state.hands[agent], self.distinct_cards),
            self.convert_to_multidiscrete(self.state.creatures[agent], self.distinct_creatures),
            self.convert_to_multidiscrete(self.state.creatures[1 - agent], self.distinct_creatures),
            self.convert_to_multidiscrete(self.state.attackingCreatures, self.distinct_creatures),
            np.array([self.state.totalLands[agent], self.state.untappedLands[agent], self.state.life[agent], self.state.life[1 - agent], self.state.turn == agent],
                     dtype=np.float32)
        ])
        return {"observation":obs.astype(np.float32), "action_mask":self.generate_action_mask(agent)}

    def step(self, action):
        # self.render()
        action_type, action_index = self.mask_to_action(action)
        pl = self.state.priority
        if action_type == "pass_priority":
            reward = self.state.passPriority(pl)
            self.rewards[pl] += reward
            self.rewards[1-pl] -= reward
        elif action_type == "play_card":
            self.state.playCard(copy(self.distinct_cards[action_index]), pl)
            self.rewards[pl] += 5
        elif action_type == "attack":
            attacker = next((c for c in self.state.creatures[pl] if c.name == self.distinct_creatures[action_index].name))
            self.state.addAttacker(pl, attacker)
        elif action_type == "block":
            attacker, blocker = action_index
            attacker = next((c for c in self.state.attackingCreatures if c.name == self.distinct_creatures[attacker].name))
            blocker = next((c for c in self.state.creatures[pl] if c.name == self.distinct_creatures[blocker].name))
            self.state.addBlocker(pl, attacker, blocker)
        if self.state.life[pl] <= 0 or len(self.state.decks[pl]) == 0:
            self.rewards[pl] -= 500
            self.rewards[1 - pl] += 500
            self.terminations = {0: True, 1: True}
            self._accumulate_rewards()
            if (pl == 1):
                print("Loss")
                print(f"My reward {self._cumulative_rewards[1]}, their reward {self._cumulative_rewards[0]}")
            else:
                print("Win")
                print(f"My reward {self._cumulative_rewards[1]}, their reward {self._cumulative_rewards[0]}")
            self.reset()
        if self.state.life[1 - pl] <= 0 or len(self.state.decks[1-pl]) == 0:
            self.rewards[1 - pl] = -1
            self.rewards[pl] = 1
            self.terminations = {0: True, 1: True}
            self._accumulate_rewards()
            self.reset()
            # if (pl == 1):
            #     print("Loss1")
            # else:
            #     print("Win1")
        self.observations = {agent: self.observe(agent) for agent in self.agents}
        self.infos = {agent: {"action_mask": self.generate_action_mask(agent)} for agent in self.agents}
        self._agent_selector = self.state.priority
        self.agent_selection = self.state.priority
        self._accumulate_rewards()
        self.rewards = {agent: 0 for agent in self.agents}

    def render(self, mode='human'):
        pass

    def close(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self._observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self._action_spaces[agent]
