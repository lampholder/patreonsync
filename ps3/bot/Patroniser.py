#!/usr/bin/env python3
"""The lovely bot who is fun to be with."""

from matrix_client.client import MatrixClient

from ps3.bot.traits import PA, Bouncer


class Patroniser(Bouncer, PA):
    """Bot to do the needful"""

    client: MatrixClient = None

    def __init__(self, username, password):
        self.client = MatrixClient("https://matrix.org")
        self.client.login_with_password_no_sync(username=username, password=password)

    def get_client(self):
        """Provide the matrix client for all the myriad purposes."""
        return self.client
