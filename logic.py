import copy
import random
import game
import itertools
from functools import lru_cache

'''
Inputs: Attacker and tuple of blockers
Outputs: Score of the attack
'''


@lru_cache(maxsize=None)
def scoreAttackCombo(attacker, blockers):
    mana = 0
    cards = 0
    life = 0
    if not blockers:
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
    return mana, cards, life


'''
Inputs: List of tuples of attacker and blocker combos, defender GameState, score function
Outputs: Score of the attack
'''
def scoreAttack(attackCombos, defender, scorefn):
    mana = 0
    cards = 0
    life = 0
    for attacker, blockers in attackCombos:
        dmana, dcards, dlife = scoreAttackCombo(attacker, blockers)
        mana += dmana
        cards += dcards
        life += dlife
    return scorefn(mana, cards, life, defender.life)


# '''
# Inputs: List of attackers, defender GameState, score function
# Outputs: Tuple of (score of minimum score blocking combination, minimum score blocking combination)
# '''
def calculateBlock(attackers, blockers, attackPlayer, defendPlayer, k):

    if k > len(blockers):
        return scoreAttack([(attacker, tuple()) for attacker in attackers], defendPlayer, attackPlayer.scorefn), [(attacker, tuple())                                                                                                           for attacker in
                                                                                                           attackers]
    attackersCopy = copy.copy(attackers)
    blockersCopy = copy.copy(blockers)
    totalScore = 0
    blockCombos = []

    for attacker in attackers:
        bestScore = 1000000
        bestBlock = None
        for blockers_combination in itertools.combinations(blockersCopy, k):
            mana, cards, life = scoreAttackCombo(attacker, blockers_combination)
            score = attackPlayer.scorefn(mana, cards, life, defendPlayer.life)

            if score < bestScore:
                bestScore = score
                bestBlock = blockers_combination

        if bestScore < scoreAttack([(attacker, tuple())], defendPlayer, attackPlayer.scorefn):
            totalScore += bestScore
            for blocker in bestBlock:
                blockersCopy.remove(blocker)
            attackersCopy.remove(attacker)
            blockCombos.append((attacker, bestBlock))

    s, a = calculateBlock(attackersCopy, blockersCopy, attackPlayer, defendPlayer, k + 1)

    return s + totalScore, a + blockCombos


def chooseAttackers(player1, player2):
    untap1 = player1.untappedCreatures()
    possibleAttacks = list(
        itertools.chain.from_iterable(itertools.combinations(untap1, r) for r in range(len(untap1) + 1)))
    result = max(
        [(calculateBlock(list(attackers), player2.untappedCreatures(), player1, player2, 0), attackers) for attackers in
         possibleAttacks],
        key=lambda p: p[0][0]  # Compare based on the score part of the tuple returned by calculateWorstBlock
    )
    return result[1]
