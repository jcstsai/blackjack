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

# Basic strategy tables
HARD_TOTAL_STRATEGY = {
    5:  'H', 6:  'H', 7:  'H', 8:  'H', 9:  'Dh', 10: 'Dh', 11: 'Dh', 12: 'H',
    13: 'S', 14: 'S', 15: 'S', 16: 'S', 17: 'S', 18: 'S', 19: 'S', 20: 'S', 21: 'S'
}

SOFT_TOTAL_STRATEGY = {
    13: 'H', 14: 'H', 15: 'H', 16: 'H', 17: 'H', 18: 'S', 19: 'S', 20: 'S', 21: 'S'
}

PAIR_STRATEGY = {
    'A': 'P', '10': 'S', '9': 'P', '8': 'P', '7': 'P', '6': 'P', '5': 'Dh',
    '4': 'H', '3': 'P', '2': 'P'
}

def create_deck():
    ranks = list(CARD_VALUES.keys())
    suits = ['♠', '♥', '♦', '♣']
    return [(rank, suit) for rank in ranks for suit in suits]

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

def show_hand(name, hand, hide_first=False):
    if hide_first:
        print(f"{name}'s hand: [Hidden], {hand[1][0]}{hand[1][1]}")
    else:
        cards = " ".join(f"{rank}{suit}" for rank, suit in hand)
        print(f"{name}'s hand: {cards} (Value: {hand_value(hand)})")

def get_recommended_play(player_hand, dealer_upcard):
    dealer_rank = dealer_upcard[0]
    # Convert dealer rank to numeric value for strategy lookup
    if dealer_rank in ['J', 'Q', 'K']:
        dealer_value = 10
    elif dealer_rank == 'A':
        dealer_value = 11
    else:
        dealer_value = int(dealer_rank)

    # Check for pairs
    if len(player_hand) == 2 and player_hand[0][0] == player_hand[1][0]:
        rank = player_hand[0][0]
        pair_rank = rank
        # For 10-value cards, unify to '10'
        if rank in ['J', 'Q', 'K']:
            pair_rank = '10'
        play = PAIR_STRATEGY.get(pair_rank, None)
        if play == 'P':
            return 'Split'
        elif play == 'Dh':
            # Double if allowed, else hit
            return 'Double or Hit'
        elif play == 'H':
            return 'Hit'
        elif play == 'S':
            return 'Stand'

    # Check for soft hands
    soft = False
    aces = [card for card in player_hand if card[0] == 'A']
    if aces and hand_value(player_hand) <= 21:
        soft = True

    total = hand_value(player_hand)
    if soft:
        # Use soft total strategy
        # Soft totals are counted as total - 11 (ace counted as 11)
        # But in our dict, keys are total with ace counted as 11
        # So we can use total directly
        # If total not in table, find closest lower key
        keys = sorted(SOFT_TOTAL_STRATEGY.keys())
        lookup_total = max([k for k in keys if k <= total], default=18)
        play = SOFT_TOTAL_STRATEGY.get(lookup_total, 'H')
    else:
        # Hard total strategy
        keys = sorted(HARD_TOTAL_STRATEGY.keys())
        lookup_total = max([k for k in keys if k <= total], default=17)
        play = HARD_TOTAL_STRATEGY.get(lookup_total, 'H')

    # Interpret play codes
    if play == 'H':
        return 'Hit'
    elif play == 'S':
        return 'Stand'
    elif play == 'Dh':
        return 'Double or Hit'
    elif play == 'Ds':
        return 'Double or Stand'
    return 'Hit'

def translate_move(move):
    if move == 'h':
        return 'Hit'
    elif move == 's':
        return 'Stand'
    elif move == 'p':
        return 'Split'
    elif move == 'd':
        return 'Double'
    else:
        return 'Unknown'

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
        player_moves = [[]]  # To record moves per hand

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
                recommended = get_recommended_play(hand, dealer_hand[1])
                prompt = f"Recommended play: {recommended}. Hit, Stand"
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
                    player_moves[hand_index].append('Hit')
                    show_hand(f"Player Hand {hand_index+1}", hand)
                    if hand_value(hand) > 21:
                        print("Bust!")
                        break
                elif move == 's':
                    player_moves[hand_index].append('Stand')
                    break
                elif move == 'p' and can_split:
                    player_moves[hand_index].append('Split')
                    # Split hand
                    player_balance -= current_bet
                    card1 = hand[0]
                    card2 = hand[1]
                    player_hands[hand_index] = [card1, deck.pop()]
                    player_hands.insert(hand_index + 1, [card2, deck.pop()])
                    bets.insert(hand_index + 1, current_bet)
                    doubles.insert(hand_index + 1, False)
                    player_moves.insert(hand_index + 1, [])
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
                    player_moves[hand_index].append('Double')
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

        # Summary table
        print("\nRound Summary:")
        print(f"Dealer's upcard: {dealer_hand[1][0]}{dealer_hand[1][1]}")
        print(f"{'Hand':<10}{'Cards':<20}{'Moves':<30}{'Recommended':<20}{'Match':<10}")
        for i, hand in enumerate(player_hands):
            cards_str = " ".join(f"{rank}{suit}" for rank, suit in hand)
            recommended = get_recommended_play(hand, dealer_hand[1])
            moves_str = ", ".join(player_moves[i]) if player_moves[i] else "No moves"
            # Determine if moves matched recommendation: if any move matches recommended or if recommended is 'Double or Hit' or 'Double or Stand', consider partial match
            match = False
            rec_lower = recommended.lower()
            for mv in player_moves[i]:
                mv_lower = mv.lower()
                if rec_lower == mv_lower:
                    match = True
                    break
                if rec_lower == 'double or hit' and mv_lower in ['double', 'hit']:
                    match = True
                    break
                if rec_lower == 'double or stand' and mv_lower in ['double', 'stand']:
                    match = True
                    break
            match_str = "Yes" if match else "No"
            print(f"{'Hand '+str(i+1):<10}{cards_str:<20}{moves_str:<30}{recommended:<20}{match_str:<10}")

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
