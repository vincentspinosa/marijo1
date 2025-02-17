import time
from ui import UI, new_hand
from ai.rules.player import Player

print_ai_crds = int(input("\nPrint AI cards? (0: No, 1: Yes): "))
ai_verbose_lvl = int(input("Verbose level (0 and upwards): "))

iterations = 5000
playersDict = {0: "Marijo1 (Player 0)", 1: "You (Player 1)"}
sm_blind = 10
players_chips = 1000
players = (Player(chips=players_chips), Player(chips=players_chips))
print("\nIn this game, Marijo1 is indexed as Player 0, and you are indexed as Player 1.")
first_dealer = int(input("First dealer of the game (Marijo1: 0, You: 1): "))
game_ui = UI(ai_iterations=iterations, players=players, ai_player_index=0, ai_verbose=ai_verbose_lvl, dealer_position=first_dealer, small_blind=sm_blind, big_blind=(sm_blind * 2))

print("\nLet's begin!")
time.sleep(1)

while game_ui.is_game_over() == False:
    print("\nStarting a new hand!")
    game_ui = new_hand(game_ui)
    time.sleep(1)
    game_ui.round(stage='pre-flop', print_ai_cards=print_ai_crds)
    time.sleep(1)
    game_ui.set_if_hand_over()
    if game_ui.hand_is_over == False:
        game_ui.round(stage='flop', print_ai_cards=print_ai_crds)
        game_ui.set_if_hand_over()
        time.sleep(1)
    if game_ui.hand_is_over == False:
        game_ui.round(stage='turn', print_ai_cards=print_ai_crds)
        game_ui.set_if_hand_over()
        time.sleep(1)
    if game_ui.hand_is_over == False:
        game_ui.round(stage='river', print_ai_cards=print_ai_crds)
        time.sleep(1)
    winner = None
    if len(game_ui.active_players) > 1 and game_ui.lastActionIsCheck == False:
        print("Going to showdown!".upper())
        len_cc = len(game_ui.community_cards)
        if len_cc < 5:
            game_ui.community_cards += [game_ui.deck.deal() for _ in range(5 - len_cc)]
        game_ui.print_showdown_info()
        winner = game_ui.showdown(game_ui.players)
    else:
        print("Not going to showdown!".upper())
        if len(game_ui.active_players) > 1:
            winner = None
        else:
            winner = game_ui.active_players[0]
    if winner is not None:
        winnerIndex = game_ui.get_player_position(winner)
        print(f"\nHand is over! {playersDict[winnerIndex]} won the hand.".upper())
    else:
        winnerIndex = None
        if len(game_ui.active_players) > 1 and game_ui.lastActionIsCheck == False:
            print("\nHands are equal!")
        print("\nThe pot is split between both players.")
    time.sleep(1)
    game_ui.end_hand(winnerIndex)
    game_ui.move_dealer_button()

print(f"\nGame is over! The winner is {playersDict[winnerIndex]}.".upper())
print(f"\nChips of {playersDict[winnerIndex]}: {game_ui.players[winnerIndex].chips}".upper())
print("\n")
