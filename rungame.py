import cProfile
import pstats
import random

import game
import logic

def generateDistinctCreatures():
    cards = []
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
    for i in range(16):
        cards.append(game.Creature(*green_creatures[i]))
    return cards
def generateDistinctCards():
    cards = []
    cards.append(game.Land("Forest"))
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
    for i in range(16):
        cards.append(game.Creature(*green_creatures[i]))
    return cards



def create_mono_green_deck():
    deck = []

    # Add 16 Forests
    for _ in range(28):
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
    return life * (10 / (defenderLife - life)) + 3 * cards + 2 * mana

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