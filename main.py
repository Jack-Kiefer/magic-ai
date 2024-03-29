import random
import game
import itertools


# card advantage, mana advantage
def scoreAttack(attackCombos, defender):
    mana = 0
    cards = 0
    life = 0
    for attacker, blockers in attackCombos:
        if blockers == []:
            life += attacker.power
        else:
            damage = attacker.power
            i = 0
            while i < len(blockers) and blockers[i].toughness <= damage:
                damage -= blockers[i].toughness
                cards += 1
                mana += blockers[i].cost
                i += 1
            if attacker.toughness <= sum([blocker.power for blocker in blockers]):
                cards -= 1
                mana -= attacker.cost
    return score(mana, cards, life, defender.life)


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


def score(mana, cards, life, defenderLife):
    if defenderLife - life <= 0 :
        return 1000
    return life * (10 / (defenderLife - life)) + 3 * cards + 2 * mana


def calculateWorstBlock(attackers, blockers, defender):
    n = len(attackers)  # Number of attackers
    m = len(blockers)  # Number of blockers

    # Generate all possible blocking combinations
    blocking_combinations = itertools.product(range(n + 1), repeat=m)

    all_blocking_pairs = []

    # Interpret each combination
    for combo in blocking_combinations:
        attacker_blockers = {attacker: [] for attacker in attackers}

        # Assign blockers based on the combination
        for blocker_index, attacker_index in enumerate(combo):
            if attacker_index < n:  # This blocker is blocking an attacker
                attacker = attackers[attacker_index]
                attacker_blockers[attacker].append(blockers[blocker_index])

        # Create the (attacker, list of blockers) pairs
        blocking_pairs = []
        for attacker in attackers:
            blockers_assigned = attacker_blockers[attacker]
            blocking_pairs.append((attacker, blockers_assigned if blockers_assigned else []))

        all_blocking_pairs.append((scoreAttack(blocking_pairs, defender), blocking_pairs))
    return min(all_blocking_pairs, key=lambda p: p[0])


def chooseAttackersAndBlockers(player1, player2):
    untap1 = player1.untappedCreatures()
    untap2 = player2.untappedCreatures()
    possibleAttacks = list(itertools.chain.from_iterable(itertools.combinations(untap1, r) for r in range(len(untap1) + 1)))
    result = max(
        [(calculateWorstBlock(attackers, untap2, player2), attackers) for attackers in possibleAttacks],
        key=lambda p: p[0][0]  # Compare based on the score part of the tuple returned by calculateWorstBlock
    )
    return result[0][1]


def runTurn(player1, player2):
    player1.startTurn()
    blocks = chooseAttackersAndBlockers(player1, player2)
    for attacker, blockers in blocks:
        print(f"{player1.name} attacks with {attacker.name}")
        player1.resolveAttack(attacker, blockers)
        player2.resolveBlock(attacker, blockers)
    for card in player1.hand:
        player1.playCard(card)


if __name__ == "__main__":
    deck1 = create_mono_green_deck()
    deck2 = create_mono_green_deck()
    gameState1 = game.GameState(deck1, "Johnny", 5)
    gameState2 = game.GameState(deck2, "                                                            Timmy", 6)
    playerTurn = 1
    turn = 1
    while gameState1.life > 0 and gameState2.life > 0:
        if playerTurn == 1:
            print(
                f"Starting turn {turn}, {gameState1.name} Life Total: {gameState1.life}, {gameState2.name} Life Total: {gameState2.life}")
            runTurn(gameState1, gameState2)
            playerTurn = 0
        else:
            runTurn(gameState2, gameState1)
            playerTurn = 1
            turn += 1
    print(gameState1.life, gameState2.life)
