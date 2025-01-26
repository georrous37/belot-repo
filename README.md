# Belot machine learning project

Aim is to train a ML algorithm using RL to play the game of Belot.


# States
The state will be defined by:
- Hand: the cards that the player has in his hand (33 possible cards for each of 8 cards in hand (32 + 1 for no card))
- Trick: the the cards played so far in the trick (32 possible cards for each of 3 cards in trick (32 + 1 for no card))
- Trump suit: four possibilities ("C", "D", "H", "S")
Total number of states = 33^8 * 33^3 * 4

# Actions
- 1: Play card 1
- 2: Play card 2
- 3: Play card 3
- 4: Play card 4
- 5: Play card 5
- 6: Play card 6
- 7: Play card 7
- 8: Play card 8

# Rewards
- Select empty card slot (-20)
- Select invalid card (-10)
- Select card that wins the trick (trick points)