# -*- coding: utf-8 -*-
'''
@author: Alex Nulman <anulman@cs.haifa.ac.il>

this is teh main app, it takes no parameters, instead update config.py
'''

import sqlite3
import os

def internals_checker():
    """checks if the internals.db file exists
    and creates it, and its tables if it doesnt"""
    if not os.path.exists('internals.DB'):
        conn = sqlite3.connect('internals.DB')
        conn.execute('''CREATE TABLE IF NOT EXISTS "presets" (
            `items` TEXT,
            `json`  TEXT,
            `name`  TEXT,
            PRIMARY KEY(`name`)
            );''')
        conn.close()


if __name__ == '__main__':
    internals_checker()
