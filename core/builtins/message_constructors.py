from .assigned_element import *

class MessageChain:
    def __init__(self, *messages):
        self.messages = list(messages)

    def __str__(self):
        return "MessageChain(" + ", ".join(str(m) for m in self.messages) + ")"

    def __repr__(self):
        return str(self)