import sqlite3
import os

conn = None


def init(path):
    global conn
    conn = sqlite3.connect(path)

    return conn


def get_conn():
    """

    :return: connection object
    :rtype: sqlite3.Connection
    """
    global conn
    return conn



def fetch(query):
    cursor = get_conn().cursor()
    cursor.execute(query)
    return cursor


def commit():
    get_conn().commit()
