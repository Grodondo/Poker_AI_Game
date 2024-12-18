import random


class player:

    def __init__(self, cash, name=None):
        self.hand = []
        self.cash = cash
        self.name = name
        self.last_bet = 0

    # def bet(self, amount):
    #    self.cash -= amount

    def reset(self):
        self.hand = []
        self.last_bet = 0

    def win(self, amount):
        self.cash += amount

    def lose(self, amount):
        self.cash -= amount

    def __str__(self):
        return str(self.cash)


class poker:

    def __init__(self, player, ai, starting_bet=5):
        self.SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

        self.deck = [[] for _ in range(4)]
        self.player = player
        self.ai = ai

        self.pot = 0

        self.human_score = 0
        self.ai_score = 0
        self.starting_bet = starting_bet
        self.winner = None

    def calculate_score(self, hand):
        score = 0

        suits = [card[0] for card in hand]
        ranks = [card[1] for card in hand]

        # Sort ranks for easier pattern detection
        ranks.sort()

        # Check for duplicates (useful for pairs, three of a kind, etc.)
        rank_counts = {rank: ranks.count(rank) for rank in set(ranks)}

        # Check for Royal Flush or Straight Flush
        if self.is_flush(suits) and self.is_straight(ranks):
            if ranks == [10, 11, 12, 13, 14]:
                return 10  # Royal Flush
            return 9  # Straight Flush

        # Check for Four of a Kind
        if 4 in rank_counts.values():
            return 8

        # Check for Full House
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            return 7

        # Check for Flush
        if self.is_flush(suits):
            return 6

        # Check for Straight
        if self.is_straight(ranks):
            return 5

        # Check for Three of a Kind
        if 3 in rank_counts.values():
            return 4

        # Check for Two Pair
        if list(rank_counts.values()).count(2) == 2:
            return 3

        # Check for One Pair
        if 2 in rank_counts.values():
            return 2

        # High Card (default case)
        return 1

    def is_flush(self, suits):
        """Check if all cards have the same suit."""
        return len(set(suits)) == 1

    def is_straight(self, ranks):
        """Check if ranks form a straight (consecutive values)."""
        return ranks == list(range(ranks[0], ranks[0] + 5))

    def other_player(self, player):
        """
        poker.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        """
        return self.ai if player == self.player else self.player

    def deal(self):
        """
        Deals 2 cards to both player and AI from a shuffled deck.
        """

        # Create and shuffle deck
        self.deck = [(suit, rank) for suit in self.SUITS for rank in range(1, 14)]
        random.shuffle(self.deck)

        # Deal first 2 cards to player and AI
        self.player.hand.append(self.deck.pop())
        self.ai.hand.append(self.deck.pop())
        self.player.hand.append(self.deck.pop())
        self.ai.hand.append(self.deck.pop())

    def draw(self):
        """
        Draws a card from the deck and adds it to the table hand.
        """
        # Card drawn from the deck
        card = self.deck.pop()

        # Add card to all hands
        self.table_hand.append(card)
        # self.ai.hand.append(card)
        # self.player.hand.append(card)

        # Show the current table hand
        print("Table hand: ", self.table_hand)

    def fold(self, player):
        """
        Player surrenders the hand and loses the bet.
        """
        player.lose(self.pot)

    def choose_action(self, player, turn, current_bet=0):
        """
        Player chooses an action (call, raise, fold, check).
        Call (matching the amount of the previous bet or raise).
        Raise (increase the amount of the current open bet or raise, which any subsequent players must at least match to stay in. Raising when a player in front of you has already raised is known as a re-raise).
        Fold (pushing their cards into the middle and surrendering any chance to win the hand).
        Check (pass the action to the next player without betting anything. Checking can only be used when there's no open bet or raise in front of you.
        """
        POSSIBLE_ACTIONS = ["call", "raise", "fold", "check"]

        # Player action
        action = None
        current_bet = self.current_bet

        while True:
            # First turn
            if turn == 0:
                # print(f"Bet starting at {self.starting_bet}.")
                action = str(
                    input(f"{player.name}, choose your action (Call, Fold): ")
                ).lower()

                if action == "fold":
                    print(f"{player.name} folds.")
                    return "fold"
                elif action == "call":
                    player.lose(self.starting_bet)
                    self.pot += self.starting_bet
                    player.last_bet = self.starting_bet
                    print(f"{player.name} calls. Pot: ${self.pot}")
                    return "call"
                elif action == "check" or action == "raise":
                    print("You can't check or raise in the first turn.")
                    continue
            else:
                action = str(
                    input(
                        f"{player.name}, choose your action (Call, Raise, Fold, Check): "
                    )
                ).lower()

            # Check if action is valid
            if action not in POSSIBLE_ACTIONS:
                print(
                    "Invalid action. Please choose from the following: ",
                    POSSIBLE_ACTIONS,
                )
                continue

            if action == "call":

                if player.cash < current_bet - player.last_bet:
                    print(f"{player.name} cannot afford to call. Checking instead.")
                    return "check"

                if current_bet > player.last_bet:
                    amount = current_bet - player.last_bet
                    player.lose(amount)
                    player.last_bet = current_bet
                    self.pot += amount

                    print(f"{player.name} calls. Pot: ${self.pot}")
                    return "call"
                else:
                    print(f"{player.name} checks.")
                    return "check"

            elif action == "raise":
                raise_amount = int(
                    input(
                        f"{player.name}, enter raise amount (Current ${current_bet}): "
                    )
                )

                # Check if player can afford the raise
                if raise_amount > player.cash:
                    print(f"{player.name} cannot afford to raise {raise_amount}.")
                    continue

                # Check if the other player can afford the raise
                if raise_amount > self.other_player(player).cash:
                    print()
                    print(
                        f"{self.other_player(player).name} cannot afford to raise {raise_amount}."
                    )
                    print("Raising to the maximum amount the other player can afford.")
                    raise_amount = self.other_player(player).cash

                player.lose(raise_amount)
                player.last_bet = raise_amount + self.current_bet
                self.pot += raise_amount
                self.current_bet += raise_amount
                print(f"{player.name} raises by ${raise_amount}. Pot: ${self.pot}")
                return raise_amount

            elif action == "fold":
                print(f"{player.name} folds.")
                return "fold"

            elif action == "check":
                if current_bet > player.last_bet:
                    print(
                        f"{player.name} cannot afford to check. Only call, fold or raise allowed."
                    )
                    continue
                print(f"{player.name} checks.")
                return "check"

            else:
                print("Invalid action. Try again.")

    def win(self, player):
        """
        Player wins the pot.
        """
        player.win(self.pot)
        self.pot = 0
        print(f"{self.player.name} wins the round!")

    def determine_winner(self):
        """Determines the winner based on hand scores."""
        player_score = self.calculate_score(self.player.hand + self.table_hand)
        ai_score = self.calculate_score(self.ai.hand + self.table_hand)

        if player_score > ai_score:
            self.win(self.player)

        elif ai_score > player_score:
            self.win(self.ai)

        elif player_score == ai_score == 1:
            max_player_cards = sorted([card for card in self.player.hand], reverse=True)
            max_ai_cards = sorted([card for card in self.ai.hand], reverse=True)

            for i in range(len(max_player_cards)):
                if max_player_cards[i][1] > max_ai_cards[i][1]:
                    self.win(self.player)
                    return
                elif max_ai_cards[i][1] > max_player_cards[i][1]:
                    self.win(self.ai)
                    return

            self.player.win(self.pot // 2)
            self.ai.win(self.pot // 2)
            self.pot = 0
            print("It's a tie!")

        else:
            print("You shoudnt be seeing this message")

        self.pot = 0

    def round(self):
        """
        Plays a round of poker.
        """

        # Reset the game state
        self.table_hand = []
        self.player.reset()
        self.ai.reset()

        self.pot = 0
        self.turn = 0

        self.current_bet = self.starting_bet

        # Select random player to start
        starting_player = random.choice([0, 1])

        # Deal cards
        self.deal()
        print()
        print("--------------------------NEW-ROUND---------------------------")
        print(f"{self.player.name} hand: {self.player.hand}")
        print(f"{self.ai.name} hand: {self.ai.hand} (hidden)")

        while len(self.table_hand) <= 3:
            # Bet
            print()
            print(f"----------Turn {self.turn+1}---------")
            print(f"Current bet: {self.current_bet}")
            action_player = action_ai = None
            if starting_player == 0:
                action_ai = self.choose_action(self.ai, self.turn)
                action_player = self.choose_action(self.player, self.turn)
            else:
                action_player = self.choose_action(self.player, self.turn)
                action_ai = self.choose_action(self.ai, self.turn)

            # Checks for folds
            if action_player == "fold" or action_ai == "fold":
                print("--Round over--")
                if action_player == "fold" and action_ai != "fold":
                    self.ai.win(self.pot)
                    print(f"{self.ai.name} wins {self.pot}!")
                    return
                elif action_ai == "fold" and action_player != "fold":
                    self.player.win(self.pot)
                    print(f"{self.player.name} wins {self.pot}!")
                    return
                elif action_ai == "fold" and action_player == "fold":
                    self.player.win(self.pot // 2)
                    self.ai.win(self.pot // 2)
                    print("It's a tie!")
                    return

            print("-------------------")
            print(f"{self.player.name} cash: {self.player.cash}")
            print(f"{self.ai.name} cash: {self.ai.cash} (hidden)")
            print("-------------------")

            # If turn is 3, dont draw more cards
            if self.turn == 3:
                break

            # Draw cards
            self.draw()
            print(f"{self.player.name} hand: {self.player.hand}")
            print(f"{self.ai.name} hand: {self.ai.hand} (hidden)")

            # Increment turn
            self.turn += 1

        # Determine winner
        self.determine_winner()


def play():
    human = player(100, "Player")
    ai = player(100, "AI")

    game = poker(player=human, ai=ai, starting_bet=5)

    print("Player cash:", human.cash)
    print("AI cash:", ai.cash)

    while human.cash > 0 and ai.cash > 0:
        game.round()

    if human.cash <= 0:
        print("Game over! AI wins.")
    else:
        print("Game over! Player wins.")
