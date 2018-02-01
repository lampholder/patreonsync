# coding=utf-8
"""Module for storing various mappings; patreion id to mxid, email to mxid, etc."""

import sqlite3

from collections import defaultdict

class AddressBook(object):

    def __init__(self):
        self._db = sqlite3.connect('addressbook.db')

    def mapping(self):
        mapping = defaultdict(list)

        query = 'select patreonid, mxid from patreonid_mxid'
        cursor = self._db.cursor()
        cursor.execute(query)

        for row in cursor.fetchall():
            mapping[row[0]].append(row[1])

        return mapping

    def get_mxids(self, patreonid):
        query = 'select mxid  from patreonid_mxid where patreonid = ?'
        cursor = self._db.cursor()
        cursor.execute(query, (patreonid, ))
        return [row[0] for row in cursor.fetchall()]

    def add(self, patreonid, mxid):
        query = 'insert into patreonid_mxid (patreonid, mxid) values (?, ?)'
        cursor = self._db.cursor()
        cursor.execute(query, (patreonid, mxid, ))
        self._db.commit()
