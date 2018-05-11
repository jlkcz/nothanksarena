#!/usr/bin/python3

import random
from . import AbstractBot

DEBUG = 0
def debug(msg):
    if DEBUG == 1:
        print(msg)

class TrackingBot(AbstractBot.AbstractBot):
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
