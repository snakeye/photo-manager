import sqlite3
import os

conn = None


def init(path):
    global conn
    conn = sqlite3.connect(os.path.join(path, 'photos.db'))

    return conn
