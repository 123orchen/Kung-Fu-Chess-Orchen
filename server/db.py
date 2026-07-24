"""Stage C: SQLite-backed player accounts.

"Login with username + password (save at SQLite db on server side)" per
the assignment - kept intentionally simple ("just for presentation"),
not meant to be production-grade auth:
  - First time a username is seen, it's registered with the given
    password (there's no separate "create account" step in the spec).
  - After that, the same username must be used with the same password.
  - Every account starts at rating 1200 and moves up/down by ELO.
"""
import hashlib
import os
import sqlite3
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), "players.db")
STARTING_RATING = 1200


class PlayerDB:
    def __init__(self, path: str = DB_PATH):
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.execute(
            """CREATE TABLE IF NOT EXISTS players (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                rating INTEGER NOT NULL DEFAULT 1200
            )"""
        )
        self._conn.commit()

    @staticmethod
    def _hash(username: str, password: str) -> str:
        return hashlib.sha256(f"{username}:{password}".encode()).hexdigest()

    def login_or_register(self, username: str, password: str):
        """Returns (ok, rating, error). Registers new usernames on first login."""
        h = self._hash(username, password)
        with self._lock:
            row = self._conn.execute(
                "SELECT password_hash, rating FROM players WHERE username = ?", (username,)
            ).fetchone()
            if row is None:
                self._conn.execute(
                    "INSERT INTO players (username, password_hash, rating) VALUES (?, ?, ?)",
                    (username, h, STARTING_RATING),
                )
                self._conn.commit()
                return True, STARTING_RATING, None
            stored_hash, rating = row
            if stored_hash != h:
                return False, None, "Wrong password for this username"
            return True, rating, None

    def update_ratings_after_game(self, winner_username: str, loser_username: str, k: int = 32):
        """Standard ELO update. Returns (new_winner_rating, new_loser_rating)."""
        with self._lock:
            wr = self._conn.execute(
                "SELECT rating FROM players WHERE username=?", (winner_username,)
            ).fetchone()[0]
            lr = self._conn.execute(
                "SELECT rating FROM players WHERE username=?", (loser_username,)
            ).fetchone()[0]
            expected_w = 1 / (1 + 10 ** ((lr - wr) / 400))
            new_wr = round(wr + k * (1 - expected_w))
            new_lr = round(lr + k * (0 - (1 - expected_w)))
            self._conn.execute("UPDATE players SET rating=? WHERE username=?", (new_wr, winner_username))
            self._conn.execute("UPDATE players SET rating=? WHERE username=?", (new_lr, loser_username))
            self._conn.commit()
            return new_wr, new_lr
