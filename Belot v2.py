#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 21:39:01 2025

@author: georgiroussinov
"""

import random
import numpy as np

# Deck and Point Definitions
TRUMP_POINTS = {"J": 20, "9": 14, "A": 11, "10": 10, "K": 4, "Q": 3, "8": 0, "7": 0}
NON_TRUMP_POINTS = {"A": 11, "10": 10, "K": 4, "Q": 3, "J": 2, "9": 0, "8": 0, "7": 0}

# Generate the deck
def generate_deck():
    cards = ["7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    return [f"{rank} of {suit}" for suit in suits for rank in cards]

# Distribute cards to players
def generate_hands():
    deck = generate_deck()
    random.shuffle(deck)
    hands = [deck[i * 8:(i + 1) * 8] for i in range(4)]
    return hands

# Helper to determine card points
def get_card_points(card, is_trump):
    rank, suit = card.split(" of ")
    return TRUMP_POINTS[rank] if is_trump else NON_TRUMP_POINTS[rank]

# Play a single trick
def play_trick(players_hands, trump_suit):
    trick = []
    lead_suit = None

    for i, hand in enumerate(players_hands):
        if lead_suit:
            valid_cards = [card for card in hand if card.endswith(lead_suit)]
        else:
            valid_cards = hand
        
        if not valid_cards:
            valid_cards = hand
        
        played_card = valid_cards[0]  # Select the first valid card
        trick.append(played_card)
        hand.remove(played_card)

        if i == 0:
            lead_suit = played_card.split(" of ")[1]

    winning_card = determine_winning_card(trick, lead_suit, trump_suit)
    winning_player = trick.index(winning_card)

    return winning_player, trick

# Determine the winning card in a trick
def determine_winning_card(trick, lead_suit, trump_suit):
    winning_card = trick[0]
    lead_cards = [card for card in trick if card.endswith(lead_suit)]
    trump_cards = [card for card in trick if card.endswith(trump_suit)]

    if trump_cards:
        winning_card = max(trump_cards, key=lambda card: get_card_points(card, True))
    else:
        winning_card = max(lead_cards, key=lambda card: get_card_points(card, False))
    
    return winning_card

# Simulate bidding
def bidding_phase():
    bids = ["pass", "hearts", "diamonds", "clubs", "spades"]
    current_bid = "pass"
    winner = None

    for i in range(4):
        player_bid = bids[random.randint(0, len(bids) - 1)]
        if player_bid != "pass" and player_bid != current_bid:
            current_bid = player_bid
            winner = i

    return winner, current_bid

# Full game simulation
def play_game():
    players_hands = generate_hands()
    print("Initial Hands:")
    for i, hand in enumerate(players_hands):
        print(f"Player {i + 1}: {hand}")

    winner, trump_suit = bidding_phase()
    print(f"\nPlayer {winner + 1} won the bid with trump suit: {trump_suit}")

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

# Run the game
play_game()
