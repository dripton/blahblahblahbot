import os
import sqlite3
import time

import config


DDL = """
CREATE TABLE quotes (
    quote_id INTEGER PRIMARY KEY ASC,
    quote TEXT,
    quoter TEXT,
    author TEXT,
    channel TEXT,
    insert_time INTEGER
);
"""


class Database:
    def __init__(self, sqlite_path):
        exists = os.path.exists(sqlite_path) and os.path.getsize(sqlite_path) > 0
        dirname = os.path.dirname(sqlite_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.connection = sqlite3.connect(sqlite_path)
        # Allow accessing row items by name
        self.connection.row_factory = sqlite3.Row
        if not exists:
            self.create_db()

    def create_db(self):
        self.connection.execute(DDL)

    def add_quote(self, quote, channel, quoter):
        """Add the quote if it's not already there, for this channel."""
        if not quote:
            return "Derp, I think you forgot to provide a quote!"
        if "--" in quote:
            quote, author = quote.rsplit("--", 1)
        else:
            author = quoter
        quote = quote.strip()
        author = author.strip()
        with self.connection:
            cursor = self.connection.cursor()
            query = "SELECT quote FROM quotes WHERE quote = ? AND channel = ?"
            cursor.execute(query, (quote, channel))
            row = cursor.fetchone()
            if row is not None:
                return "Quote already exists"
            query = """INSERT INTO quotes
                       (quote, quoter, author, channel, insert_time)
                       VALUES (?, ?, ?, ?, ?)"""
            seconds = int(time.time())
            cursor.execute(query, (quote, quoter, author, channel, seconds))
            return "Added quote"

    def delete_quote(self, quote, channel, user):
        """Delete the quote if user is author, quoter, or admin."""
        quote = quote.strip()
        with self.connection:
            cursor = self.connection.cursor()
            query = """SELECT quote_id, author, quoter FROM quotes
                       WHERE quote = ? AND channel = ?"""
            cursor.execute(query, (quote, channel))
            row = cursor.fetchone()
            if row is None:
                return "No such quote"
            author = row["author"]
            quoter = row["quoter"]
            if user != author and user != quoter and user not in config.admins:
                return "Permission denied"
            quote_id = row["quote_id"]
            query = "DELETE FROM quotes WHERE quote_id = ?"
            cursor.execute(query, (quote_id,))
            return "Deleted quote"

    def quote(self, channel):
        with self.connection:
            cursor = self.connection.cursor()
            query = """SELECT quote, author FROM quotes WHERE channel = ?
                       ORDER BY RANDOM() LIMIT 1"""
            cursor.execute(query, (channel,))
            row = cursor.fetchone()
            if row is None:
                return "No quotes!"
            quote = row["quote"]
            author = row["author"]
            return "%s -- %s" % (quote, author)

    def find_quote(self, quote, channel):
        with self.connection:
            cursor = self.connection.cursor()
            wild = "%" + quote + "%"
            query = """SELECT quote, author FROM quotes
                       WHERE channel = ?
                       AND quote LIKE ?
                       ORDER BY RANDOM() LIMIT 1"""
            cursor.execute(query, (channel, wild))
            row = cursor.fetchone()
            if row is None:
                return "No such quote"
            quote = row["quote"]
            author = row["author"]
            return "%s -- %s" % (quote, author)
