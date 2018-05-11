#!/usr/bin/python3

import sys
import random
import bots

DEBUG = 0


def debug(msg):
    if DEBUG == 1:
        print(msg)


class CheatingException(Exception):
    """ Exception raised if player tries to say No Thanks without tokens"""


class PlayerState(object):
    """ Holds data for players so they can't cheat"""

    def __init__(self):
        self.tokens = 11
        self.cards = []
        self.score = 0

    def __repr__(self):
        return "Player with {} points ({} tokens, cards {})".format(self.count_score(), self.tokens, self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def add_tokens(self, num):
        self.tokens += num

    def pay_token(self):
        if self.tokens <= 0:
            raise CheatingException("Cheater! He does not have enough tokens")
        else:
            self.tokens -= 1

    def count_score(self):
        """ Counts final score by eliminating consecutive cards"""
        self.cards.sort()
        recounted_cards = []
        last_card = -1

        for card in self.cards:
            if card-1 == last_card:  # is consecutive
                last_card = card
                continue
            else:
                last_card = card
                recounted_cards.append(card)

        self.score = sum(recounted_cards) - self.tokens


class GameState(object):
    """ Holds game state and checks rules """
    def __init__(self, *args):
        """ args are playing bots"""
        self.deck = []
        self.players_data = []
        self.card_in_play = None
        self.tokens_in_play = 0
        self.on_turn = 0

        self.players_ai = list(args)
        random.shuffle(self.players_ai)  # we want randomized order

        self.num_players = len(args)
        if self.num_players < 2:
            print("This is not a solo game")
            sys.exit(1)

    def change_turn(self):
        self.on_turn = (self.on_turn + 1) % self.num_players

    def no_thanks(self):
        debug("Player {} said No Thanks!".format(self.on_turn))
        self.players_data[self.on_turn].pay_token()
        self.tokens_in_play += 1
        self.change_turn()

    def take_card(self):
        # player gets the card and tokens
        debug("Player {} took card #{} for {} tokens".format(self.on_turn, self.card_in_play, self.tokens_in_play))
        self.players_data[self.on_turn].add_card(self.card_in_play)
        self.players_data[self.on_turn].add_tokens(self.tokens_in_play)

    def notify_new_card(self):
        for player in self.players_ai:
            player.notify_new_card(self.card_in_play)

    def run_game_loop(self):
        # initialize data
        debug("Starting the game")
        debug(self.num_players)
        self.players_data = [PlayerState() for x in range(self.num_players)]
        debug(self.players_data)

        self.deck = list(range(3, 36))
        random.shuffle(self.deck)
        self.deck = self.deck[0:23]
        debug(self.deck)

        # run the game itself
        while self.deck:
            # get a new card and remove all tokens
            self.card_in_play = self.deck.pop(0)
            self.tokens_in_play = 0
            self.notify_new_card()
            debug("new card in play {}".format(self.card_in_play))

            # Lets play this round
            while True:
                if self.players_ai[self.on_turn].decide(self.card_in_play, self.tokens_in_play):
                    self.take_card()
                    break  # someone took the card, the round ends
                else:
                    self.no_thanks()

        # Game is finished, count scores
        for player in self.players_data:
            player.count_score()

    def print_results(self):
        scores = {player.score: ordnum for ordnum, player in enumerate(self.players_data)}
        for order, score in enumerate(sorted(scores)):
            num = scores[score]
            print("#{} place; {} points: {}#{}".format(order+1, score, self.players_ai[num], num))

    def get_programmatic_results(self):
        scores = {player.score: ordnum for ordnum, player in enumerate(self.players_data)}
        data = []
        for order, score in enumerate(sorted(scores)):
            num = scores[score]
            data.append({"ai": self.players_ai[num].identifier, "score": score, "position": order+1})
        return data


if __name__ == '__main__x':
    game = GameState(bots.LessDummyBot(), bots.TrackingBot())
    game.run_game_loop()
    game.print_results()
    sys.exit(0)

if __name__ == '__main__':
    rounds = 100000
    skipped_rounds = 0
    overall_score = {}
    overall_position = {}

    # Here define how many bots of each type are competing, for statistics
    bots_of_type = 1
    for i in range(rounds+1):
        # Here define bots competing
        game = GameState(bots.LessDummyBot(), bots.TrackingBot())
        try:
            game.run_game_loop()
        except CheatingException:
            skipped_rounds += 1
            debug("Skipping turn because of a cheater")
            continue
        results = game.get_programmatic_results()
        for bot in results:
            if not bot["ai"] in overall_score:
                overall_score[bot["ai"]] = 0
            if not bot["ai"] in overall_position:
                overall_position[bot["ai"]] = 0

            overall_position[bot["ai"]] += bot["position"]
            overall_score[bot["ai"]] += bot["score"]

    # Do not count rounds, where decision failed
    real_rounds = (rounds - skipped_rounds)*bots_of_type

    print("General results for {} rounds, {} rounds skipped due to cheating".format(rounds, skipped_rounds))
    print("There were {} instances of each bot".format(bots_of_type))
    for bottype in overall_score.keys():
        print("Bot: {} had average position: {} and average score: {}".format(bottype, overall_position[bottype]/real_rounds, overall_score[bottype]/real_rounds))
