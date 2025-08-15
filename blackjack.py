import random

# Card values (Ace is counted as 11 initially, handled later if bust)
CARD_VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}

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

# Print hand
def show_hand(name, hand, hide_first=False):
    if hide_first:
        print(f"{name}'s hand: [Hidden], {hand[1][0]}{hand[1][1]}")
    else:
        cards = " ".join(f"{rank}{suit}" for rank, suit in hand)
        print(f"{name}'s hand: {cards} (Value: {hand_value(hand)})")

# Main game loop
def play_blackjack():
    deck = create_deck()

    while True:
        random.shuffle(deck)
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]

        # Show initial hands
        show_hand("Dealer", dealer_hand, hide_first=True)
        show_hand("Player", player_hand)

        # Player turn
        while hand_value(player_hand) < 21:
            move = input("Hit or Stand? (h/s): ").strip().lower()
            if move == 'h':
                player_hand.append(deck.pop())
                show_hand("Player", player_hand)
            elif move == 's':
                break
            else:
                print("Invalid choice. Please type 'h' or 's'.")

        player_total = hand_value(player_hand)
        if player_total > 21:
            print("You bust! Dealer wins.")
        else:
            # Dealer's turn
            show_hand("Dealer", dealer_hand)
            while hand_value(dealer_hand) < 17:
                dealer_hand.append(deck.pop())
                show_hand("Dealer", dealer_hand)

            dealer_total = hand_value(dealer_hand)

            # Determine winner
            if dealer_total > 21:
                print("Dealer busts! You win!")
            elif player_total > dealer_total:
                print("You win!")
            elif player_total < dealer_total:
                print("Dealer wins.")
            else:
                print("It's a tie!")

        # Ask to play again
        if input("Play again? (y/n): ").strip().lower() != 'y':
            print("Thanks for playing!")
            break

if __name__ == "__main__":
    play_blackjack()
