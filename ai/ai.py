import pickle
import random
import numpy as np
from treys import Card
from gameState.gameState import GameState

def sig(n):
    return 1 / (1 + np.exp(-n))

""" def multiple_sig(iterations, n):
    for _ in range(iterations):
        n = sig(n)
    return n """

def find_max_regret(regrets:list) -> int or float:
    maxR = 0
    for data in regrets:
        if data[1] > maxR:
            maxR = data[1]
    return maxR

def turn_regrets_to_value(regrets:list) -> list:
    maxR = find_max_regret(regrets)
    for data in regrets:
        data[1] = maxR / data[1] if data[1] >= 1 else maxR
        data[1] /= sig(data[1])
        #data[1] /= (sig(data[1]) * sig(data[1]))
    return regrets

def compute_probabilities(regrets:list) -> list:
    sum = 0
    computeAgain = False
    for rg in regrets:
        sum += rg[1]
    for rg in regrets:
        rg[1] /= sum
        if rg[1] < 0.1 and rg[1] > 0:
            rg[1] = 0
            computeAgain = True
    if computeAgain == True:
        return compute_probabilities(regrets)
    else:
        return regrets

def compute_regrets_probabilities(regrets:list) -> list:
    return compute_probabilities(turn_regrets_to_value(regrets))

def algorithm(gameState:GameState, iterations:int, verboseLevel:int=0, verboseIterationsSteps:int=50) -> dict[list, int]:
    # SETTING-UP EVERYTHING
    coeffL1 = 42
    """ if gameState.current_stage == 'flop':
        coeffL1 = 3
    elif gameState.current_stage == 'turn':
        coeffL1 = 2
    elif gameState.current_stage == 'river':
        coeffL1 = 1 """
    coeffL2 = 1
    liste_actions = gameState.available_actions()
    regrets = [[el, 0] for el in liste_actions]
    aiIndex = gameState.get_player_position(gameState.ai_player)
    opposite_player_index = (aiIndex + 1) % len(gameState.players)
    gameState.ai_deck = gameState.deck.cards + gameState.players[opposite_player_index].hand
    potSave = gameState.current_pot
    aiChipsSave = gameState.ai_player.chips
    oppChipsSave = gameState.players[opposite_player_index].chips
    aiCB = gameState.current_bets[gameState.ai_player]
    oppCB = gameState.current_bets[gameState.players[opposite_player_index]]
    if gameState.ai_player.chips > oppChipsSave + oppCB:
        maxBetAmount = oppChipsSave + oppCB
    else:
        maxBetAmount = gameState.ai_player.chips
    gameStateInitial = pickle.dumps(gameState)
    gameStateTemp = pickle.loads(gameStateInitial)
    traversals = int(iterations / len(liste_actions)) + 1
    # TRAVERSAL OF THE GAME TREE
    for _ in range(traversals):
        random.shuffle(gameStateTemp.ai_deck)
        gameStateTemp.community_cards += [gameStateTemp.ai_deck.pop() for _ in range(5 - len(gameStateTemp.community_cards))]
        gameStateTemp.players[opposite_player_index].hand = [gameStateTemp.ai_deck.pop() for _ in range(2)]
        winner = gameStateTemp.showdown(gameStateTemp.players)
        if verboseLevel > 2:
            if iterations % verboseIterationsSteps == 0:
                print(f"\nIteration {iterations}")
                print(f"Community cards:")
                Card.print_pretty_cards(gameStateTemp.community_cards)
                print(f"Opposite player cards:")
                Card.print_pretty_cards(gameStateTemp.players[opposite_player_index].hand)
        index = -1
        for action in liste_actions:
            index += 1
            # LAYER 1 - DEFENSIVE
            if action[0] == 'fold':
                if winner in [gameStateTemp.ai_player, None]:
                    regrets[index][1] += (((potSave - oppCB) / 2) * coeffL1)
            elif action[0] == 'check':
                if winner == gameStateTemp.ai_player:
                    regrets[index][1] += ((potSave / 2) * coeffL1)
            elif action[0] in ['call', 'raise', 'all-in']:
                if winner == gameStateTemp.players[opposite_player_index]:
                    regrets[index][1] += (min(action[1], maxBetAmount) * coeffL1)
            # LAYER 2 - OFFENSIVE
            if action[0] == 'fold':
                if winner == gameStateTemp.ai_player:
                    if aiChipsSave + aiCB >= oppCB + oppChipsSave:
                        regrets[index][1] += ((potSave + oppChipsSave) * coeffL2)
                    else:
                        regrets[index][1] += ((potSave + oppChipsSave - (oppChipsSave + oppCB - (aiChipsSave + aiCB))) * coeffL2)
                elif winner == None:
                    regrets[index][1] += (((potSave - aiCB) / 2) * coeffL2)
            elif action[0] == 'check':
                if winner == gameStateTemp.ai_player:
                    regrets[index][1] += (((potSave / 2) + min(oppChipsSave, aiChipsSave)) * coeffL2)
            elif action[0] in ['call', 'raise', 'all-in']:
                if winner == gameStateTemp.players[opposite_player_index]:
                    regrets[index][1] += (min(action[1], maxBetAmount) * coeffL2)
                elif winner == gameStateTemp.ai_player:
                    if action[1] < aiChipsSave:
                        regrets[index][1] += ((aiChipsSave - action[1]) * coeffL2)
        gameStateTemp = pickle.loads(gameStateInitial)
    if verboseLevel > 0:
        print(f"\nIterations: {iterations}")
    if verboseLevel > 1:
        print("\nRegrets before computing them:")
        for r in regrets:
            print(r)
    # COMPUTATION OF THE RESULTS
    result = compute_regrets_probabilities(regrets)
    if verboseLevel > 1:
        print("\nAction distribution:")
        for action_distribution in result:
            print(action_distribution)
    return result
