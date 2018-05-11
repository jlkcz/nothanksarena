#!/usr/bin/python3


class AbstractBot(object):
    def __init__(self):
        self.identifier = "abstract"

    def notify_new_card(self, cardno):
        pass

    def decide(self, card, tokens):
        return True
