import random
import numpy as np

# Deck and Point Definitions
TRUMP_POINTS = {"J": 20, "9": 14, "A": 11, "10": 10, "K": 4, "Q": 3, "8": 0, "7": 0}
NON_TRUMP_POINTS = {"A": 11, "10": 10, "K": 4, "Q": 3, "J": 2, "9": 0, "8": 0, "7": 0}


# Creates a complete deck of cards with all ranks and suits.
def generate_deck():
    cards = ["7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    return [f"{rank} of {suit}" for suit in suits for rank in cards]


# Shuffles the deck and distributes 5 cards to each of the 4 players initially.
def generate_initial_hands(deck):
    return [deck[i * 5:(i + 1) * 5] for i in range(4)], deck[20:]


# Deals 3 more cards to each player from the remaining deck.
def deal_additional_cards(players_hands, deck):
    for i in range(4):
        players_hands[i].extend(deck[i * 3:(i + 1) * 3])
    return deck[12:]


# Determines the point value of a card based on whether it is a trump card.
def get_card_points(card, is_trump):
    rank, suit = card.split(" of ")
    return TRUMP_POINTS[rank] if is_trump else NON_TRUMP_POINTS[rank]


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

# State Encoder: Converts the current state of the game into a numerical representation for the RL agent.
def encode_state(hand, trick, trump_suit, lead_suit, valid_cards):
    """
    Encodes the current game state into a numerical array for the RL agent.
    
    - Hand: Encodes each card in the hand as a one-hot vector for ranks and suits.
    - Trick: Encodes the cards in the current trick in the same format.
    - Trump Suit: Encodes the trump suit as a one-hot vector.
    - Lead Suit: Encodes the lead suit as a one-hot vector.
    - Valid Cards: Encodes the valid cards that can be played as a one-hot vector.
    """
    # Helper to encode a card as a numerical vector
    def encode_card(card):
        ranks = ["7", "8", "9", "10", "J", "Q", "K", "A"]
        suits = ["hearts", "diamonds", "clubs", "spades"]
        rank, suit = card.split(" of ")
        rank_encoding = [1 if rank == r else 0 for r in ranks]
        suit_encoding = [1 if suit == s else 0 for s in suits]
        return rank_encoding + suit_encoding

    # Encode the hand
    hand_encoding = [encode_card(card) for card in hand]

    # Encode the trick
    trick_encoding = [encode_card(card) for card in trick]

    # Encode trump suit and lead suit
    suits = ["hearts", "diamonds", "clubs", "spades"]
    trump_suit_encoding = [1 if trump_suit == suit else 0 for suit in suits]
    lead_suit_encoding = [1 if lead_suit == suit else 0 for suit in suits] if lead_suit else [0, 0, 0, 0] 

    # Encode valid cards
    valid_cards_encoding = [encode_card(card) for card in valid_cards]

    # Flatten everything into a single numerical array
    state = (
        [item for card in hand_encoding for item in card] +  # Flatten hand
        [item for card in trick_encoding for item in card] +  # Flatten trick
        trump_suit_encoding +  # Add trump suit encoding
        lead_suit_encoding +   # Add lead suit encoding
        [item for card in valid_cards_encoding for item in card]  # Flatten valid cards
    )
    
    return np.array(state)