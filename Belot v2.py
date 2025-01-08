import random
import numpy as np

# Deck and Point Definitions
TRUMP_POINTS = {"J": 20, "9": 14, "A": 11, "10": 10, "K": 4, "Q": 3, "8": 0, "7": 0}
NON_TRUMP_POINTS = {"A": 11, "10": 10, "K": 4, "Q": 3, "J": 2, "9": 0, "8": 0, "7": 0}

# Generate the deck
# Creates a complete deck of cards with all ranks and suits.
def generate_deck():
    cards = ["7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    return [f"{rank} of {suit}" for suit in suits for rank in cards]

# Distribute initial 5 cards to players
# Shuffles the deck and distributes 5 cards to each of the 4 players initially.
def generate_initial_hands(deck):
    return [deck[i * 5:(i + 1) * 5] for i in range(4)], deck[20:]

# Distribute additional 3 cards to players after bidding
# Deals 3 more cards to each player from the remaining deck.
def deal_additional_cards(players_hands, deck):
    for i in range(4):
        players_hands[i].extend(deck[i * 3:(i + 1) * 3])
    return deck[12:]

# Helper to determine card points
# Determines the point value of a card based on whether it is a trump card.
def get_card_points(card, is_trump):
    rank, suit = card.split(" of ")
    return TRUMP_POINTS[rank] if is_trump else NON_TRUMP_POINTS[rank]

# Play a single trick with smarter decision-making
# Simulates one round of play where each player contributes one card to the trick.
# Players follow the lead suit if possible, play a trump card if required (opponents only), or any card otherwise.
# If a player does not have the lead suit and plays a trump card instead, this event is called "Tsakane."
def play_trick(players_hands, trump_suit):
    trick = []
    lead_suit = None

    for i, hand in enumerate(players_hands):
        if lead_suit:
            valid_cards = [card for card in hand if card.endswith(lead_suit)]
        else:
            valid_cards = hand

        if not valid_cards:
            first_player_team = (0 % 2)  # Team of the first player (0-indexed)
            current_player_team = (i % 2)  # Team of the current player
            winning_card = determine_winning_card(trick, lead_suit, trump_suit)
            winning_player = trick.index(winning_card)
          
            if (current_player_team != winning_player % 2):  # Check if the opponent team currently has the highest card in the trick
                trump_cards = [card for card in hand if card.endswith(trump_suit)]
                valid_cards = trump_cards if trump_cards else hand
            else:
                valid_cards = hand

        # Smarter card selection: play the highest-ranked card among valid options
        played_card = max(valid_cards, key=lambda card: get_card_points(card, card.endswith(trump_suit)))
        trick.append(played_card)
        hand.remove(played_card)

        if i == 0:
            lead_suit = played_card.split(" of ")[1]

    winning_card = determine_winning_card(trick, lead_suit, trump_suit)
    winning_player = trick.index(winning_card)

    return winning_player, trick

# Determine the winning card in a trick
# Determines which card wins the trick based on the lead suit and trump suit.
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
# Simulates the bidding phase where players decide on the trump suit or pass.
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
# Simulates an entire game, calculates scores for both teams, and displays results.
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

# Run the game
play_game()
