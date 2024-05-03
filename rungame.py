import cProfile
import pstats
import random

import game
import logic

green_creatures = [
        ("Woodland Druid", 1, "images/woodland-druid.png", 1, 2),
        ("Dryad Militant", 1, "images/dryad-militant.png", 2, 1),
        ("Grizzly Bears", 2, "images/grizzly-bears.png", 2, 2),
        ("Terrian Elemental",2, "images/terrain-elemental.png", 3, 2),
        ("Winding Constrictor",2, "images/winding-constrictor.png", 2, 3),
        ("Wary Thespian", 2, "images/wary-thespian.png", 3, 1),
        ("Alpine Grizzly", 3, "images/alpine-grizzly.png", 4, 2),
        ("Centaur Courser", 3, "images/centaur-courser.png", 3, 3),
        ("Spined Karok", 3, "images/spined-karok.png", 2, 4),
        ("Rumbling Baloth", 4, "images/rumbling-baloth.png", 4, 4),
        ("Axebane Beast", 4, "images/axebane-beast.png", 3, 4),
        ("Vine Mare", 4, "images/vine-mare.png", 5, 3),
        ("Thornhide Wolves", 5, "images/thornhide-wolves.png", 4, 5),
        ("Craw Wurm", 6, "images/craw-wurm.png", 6, 4),
        ("Vastwood Gorger", 6, "images/vastwood-gorger.png", 5, 6),
        ("Axebane Stag", 7, "images/axebane-stag.png", 6, 7),
    ]

def generateDistinctCreatures():
    cards = []
    for i in range(16):
        cards.append(game.Creature(*green_creatures[i]))
    return cards
def generateDistinctCards():
    cards = []
    cards.append(game.Land("Forest", "images/forest.png"))
    for i in range(16):
        cards.append(game.Creature(*green_creatures[i]))
    return cards

def generateCreatures():
    cards = []
    for i in range(16):
        cards.append(game.Creature(*green_creatures[i]))
        cards.append(game.Creature(*green_creatures[i]))
    return cards

def create_mono_green_deck():
    deck = []

    # Add 16 Forests
    for _ in range(28):
        deck.append(game.Land("Forest", "images/forest.png"))
    for i in range(16):
        deck.append(game.Creature(*green_creatures[i]))
        deck.append(game.Creature(*green_creatures[i]))

    return deck

def runTurn(player1, player2, verbose):
    player1.startTurn()
    attackers = logic.chooseAttackers(player1, player2, )
    blockers = logic.calculateBlock(list(attackers), player2.untappedCreatures(), base_score, player2, 0)[1]
    for attacker, blockers in blockers:
        if verbose:
            print(f"{player1.name} attacks with {attacker.name}")
        player1.resolveAttack(attacker, blockers)
        player2.resolveBlock(attacker, blockers)
    for card in player1.hand:
        player1.playCard(card)

def base_score(mana, cards, life, defenderLife):
    if defenderLife - life <= 0:
        return 1000
    # life * (10 / (defenderLife - life))
    return life * (10 / (defenderLife - life)) + 30 * cards

def aggressive_score(mana, cards, life, defenderLife):
    # Prioritize attacking and reducing defender life
    return (100 - defenderLife) + mana + cards

def defensive_score(mana, cards, life, defenderLife):
    # Prioritize player life and card advantage
    return life + 2 * cards + 0.5 * mana

def runGame(scorefn1, scorefn2, verbose):
    deck1 = create_mono_green_deck()
    deck2 = create_mono_green_deck()
    # if seed = then it is random
    gameState1 = game.GameState(deck1, "Johnny",0, scorefn1)
    gameState2 = game.GameState(deck2, "                                                            Timmy", 0, scorefn2)
    playerTurn = random.randint(0, 1)
    turn = 1
    while gameState1.life > 0 and gameState2.life > 0:
        if playerTurn == 1:
            if verbose:
                print(
                    f"Starting turn {turn}, {gameState1.name} Life Total: {gameState1.life}, {gameState2.name} Life Total: {gameState2.life}")
            runTurn(gameState1, gameState2, verbose)
            playerTurn = 0
        else:
            runTurn(gameState2, gameState1, verbose)
            playerTurn = 1
            turn += 1
    if gameState1.life <= 0:
        return "Player 2 Win"
    else:
        return "Player 1 Win"

def main():
    for _ in range(1):
        print(runGame(defensive_score, base_score, False))



if __name__ == "__main__":
    # Run main() under the profiler, saving the stats to 'game_profile.stats'
    cProfile.run('main()', 'game_profile.stats')

    # Create a Stats object from the saved stats
    p = pstats.Stats('game_profile.stats')

    # Sort the statistics by the cumulative time spent in the function and print the top parts
    p.sort_stats('cumulative').print_stats(10)