import random

# Card values (Ace is counted as 11 initially, handled later if bust)
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

MAX_SPLITS = 4
BASE_BET = 10
player_balance = 1000

# Create a deck of 52 cards
def create_deck():
    ranks = list(CARD_VALUES.keys())
    suits = ['♠', '♥', '♦', '♣']
    return [(rank, suit) for rank in ranks for suit in suits]

# Calculate hand value (Aces can be 1 or 11)
def hand_value(hand):
    value = sum(CARD_VALUES[rank] for rank, _ in hand)
    aces = sum(1 for rank, _ in hand if rank == 'A')
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

def is_soft_hand(hand):
    value = sum(CARD_VALUES[rank] for rank, _ in hand)
    aces = sum(1 for rank, _ in hand if rank == 'A')
    return aces > 0 and value <= 21

# Print hand
def show_hand(name, hand, hide_first=False):
    if hide_first:
        print(f"{name}'s hand: [Hidden], {hand[1][0]}{hand[1][1]}")
    else:
        cards = " ".join(f"{rank}{suit}" for rank, suit in hand)
        print(f"{name}'s hand: {cards} (Value: {hand_value(hand)})")

# Main game loop
def play_blackjack():
    global player_balance

    while True:
        deck = create_deck()
        random.shuffle(deck)

        # Get bet from player
        while True:
            try:
                bet = int(input(f"Place your bet (between {BASE_BET} and {player_balance}): "))
                if BASE_BET <= bet <= player_balance:
                    break
                else:
                    print(f"Invalid bet amount. Must be between {BASE_BET} and {player_balance}.")
            except ValueError:
                print("Please enter a valid number.")

        player_balance -= bet

        player_hands = [[deck.pop(), deck.pop()]]
        bets = [bet]
        doubles = [False]

        dealer_hand = [deck.pop(), deck.pop()]

        # Show initial hands
        show_hand("Dealer", dealer_hand, hide_first=True)
        show_hand("Player", player_hands[0])

        hand_index = 0
        while hand_index < len(player_hands):
            hand = player_hands[hand_index]
            current_bet = bets[hand_index]
            can_split = len(player_hands) < MAX_SPLITS and len(hand) == 2 and hand[0][0] == hand[1][0] and player_balance >= current_bet
            can_double = len(hand) == 2 and player_balance >= current_bet and not doubles[hand_index]

            while True:
                prompt = "Hit, Stand"
                if can_split:
                    prompt += ", Split"
                if can_double:
                    prompt += ", Double"
                prompt += "? (h/s"
                if can_split:
                    prompt += "/p"
                if can_double:
                    prompt += "/d"
                prompt += "): "

                move = input(prompt).strip().lower()
                if move == 'h':
                    hand.append(deck.pop())
                    show_hand(f"Player Hand {hand_index+1}", hand)
                    if hand_value(hand) > 21:
                        print("Bust!")
                        break
                elif move == 's':
                    break
                elif move == 'p' and can_split:
                    # Split hand
                    player_balance -= current_bet
                    card1 = hand[0]
                    card2 = hand[1]
                    player_hands[hand_index] = [card1, deck.pop()]
                    player_hands.insert(hand_index + 1, [card2, deck.pop()])
                    bets.insert(hand_index + 1, current_bet)
                    doubles.insert(hand_index + 1, False)
                    show_hand(f"Player Hand {hand_index+1}", player_hands[hand_index])
                    show_hand(f"Player Hand {hand_index+2}", player_hands[hand_index + 1])
                    can_split = len(player_hands) < MAX_SPLITS and len(player_hands[hand_index]) == 2 and player_hands[hand_index][0][0] == player_hands[hand_index][1][0] and player_balance >= bets[hand_index]
                    can_double = len(player_hands[hand_index]) == 2 and player_balance >= bets[hand_index] and not doubles[hand_index]
                    # Don't increment hand_index to play the new hand after split
                    continue
                elif move == 'd' and can_double:
                    player_balance -= current_bet
                    doubles[hand_index] = True
                    bets[hand_index] *= 2
                    hand.append(deck.pop())
                    show_hand(f"Player Hand {hand_index+1}", hand)
                    if hand_value(hand) > 21:
                        print("Bust!")
                    break
                else:
                    print("Invalid choice. Please try again.")

            hand_index += 1

        # Dealer's turn
        show_hand("Dealer", dealer_hand)
        while True:
            dealer_val = hand_value(dealer_hand)
            if dealer_val < 17:
                dealer_hand.append(deck.pop())
                show_hand("Dealer", dealer_hand)
            elif dealer_val == 17 and is_soft_hand(dealer_hand):
                dealer_hand.append(deck.pop())
                show_hand("Dealer", dealer_hand)
            else:
                break

        dealer_total = hand_value(dealer_hand)

        # Evaluate each player hand
        for i, hand in enumerate(player_hands):
            player_total = hand_value(hand)
            print(f"\nResult for Player Hand {i+1}:")
            if player_total > 21:
                print("Bust! You lose this hand.")
            else:
                if dealer_total > 21:
                    print("Dealer busts! You win this hand!")
                    player_balance += bets[i] * 2
                else:
                    if player_total > dealer_total:
                        print("You win this hand!")
                        player_balance += bets[i] * 2
                    elif player_total < dealer_total:
                        print("Dealer wins this hand.")
                    else:
                        print("It's a tie!")
                        player_balance += bets[i]

        print(f"\nYour balance: {player_balance}")
        if player_balance <= 0:
            print("You have run out of money! Game over.")
            break

        # Ask to play again
        if input("Play again? (y/n): ").strip().lower() != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    play_blackjack()
