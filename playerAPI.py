import game
class playerAPI:
    def __init__(self, game, pl):
        self.game = game
        self.pl = pl

    def declareAttack(self, attackers):
        return self.game.declareAttack(attackers, self.pl)

    def declareBlock(self, blockers):
        return self.game.declareBlock(blockers, self.pl)

    def playCard(self, card):
        return self.game.playCard(card, self.pl)

    def passPriority(self):
        self.game.passPriority(self.pl)

    def getHand(self):
        return self.game.hands[self.pl]

    def getBoard(self):
        return self.game.hands[self.pl]



