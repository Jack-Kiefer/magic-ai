import random
from collections import defaultdict


class MagicCard:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):

        return self.name == other.name


class Creature(MagicCard):
    def __init__(self, name, cost, power, toughness):
        super().__init__(name, cost)
        self.power = power
        self.toughness = toughness
        self.tapped = False

    def tap(self):
        self.tapped = True

    def untap(self):
        self.tapped = False


class Land(MagicCard):
    def __init__(self, name):
        super().__init__(name, None)
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
        self.blockingCreatures = defaultdict(lambda x : [])
        self.shuffleDeck(0)
        self.shuffleDeck(1)
        self.drawCards(7, 0)
        self.drawCards(7, 1)
        self.turn = random.choice([0,1])
        self.priority = self.turn
        # 'main1', 'declare_attackers', 'declare_blockers', 'main2'
        self.phase = 0
        self.attackers = []

    def addBlocker(self, attacker, blocker):
        self.blockingCreatures[attacker].append(blocker)
    def addAttacker(self, attacker):
        self.attackingCreatures.append(attacker)

    def declareAttack(self):
        for attacker in self.attackingCreatures:
            attacker.tap()
        self.blockingCreatures = [[attacker, []] for attacker in self.attackingCreatures]

    def declareBlock(self, pl):
        for attacker, blockers in self.blockingCreatures:
            self.resolveAttack(attacker, blockers, 1 - pl)
        self.phase = 3


    def passPriority(self, pl):
        if pl == self.turn:
            if self.phase == 0:
                self.phase += 1
            elif self.phase == 1:
                if self.attackingCreatures == []:
                    self.phase = 3
                else:
                    self.declareAttack()
                    self.phase = 2
                    self.priority = 1 - self.priority
            elif self.phase == 3:
                self.startTurn(self.turn)
        else:
            if self.phase == 2:
                self.declareBlock(pl)
                self.priority = 1 - self.priority



    def playCard(self, card, pl):
        if card in self.hands[pl]:
            if isinstance(card, Creature) and card.cost <= self.untappedLands:
                self.untappedLands -= card.cost
                self.creatures[pl].append(card)
                self.hands[pl].remove(card)
                # print(f'{self.name} plays {card.name}')
            elif isinstance(card, Land) and self.landDrops[pl] > 0:
                self.untappedLands += 1
                self.totalLands += 1
                self.landDrops -= 1
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


    def resolveAttack(self, attacker, blockers, pl):
        if len(blockers) == 0:
            # print(f"{self.name} doesn't block {attacker.name}")
            self.life[1 - pl] -= attacker.power
        else:
            # print(f"{self.name} blocks {attacker.name} with {blockers}")
            damage = attacker.power
            i = 0
            while i < len(blockers) and blockers[i].toughness <= damage:
                self.creatures[1 - pl].remove(blockers[i])
                damage -= blockers[i].toughness
                i += 1
            if blockers != [] and attacker.toughness <= sum([blocker.power for blocker in blockers]):
                self.creatures[pl].remove(attacker)

    def untappedCreatures(self, pl):
        return [creature for creature in self.creatures[pl] if not creature.tapped]

    def startTurn(self, pl):
        self.drawCards(1, pl)
        self.untappedLands[pl] = self.totalLands[pl]
        self.landDrops[pl] = 1
        self.attackingCreatures = []
        self.blockingCreatures = []
        self.turn = 1 - self.turn
        self.priority = self.turn
        for creature in self.creatures[pl]:
            creature.untap()