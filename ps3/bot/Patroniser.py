# coding=utf-8
"""The lovely bot who is fun to be with."""

from matrix_client.client import MatrixClient

from ps3.bot.traits import Bouncer
from ps3.bot.traits import PA

class Patroniser(Bouncer, PA):
    """Bot to do the needful"""
    client = None

    def __init__(self, username, password):
        self.client = MatrixClient('https://matrix.org')
        self.client.login_with_password(username=username,
                                        password=password)

    def get_client(self):
        """Provide the matrix client for all the myriad purposes."""
        return self.client
