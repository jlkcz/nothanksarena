#!/usr/bin/python3

import random
from . import AbstractBot 

class LessDummyBot(AbstractBot.AbstractBot):
    """Dummy bot"""
    def __init__(self):
        self.tokens = 11
        self.identifier = "lessdummy"

    def __repr__(self):
        return "LessDummyBot v1.0"
    
    def decide(self, card, tokens):
        return random.random() < 0.125
