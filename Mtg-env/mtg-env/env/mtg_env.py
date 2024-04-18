import functools
from copy import copy

import numpy as np
from gymnasium.spaces import Discrete, MultiDiscrete

import rungame
import game

from pettingzoo import AECEnv


def flatten(matrix):
    flat_set = set()
    for row in matrix:
        flat_set = flat_set.union(set(row))
    return flat_set


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

        max_values = np.array([25] + [3] * 3 * self.num_distinct_creatures + [29] + [21] + [21])
        self._observation_spaces = {
            agent: MultiDiscrete(max_values)
            for agent in self.agents
        }
        self.reset()

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
                        creature not in self.state.attackingCreatures
                    ]):
                        mask[i + last] = 1

        last += self.num_distinct_creatures
        if self.state.phase == 2:
            # print(self.state.attackingCreatures)
            # print(self.state.untappedCreatures(agent))
            # print(self.state.blockingCreatures)
            for i in range(self.num_distinct_creatures):
                for j in range(self.num_distinct_creatures):
                    if all([
                        self.distinct_creatures[i] in self.state.attackingCreatures,
                        self.distinct_creatures[j] in self.state.untappedCreatures(agent),
                        self.distinct_creatures[j] not in flatten([*self.state.blockingCreatures.values()])
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
            index = total_cards.index(card)
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
        # self.render()
        action_type, action_index = self.mask_to_action(action)
        pl = self.state.priority
        if action_type == "pass_priority":
            self.state.passPriority(pl)
        elif action_type == "play_card":
            self.state.playCard(self.distinct_cards[action_index], pl)
        elif action_type == "attack":
            attacker = next((c for c in self.state.creatures[pl] if c.name == self.distinct_creatures[action_index].name))
            self.state.addAttacker(attacker)
        elif action_type == "block":
            attacker, blocker = action_index
            # print(self.distinct_creatures[attacker].name, self.distinct_creatures[blocker].name)
            # print(self.state.creatures[1 - pl], self.state.creatures[pl])
            attacker = next((c for c in self.state.creatures[1 - pl] if c.name == self.distinct_creatures[attacker].name))
            blocker = next((c for c in self.state.creatures[pl] if c.name == self.distinct_creatures[blocker].name))
            self.state.addBlocker(attacker, blocker)
        if self.state.life[pl] <= 0 or len(self.state.decks[pl]) == 0:
            self.rewards[pl] += -1
            self.rewards[1 - pl] += 1
            self.terminations = {0: True, 1: True}
            self._accumulate_rewards()
            self.reset()
        if self.state.life[1 - pl] <= 0 or len(self.state.decks[1-pl]) == 0:
            self.rewards[1 - pl] = 1
            self.rewards[pl] = 0
            self.terminations = {0: True, 1: True}
            self._accumulate_rewards()
            self.reset()
        self.observations = {agent: self.observe(agent) for agent in self.agents}
        self.infos = {agent: {"action_mask": self.generate_action_mask(agent)} for agent in self.agents}
        self._agent_selector = self.state.priority
        self.agent_selection = self.state.priority

    def render(self, mode='human'):
        pass

    # def render(self):
    #     print(f"Current turn: Player {self.state.turn + 1}")
    #     print(f"Phase: {['Main phase 1', 'Declare attackers', 'Declare blockers', 'Main phase 2'][self.state.phase]}")
    #     print(f"Priority: Player {self.state.priority + 1}\n")
    #
    #     for agent in self.agents:
    #         player_label = f"Player {agent + 1} (Life: {self.state.life[agent]})"
    #         if self.state.priority == agent:
    #             player_label += " <- Priority"
    #         print(player_label)
    #
    #         lands_display = "Lands: [" + "U"*self.state.untappedLands[agent] + "T"*(self.state.totalLands[agent] - self.state.untappedLands[agent]) + "]"
    #         print(lands_display)
    #
    #         print("Hand: ", end="")
    #         if self.state.hands[agent]:
    #             print(", ".join([f"{card.name}" for card in self.state.hands[agent]]))
    #         else:
    #             print("Empty")
    #
    #         print("\nBoard:")
    #         if self.state.creatures[agent]:
    #             for creature in self.state.creatures[agent]:
    #                 status = "tapped" if creature.tapped else "untapped"
    #                 print(f"{creature.name} ({creature.power}/{creature.toughness}, {status})")
    #         else:
    #             print("No creatures on board")
    #
    #         print("\n")
    #
    #     print("Combat Zone:")
    #     if self.state.phase in [1, 2]:  # Attackers and blockers phase
    #         for attacker in self.state.attackingCreatures:
    #             blockers = self.state.blockingCreatures.get(attacker, [])
    #             if blockers:
    #                 blocker_names = ", ".join([blocker.name for blocker in blockers])
    #                 print(f"{attacker.name} (attacking) is blocked by {blocker_names}")
    #             else:
    #                 print(f"{attacker.name} (attacking) is unblocked")
    #
    #     print("\n" + "=" * 50 + "\n")

    def close(self):
        pass

    @functools.lru_cache(maxsize=None)
    def observation_space(self, agent):
        return self._observation_spaces[agent]

    @functools.lru_cache(maxsize=None)
    def action_space(self, agent):
        return self._action_spaces[agent]
