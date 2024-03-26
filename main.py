import random
import game


def create_mono_green_deck():
    deck = []

    # Add 16 Forests
    for _ in range(16):
        deck.append(game.Land("Forest"))

    green_creatures = [
        ("Woodland Druid", 1, 1, 2),
        ("Dryad Militant", 1, 2, 1),
        ("Grizzly Bears", 2, 2, 2),
        ("Terrian Elemental", 2, 3, 2),
        ("Winding Constrictor", 2, 2, 3),
        ("Wary Thespian", 2, 3, 1),
        ("Alpine Grizzly", 3, 4, 2),
        ("Centaur Courser", 3, 3, 3),
        ("Spined Karok", 3, 2, 4),
        ("Rumbling Baloth", 4, 4, 4),
        ("Axebane Beast", 4, 3, 4),
        ("Vine Mare", 4, 5, 3),
        ("Thornhide Wolves", 5, 4, 5),
        ("Craw Wurn", 6, 6, 5),
        ("Vastwood Gorger", 6, 5, 6),
        ("Axebane Stag", 7, 6, 7),
    ]
    for _ in range(24):
        creature = random.choice(green_creatures)
        deck.append(game.Creature(*creature))

    return deck


def runTurn(player1, player2):
    player1.startTurn()
    c1 = player1.untappedCreatures()
    c2 = player2.untappedCreatures()
    if len(c1) > 0:
        print(f"{player1.name} attacks with {c1}")
    for i in range(len(c1)):
        if i >= len(c2):
            player1.resolveAttack(c1[i], None)
            player2.resolveBlock(c1[i], None)
        else:
            player1.resolveAttack(c1[i], c2[i])
            player2.resolveBlock(c1[i], c2[i])
    for card in player1.hand:
        player1.playCard(card)


if __name__ == "__main__":
    deck1 = create_mono_green_deck()
    deck2 = create_mono_green_deck()
    gameState1 = game.GameState(deck1, "Johnny")
    gameState2 = game.GameState(deck2, "Timmy")
    playerturn = 1
    turn = 1
    while gameState1.life > 0 and gameState2.life > 0:
        if playerturn == 1:
            print(f"Starting turn {turn}")
            runTurn(gameState1, gameState2)
            playerturn = 0
        else:
            runTurn(gameState2, gameState1)
            playerturn = 1
            turn += 1
    print(gameState1.life, gameState2.life)
