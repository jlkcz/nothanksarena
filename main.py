#!/usr/bin/python3

import sys
import random
from operator import itemgetter

DEBUG = 0
def debug(msg):
    if DEBUG == 1:
        print(msg)

class CheatingException(Exception):
    """ Exception raised if some player tries to say No Thanks without tokens"""

class AbstractBot(object):
    def __init__(self):
        self.identifier = "abstract"

    def notify_new_card(self, cardno):
        pass

    def decide(self, card, tokens):
        return True

class DummyBot(AbstractBot):
    """Dummy bot"""
    def __init__(self):
        self.identifier = "dummy"

    def __repr__(self):
        return "DummyBot v1.0"

    def decide(self, card, tokens):
        return random.random() < 0.5

class LessDummyBot(AbstractBot):
    """Dummy bot"""
    def __init__(self):
        self.tokens = 11
        self.identifier = "lessdummy"

    def __repr__(self):
        return "LessDummyBot v1.0"
    
    def decide(self, card, tokens):
        return random.random() < 0.125


class TrackingBot(object):
    """Dummy bot"""
    def __init__(self):
        self.identifier = "tracking"
        self.tokens = 11
        self.cards = []
        self.played_cards = []


    def __repr__(self):
        return "TrackingBot v1.0"

    def notify_new_card(self, cardno):
        self.played_cards.append(cardno)

    def decide(self, card, tokens):
        if self.tokens == 0: #No tokens, we accept whatever comes
            decision = True
        elif tokens == 0: #No tokens? Let someone else get it...
            decision = False
        elif (card+1) in self.cards and tokens > 0: #this is a free card
            decision = True
        elif tokens > card/2: #this is a nice offer
            decision = True
        else:
            decision = random.random() < 0.25

        if decision:
            self.cards.append(card)
            self.tokens += tokens
            debug("Decided to take the card #{} with {} tokens. Now I have {} tokens and cards: {}".format(card, tokens, self.tokens, self.cards))
        else:
            self.tokens -= 1
            debug("No thanks to card #{} with {} tokens. I have {} tokens and cards: {}".format(card, tokens, self.tokens, self.cards))
            
        return decision


class PlayerState(object):
    """ Holds data for players so they can't cheat"""

    def __init__(self):
        self.tokens = 11
        self.cards = []

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
            if card-1 == last_card: #is consecutive
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
        self.played_cards = []
        self.players_data = []
        self.card_in_play = None
        self.tokens_in_play = 0
        self.on_turn = 0
        
        self.playersAI = list(args)
        random.shuffle(self.playersAI) # we want randomized order
        
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
        #player gets card and tokens
        debug("Player {} took card #{} for {} tokens".format(self.on_turn, self.card_in_play, self.tokens_in_play))
        self.players_data[self.on_turn].add_card(self.card_in_play)
        self.players_data[self.on_turn].add_tokens(self.tokens_in_play)
       
    def notify_new_card(self):
        for player in self.playersAI:
            player.notify_new_card(self.card_in_play)

    def run_game_loop(self):
        #initialize data
        debug("Starting the game")
        debug(self.num_players)
        self.players_data = [PlayerState() for x in range(0,self.num_players)]
        debug(self.players_data)

        self.deck = list(range(3,36))
        random.shuffle(self.deck)
        self.deck = self.deck[0:23]
        debug(self.deck)

        
        #run the game itself
        while self.deck:
            #get a new card and remove all tokens
            self.card_in_play = self.deck.pop(0)
            self.tokens_in_play = 0
            self.notify_new_card()
            debug("new card in play {}".format(self.card_in_play))
            

            #Lets play this round
            while True:
                if self.playersAI[self.on_turn].decide(self.card_in_play, self.tokens_in_play):
                    self.take_card()
                    break #someone took the card, the round ends
                else:
                    self.no_thanks()

            #clean up after round
            self.played_cards.append(self.card_in_play)
        #Game is finished, count scores
        for player in self.players_data:
            player.count_score()


    def print_results(self):
        scores = {player.score:ordnum for ordnum, player in enumerate(self.players_data)}
        for order, score in enumerate(sorted(scores)):
            num = scores[score]
            print("#{} place; {} points: {}#{}".format(order+1 ,score, self.playersAI[num], num))
       
    def get_programmatic_results(self):
        scores = {player.score:ordnum for ordnum, player in enumerate(self.players_data)}
        results = []
        for order, score in enumerate(sorted(scores)):
            num = scores[score]
            results.append({"ai": self.playersAI[num].identifier, "score": score, "position": order+1})
        return results
        

if __name__ == '__main__x':
    game = GameState(LessDummyBot(),TrackingBot())
    game.run_game_loop()
    game.print_results()
    sys.exit(0)

if __name__ == '__main__':
    rounds = 100000
    skipped_rounds = 0
    overall_score = {}
    overall_position = {}

    #Here define how many bots of each type are competing, for statistics
    bots_of_type = 1
    for i in range(rounds+1):
        #Here define bots competing
        game = GameState(LessDummyBot(),TrackingBot())
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

    #Do not count rounds, where decision failed
    real_rounds = (rounds - skipped_rounds)*bots_of_type
    
    print("General results for {} rounds, {} rounds skipped due to cheating".format(rounds, skipped_rounds))
    print("There were {} instances of each bot".format(bots_of_type))
    for bottype in overall_score.keys():
        print("Bot: {} had average position: {} and average score: {}".format(bottype, overall_position[bottype]/real_rounds, overall_score[bottype]/real_rounds))