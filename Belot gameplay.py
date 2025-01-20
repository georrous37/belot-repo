import random
import numpy as np
from Belot_game_setting import *

# Play a single trick
# Simulates one round of play where each player contributes one card to the trick.
# Players follow the lead suit if possible, play a trump card if required (opponents only), or any card otherwise.
# If a player does not have the lead suit and plays a trump card instead, this event is called "Tsakane."
def play_trick(players_hands, trump_suit):
    trick = [] # Cards played in the trick
    lead_suit = None # Lead suit of the trick

    for i, hand in enumerate(players_hands): # Iterate through each player to play a card
        if lead_suit: # Not the first player in the trick
            # Determine valid cards based on the lead suit
            valid_cards = [card for card in hand if card.endswith(lead_suit)]
        else: # First player in the trick
            # Determine valid cards based on the trump suit
            valid_cards = hand

        if not valid_cards: # Tsakane event
            current_player_team = (i % 2)  # Team of the current player
            winning_card_sofar = determine_winning_card(trick, lead_suit, trump_suit) # Winning card in the trick so far
            winning_player = trick.index(winning_card_sofar) # Player who played the winning card so far
          
            if (current_player_team != winning_player % 2): # Check if the opponent team currently has the highest card in the trick
                # Tsakane: Player does not have the lead suit and plays a trump card instead
                trump_cards = [card for card in hand if card.endswith(trump_suit)] # Trump cards in hand
                if trump_cards: # If player has trump cards, play the highest one
                    # Find the highest trump card in the trick
                    highest_trump_in_trick = max([card for card in trick if card.endswith(trump_suit)], key=lambda card: get_card_points(card, True), default=None)
                    if highest_trump_in_trick:  # If there is a trump card in the trick
                    # Play a trump card higher than the highest trump card in the trick
                        higher_trump_cards = [card for card in trump_cards if get_card_points(card, True) > get_card_points(highest_trump_in_trick, True)]
                        valid_cards = higher_trump_cards if higher_trump_cards else trump_cards  # Play a higher trump card if available, else play any trump card
                    else:
                        # Play a trump card in hand
                        valid_cards = trump_cards
                else: # If player does not have trump cards, play any card
                    valid_cards = hand
            else: # If the current player's team has the highest card in the trick, play any card
                valid_cards = hand

        # Smarter card selection using RL agent
        played_card = select_card_with_rl(valid_cards, players_hands[i], trick, trump_suit, lead_suit)
        trick.append(played_card)
        hand.remove(played_card)

        if i == 0: # First player in the trick
            lead_suit = played_card.split(" of ")[1]

    winning_card = determine_winning_card(trick, lead_suit, trump_suit) # Winning card in the trick
    winning_player = trick.index(winning_card) # Player who played the winning card

    return winning_player, trick 


# Chooses a card based on the RL agent's policy.
def select_card_with_rl(valid_cards, hand, trick, trump_suit, lead_suit):
    state = encode_state(hand, trick, trump_suit, lead_suit, valid_cards)
    agent = rl_agent()  # Instantiate the RL agent
    action = agent.select_action(state, valid_cards)
    return valid_cards[action]


# Full game simulation: Simulates an entire game, calculates scores for both teams, and displays results.
def play_game():
    deck = generate_deck()
    random.shuffle(deck)

    # Initial card distribution
    players_hands, remaining_deck = generate_initial_hands(deck)
    print("Initial Hands:")
    for i, hand in enumerate(players_hands):
        print(f"Player {i + 1}: {hand}")

    # Bidding phase
    winner, trump_suit = bidding_phase()
    print(f"\nPlayer {winner + 1} won the bid with trump suit: {trump_suit}")

    # Distribute additional cards
    remaining_deck = deal_additional_cards(players_hands, remaining_deck)
    print("\nHands after receiving additional cards:")
    for i, hand in enumerate(players_hands):
        print(f"Player {i + 1}: {hand}")

    # Play tricks
    scores = [0, 0]
    for trick_num in range(8):
        trick_winner, trick = play_trick(players_hands, trump_suit)
        trick_points = sum(get_card_points(card, card.endswith(trump_suit)) for card in trick)
        scores[trick_winner % 2] += trick_points

        print(f"\nTrick {trick_num + 1}: {trick}")
        print(f"Player {trick_winner + 1} won the trick and earned {trick_points} points")
    print("\nFinal Scores:")
    print(f"Team 1 (Players 1 & 3): {scores[0]} points")
    print(f"Team 2 (Players 2 & 4): {scores[1]} points")


# RL Agent Placeholder
# Placeholder for the RL agent implementation
def rl_agent():
    class Agent:
        def select_action(self, state, valid_cards):
            # Placeholder: Replace with trained RL policy
            return random.randint(0, len(valid_cards) - 1)

    return Agent()

# Run the game
play_game()