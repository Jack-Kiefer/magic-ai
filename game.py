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
    def __init__(self, deck, name):
        self.deck = deck
        self.hand = []
        self.untappedLands = 0
        self.totalLands = 0
        self.creatures = []
        self.landDrops = 1
        self.attacks = 1
        self.life = 20
        self.shuffleDeck()
        self.drawCards(7)
        self.name = name

    def shuffleDeck(self):
        random.shuffle(self.deck)

    def drawCards(self, n):
        for _ in range(n):
            self.hand.append(self.deck.pop())

    def playCard(self, card):
        if card in self.hand:
            if isinstance(card, Creature) and card.cost <= self.untappedLands:
                self.untappedLands -= card.cost
                self.creatures.append(card)
                self.hand.remove(card)
                print(f'{self.name} plays {card.name}')
            elif isinstance(card, Land) and self.landDrops > 0:
                self.untappedLands += 1
                self.totalLands += 1
                self.landDrops -= 1
                self.hand.remove(card)
                print(f'{self.name} plays {card.name}')

    def resolveBlock(self, attacker, blocker):
        if blocker is None:
            print(f"{self.name} doesn't block {attacker.name}")
            self.life -= attacker.power
        elif blocker.toughness <= attacker.power:
            print(f"{self.name} blocks {attacker.name} with {blocker.name}")
            self.creatures.remove(blocker)

    def resolveAttack(self, attacker, blocker):
        attacker.tap()
        if blocker is not None and attacker.toughness <= blocker.power:
            self.creatures.remove(attacker)

    def untappedCreatures(self):
        return [creature for creature in self.creatures if not creature.tapped]

    def startTurn(self):
        self.drawCards(1)
        self.untappedLands = self.totalLands
        self.landDrops = 1
        for creature in self.creatures:
            creature.untap()