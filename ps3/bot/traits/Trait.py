# coding=utf-8
"""Docstring ftw"""

from abc import ABCMeta, abstractmethod

class Trait:
    """Abstract class for behaviours we want the bot to have."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_client(self):
        """Fetches the matrix client"""
        pass
