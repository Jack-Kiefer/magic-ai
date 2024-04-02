import copy
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


def findMaxBlockOrdering(attacker, blockers, defender, scorefn):
    return max(itertools.permutations(blockers), key=lambda p: scoreAttack([(attacker, p)], defender, scorefn))


'''
Inputs: List of attackers, defender GameState, score function
Outputs: Tuple of (score of minimum score blocking combination, minimum score blocking combination)
'''
def calculateBlock(attackers, blockers, scorefn, defender, k):
    if k > len(blockers):
        return scoreAttack([(attacker, tuple()) for attacker in attackers], defender, scorefn), [
            (attacker, tuple()) for attacker in
            attackers]
    attackersCopy = copy.copy(attackers)
    blockersCopy = copy.copy(blockers)
    totalScore = 0
    blockCombos = []

    for attacker in attackers:
        bestScore = 1000000
        bestBlock = None
        for blockers_combination in itertools.combinations(blockersCopy, k):
            bestOrdering = findMaxBlockOrdering(attacker, blockers_combination, defender, scorefn)
            mana, cards, life = scoreAttackCombo(attacker, bestOrdering)
            score = scorefn(mana, cards, life, defender.life)

            if score < bestScore:
                bestScore = score
                bestBlock = bestOrdering

        if bestScore < scoreAttack([(attacker, tuple())], defender, scorefn):
            totalScore += bestScore
            for blocker in bestBlock:
                blockersCopy.remove(blocker)
            attackersCopy.remove(attacker)
            blockCombos.append((attacker, bestBlock))

    s, a = calculateBlock(attackersCopy, blockersCopy, scorefn, defender, k + 1)

    return s + totalScore, a + blockCombos


def chooseAttackers(player1, player2):
    untap1 = player1.untappedCreatures()
    possibleAttacks = list(
        itertools.chain.from_iterable(itertools.combinations(untap1, r) for r in range(len(untap1) + 1)))
    result = max(
        [(calculateBlock(list(attackers), player2.untappedCreatures(), player1.scorefn, player2, 0), attackers) for attackers in
         possibleAttacks],
        key=lambda p: p[0][0]  # Compare based on the score part of the tuple returned by calculateWorstBlock
    )
    return result[1]
