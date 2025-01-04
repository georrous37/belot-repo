import numpy as np
import random

# Define the deck of cards

# Deck: Each card is represented by a unique ID (e.g., 0 to 31)
def generate_deck():
    """
    Creates a full 32-card Belot deck.
    """
    cards = ["7", "8", "9", "10", "J", "Q", "K", "A"]
    suits = ["hearts", "diamonds", "clubs", "spades"]
    return [f"{rank} of {suit}" for suit in suits for rank in cards]


# Create the State Representation
def initialize_state():
    """
    Initializes a state representation for Belot.
    """
    state = {
        "cards_in_hand": np.zeros(32, dtype=int),  # Binary vector for cards in hand
        "cards_played": np.zeros(32, dtype=int),   # Binary vector for cards played
        "trump_suit": np.zeros(4, dtype=int),      # One-hot for trump suit
        "current_trick": np.zeros(8, dtype=int),   # Cards in current trick
        "bidding_info": np.zeros(8, dtype=int),    # Bids and contract info
        "game_phase": np.zeros(3, dtype=int),      # Phase of the game
        "scores": np.zeros(2, dtype=float),        # Team scores
    }
    return state


# Update the State

# Update cards in hand
def update_cards_in_hand(state, card_ids):
    """
    Updates the 'cards_in_hand' vector in the state.
    """
    state["cards_in_hand"][:] = 0  # Reset all cards
    for card_id in card_ids:
        state["cards_in_hand"][card_id] = 1

# Update cards in played
def update_cards_played(state, card_id):
    """
    Marks a card as played in the 'cards_played' vector.
    """
    state["cards_played"][card_id] = 1

# Update the Trump Suit
def set_trump_suit(state, suit):
    """
    Updates the trump suit in the state.
    """
    suit_map = {"hearts": 0, "diamonds": 1, "clubs": 2, "spades": 3}
    state["trump_suit"][:] = 0  # Reset all suits
    state["trump_suit"][suit_map[suit]] = 1

# Update the Current Trick
def update_current_trick(state, played_cards):
    """
    Updates the 'current_trick' with the cards currently in play.
    """
    state["current_trick"][:] = 0
    for i, card_id in enumerate(played_cards):
        state["current_trick"][2 * i] = card_id % 8  # Rank
        state["current_trick"][2 * i + 1] = card_id // 8  # Suit


# Combine the State into a Vector
def get_state_vector(state):
    """
    Combines all components of the state into a single vector.
    """
    return np.concatenate([
        state["cards_in_hand"],
        state["cards_played"],
        state["trump_suit"],
        state["current_trick"],
        state["bidding_info"],
        state["game_phase"],
        state["scores"],
    ])



# Initialize the state
state = initialize_state()

# Update the state as the game progresses
update_cards_in_hand(state, [0, 15, 23])  # Player holds these cards
update_cards_played(state, 10)  # Card with ID 10 is played
set_trump_suit(state, "hearts")  # Hearts is the trump suit
update_current_trick(state, [10, 25])  # Two cards in the trick

# Get the state vector for the RL agent
# state_vector = get_state_vector(state)
# print("State Vector:", state_vector)


# Encode the rankings
TRUMP_POINTS = {"J": 20, "9": 14, "A": 11, "10": 10, "K": 4, "Q": 3, "8": 0, "7": 0}
NON_TRUMP_POINTS = {"A": 11, "10": 10, "K": 4, "Q": 3, "J": 2, "9": 0, "8": 0, "7": 0}

# Helper to determine points
def get_card_points(card, is_trump):
    rank, suit = card.split(" of ")
    return TRUMP_POINTS[rank] if is_trump else NON_TRUMP_POINTS[rank]


# Play a trick
def play_trick(players_hands, trump_suit):
    """
    Simulates one trick in Belot.
    
    Args:
    - players_hands: List of 4 hands (each a list of card strings).
    - trump_suit: The current trump suit (e.g., "hearts").
    
    Returns:
    - winning_player: The index of the player who won the trick.
    - trick: The cards played in this trick.
    """
    trick = []
    lead_suit = None

    for i, hand in enumerate(players_hands):
        # Player selects a card to play (for simplicity, pick the first valid card)
        if lead_suit:
            # Must follow suit if possible
            valid_cards = [card for card in hand if card.endswith(lead_suit)]
        else:
            # No lead suit yet, can play any card
            valid_cards = hand
        
        # If no valid cards, play any card (may happen if following suit isn't possible)
        if not valid_cards:
            valid_cards = hand
        
        played_card = valid_cards[0]  # Select the first valid card (can improve strategy here)
        trick.append(played_card)
        hand.remove(played_card)

        if i == 0:
            lead_suit = played_card.split(" of ")[1]  # Set lead suit from first card

    # Determine winner of the trick
    winning_card = determine_winning_card(trick, lead_suit, trump_suit)
    winning_player = trick.index(winning_card)

    return winning_player, trick

def determine_winning_card(trick, lead_suit, trump_suit):
    """
    Determines the winning card of a trick.
    """
    winning_card = trick[0]
    lead_cards = [card for card in trick if card.endswith(lead_suit)]
    trump_cards = [card for card in trick if card.endswith(trump_suit)]

    if trump_cards:
        winning_card = max(trump_cards, key=lambda card: get_card_points(card, True))
    else:
        winning_card = max(lead_cards, key=lambda card: get_card_points(card, False))
    
    return winning_card

# Test trick-taking
players_hands = [
    ["Q of hearts", "9 of diamonds", "7 of spades"],
    ["A of clubs", "10 of spades", "8 of clubs"],
    ["K of hearts", "Q of diamonds", "9 of clubs"],
    ["8 of hearts", "A of spades", "10 of diamonds"],
]

trump_suit = "hearts"

winner, trick = play_trick(players_hands, trump_suit)
#print("Trick Played:", trick)
#print("Winner:", winner)


# Bidding phase
def bidding_phase():
    """
    Simulates the bidding phase.
    """
    bids = ["pass", "clubs", "diamonds", "hearts", "spades"]
    current_bid = "pass"
    winner = None

    for i in range(4):
        player_bid = bids[np.random.randint(0, len(bids))]  # Random bid (improve with strategy)
        if player_bid != "pass" and player_bid != current_bid:
            current_bid = player_bid
            winner = i

    return winner, current_bid


# Bidding + Trick-taking
def play_game():
    # Generate hands for all players
    players_hands = generate_hands()
    
    # Bidding
    winner, trump_suit = bidding_phase()
    print(f"Player {winner} won the bid with trump suit: {trump_suit}")

    # Play tricks
    scores = [0, 0]
    for _ in range(8):  # 8 tricks in a Belot round
        trick_winner, trick = play_trick(players_hands, trump_suit)
        scores[trick_winner % 2] += sum(get_card_points(card, card.endswith(trump_suit)) for card in trick)

    print("Final Scores:", scores)


def generate_hands():
    """
    Shuffles the deck and distributes 8 cards to each of 4 players.
    
    Returns:
    - hands: List of 4 hands, each containing 8 cards.
    """
    deck = generate_deck()
    random.shuffle(deck)  # Shuffle the deck
    
    # Distribute 8 cards to each player
    hands = [deck[i * 8:(i + 1) * 8] for i in range(4)]
    return hands

hands = generate_hands()
for i, hand in enumerate(hands):
    print(f"Player {i + 1}'s Hand: {hand}")
    

