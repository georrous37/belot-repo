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
    state = encode_state(hand, trick, trump_suit, lead_suit)
    agent = rl_agent()  # Instantiate the RL agent
    action = agent.select_action(state, valid_cards)
    return valid_cards[action]


# State Encoder: Converts the current state of the game into a numerical representation for the RL agent.
def encode_state(hand, trick, trump_suit, lead_suit):
    """
    Encodes the current game state into a numerical array for the RL agent.
    
    - Hand: Encodes each card in the hand as a one-hot vector for ranks and suits.
    - Trick: Encodes the cards in the current trick in the same format.
    - Trump Suit: Encodes the trump suit as a one-hot vector.
    - Lead Suit: Encodes the lead suit as a one-hot vector.
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

    # Flatten everything into a single numerical array
    state = (
        [item for card in hand_encoding for item in card] +  # Flatten hand
        [item for card in trick_encoding for item in card] +  # Flatten trick
        trump_suit_encoding +  # Add trump suit encoding
        lead_suit_encoding     # Add lead suit encoding
    )
    
    return np.array(state)


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
