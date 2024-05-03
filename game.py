import random
from collections import defaultdict

import numpy as np
def flatten(matrix):
    flat_set = set()
    for row in matrix:
        flat_set = flat_set.union(set(row))
    return flat_set

class MagicCard:
    def __init__(self, name, cost, image_path):
        self.name = name
        self.cost = cost
        self.image_path = image_path

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Creature(MagicCard):
    def __init__(self, name, cost, image_path, power, toughness):
        super().__init__(name, cost, image_path)
        self.power = power
        self.toughness = toughness
        self.tapped = False
        self.summoning_sick = True

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False

    def __eq__(self, other):
        if isinstance(other, Creature):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)


class Land(MagicCard):
    def __init__(self, name, image_path):
        super().__init__(name, None, image_path)
        self.tapped = False


class GameState:
    def __init__(self, decks):
        self.decks = decks
        self.hands = [[], []]
        self.life = [20, 20]
        self.untappedLands = [0, 0]
        self.totalLands = [0, 0]
        self.creatures = [[], []]
        self.landDrops = [1, 1]
        self.attacks = [1, 1]
        self.attackingCreatures = []
        self.blockingCreatures = []
        self.shuffleDeck(0)
        self.shuffleDeck(1)
        self.drawCards(7, 0)
        self.drawCards(7, 1)
        self.turn = random.choice([0, 1])
        self.priority = self.turn
        # 'main1', 'declare_attackers', 'declare_blockers', 'main2'
        self.phase = 0

    def addBlocker(self, pl, attacker, blocker):
        self.creatures[pl].remove(blocker)
        i = next((index for index, creature in enumerate(self.blockingCreatures) if creature[0] == attacker))
        self.blockingCreatures[i][1].append(blocker)

    def addAttacker(self, pl, attacker):
        self.creatures[pl].remove(attacker)
        self.attackingCreatures.append(attacker)

    def declareAttack(self):
        for attacker in self.attackingCreatures:
            attacker.tap()
        self.blockingCreatures = [[attacker,[]] for attacker in self.attackingCreatures]

    def declareBlock(self, pl):
        reward = 0
        for i in range(len(self.blockingCreatures)):
            reward += self.resolveAttack(i, 1 - pl)
        self.creatures[1-pl] += self.attackingCreatures
        self.creatures[pl] += flatten(map(lambda x : x[1], self.blockingCreatures))
        self.attackingCreatures = []
        self.blockingCreatures = []
        self.phase = 3
        return reward

    def passPriority(self, pl):
        reward = 0
        if pl == self.turn:
            if self.phase == 0:
                self.phase += 1
            elif self.phase == 1:
                if not self.attackingCreatures:
                    self.phase = 3
                else:
                    self.declareAttack()
                    self.phase = 2
                    self.priority = 1 - self.priority
            elif self.phase == 3:
                self.turn = 1 - self.turn
                self.startTurn(self.turn)
        else:
            if self.phase == 2:
                reward = self.declareBlock(pl)
                self.priority = 1 - self.priority
        return reward

    def playCard(self, card, pl):
        if card in self.hands[pl]:
            if isinstance(card, Creature) and card.cost <= self.untappedLands[pl]:
                self.untappedLands[pl] -= card.cost
                self.creatures[pl].append(card)
                self.hands[pl].remove(card)
                # print(f'{self.name} plays {card.name}')
            elif isinstance(card, Land) and self.landDrops[pl] > 0:
                self.untappedLands[pl] += 1
                self.totalLands[pl] += 1
                self.landDrops[pl] -= 1
                self.hands[pl].remove(card)
                # print(f'{self.name} plays {card.name}')

    def shuffleDeck(self, pl):
        random.shuffle(self.decks[pl])

    def drawCards(self, n, pl):
        if self.decks[pl] == []:
            self.life = 0
            return
        for _ in range(n):
            self.hands[pl].append(self.decks[pl].pop())

    def rewardFn(self, life, mana, cards, pl):
        if self.life[1-pl] <= 0:
            return -100
        else:
            # life * (10 / self.life[1 - pl])
            return life * (10 / self.life[1 - pl]) + 50 * cards + 2 * mana

    def resolveAttack(self, i, pl):
        attacker, blockers = self.blockingCreatures[i]
        life, mana, cards = 0, 0, 0
        if len(blockers) == 0:
            self.life[1 - pl] -= attacker.power
            life -= attacker.power
        else:
            damage = attacker.power
            if blockers != [] and attacker.toughness <= sum([blocker.power for blocker in blockers]):
                mana += attacker.cost
                cards += 1
                self.attackingCreatures.remove(attacker)
            while len(blockers) > 0 and blockers[0].toughness <= damage:
                mana -= blockers[0].cost
                cards -= 1
                damage -= blockers[0].toughness
                blockers.remove(blockers[0])
        return self.rewardFn(life, mana, cards, pl)

    def untappedCreatures(self, pl):
        return [creature for creature in self.creatures[pl] if not creature.tapped]

    def startTurn(self, pl):
        self.drawCards(1, pl)
        self.untappedLands[pl] = self.totalLands[pl]
        self.landDrops[pl] = 1
        self.blockingCreatures = []
        self.priority = self.turn
        self.phase = 0
        for creature in self.creatures[pl]:
            creature.untap()
            creature.summoning_sick = False
