#!/usr/bin/python3

import random
from . import AbstractBot

class DummyBot(AbstractBot.AbstractBot):
    """Dummy bot"""
    def __init__(self):
        self.identifier = "dummy"

    def __repr__(self):
        return "DummyBot v1.0"

    def decide(self, card, tokens):
        return random.random() < 0.5
