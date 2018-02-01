# coding=utf-8
"""Module for exposing hard-coded list of subscribers as a list of rooms and
mxids entitled to those rooms."""

class GuestListUtils(object):

    @staticmethod
    def aggregate(guest_lists):
        """Takes a list of guest lists (dicts of room_aliases to lists of mxids) and merges them
        into one big guestlist."""
        rooms = set(reduce(lambda x, y: x + y, [guest_list.keys() for guest_list in guest_lists]))

        return {room:
                list(
                    set(
                        reduce(lambda x, y: x + y,
                               [
                                   guest_list[room]
                                   if room in guest_list else []
                                   for guest_list in guest_lists
                               ]
                              )
                    )
                )
                for room in rooms}
