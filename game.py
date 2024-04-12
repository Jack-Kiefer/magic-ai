import random

class MagicCard:
    def __init__(self, name, cost):
        self.name = name
        self.cost = cost

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()


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
    def __init__(self, deck, name, seed, scorefn):
        self.deck = deck
        self.hand = []
        self.untappedLands = 0
        self.totalLands = 0
        self.creatures = []
        self.landDrops = 1
        self.attacks = 1
        self.life = 20
        self.shuffleDeck(seed)
        self.drawCards(7)
        self.name = name
        self.scorefn = scorefn

    def shuffleDeck(self, seed):
        if seed == 0:
            random.shuffle(self.deck)
        else:
            random.Random(seed).shuffle(self.deck)

    def drawCards(self, n):
        if self.deck == []:
            self.life = 0
            return
        for _ in range(n):
            self.hand.append(self.deck.pop())

    def playCard(self, card):
        if card in self.hand:
            if isinstance(card, Creature) and card.cost <= self.untappedLands:
                self.untappedLands -= card.cost
                self.creatures.append(card)
                self.hand.remove(card)
                # print(f'{self.name} plays {card.name}')
            elif isinstance(card, Land) and self.landDrops > 0:
                self.untappedLands += 1
                self.totalLands += 1
                self.landDrops -= 1
                self.hand.remove(card)
                # print(f'{self.name} plays {card.name}')

    def resolveBlock(self, attacker, blockers):
        if len(blockers) == 0:
            # print(f"{self.name} doesn't block {attacker.name}")
            self.life -= attacker.power
        else:
            # print(f"{self.name} blocks {attacker.name} with {blockers}")
            damage = attacker.power
            i = 0
            while i < len(blockers) and blockers[i].toughness <= damage:
                self.creatures.remove(blockers[i])
                damage -= blockers[i].toughness
                i += 1


    def resolveAttack(self, attacker, blockers):
        attacker.tap()
        if blockers != [] and attacker.toughness <= sum([blocker.power for blocker in blockers]):
            self.creatures.remove(attacker)

    def untappedCreatures(self):
        return [creature for creature in self.creatures if not creature.tapped]

    def startTurn(self):
        self.drawCards(1)
        self.untappedLands = self.totalLands
        self.landDrops = 1
        for creature in self.creatures:
            creature.untap()