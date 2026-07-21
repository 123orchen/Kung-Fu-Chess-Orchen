import time

_FILES = 'abcdefgh'


class MoveHistoryEntry:
    """A single logged command. received_at is a real (wall-clock) server-side
    timestamp - independent of the simulated in-game clock used for move/rest
    timing - so it reflects when the command actually arrived.

    game_time_ms is the in-game clock value *at the moment the command was
    received* (not when the move lands) - used for the elapsed-time column
    shown in the GUI move log."""

    def __init__(self, color, piece_type, from_r, from_c, to_r, to_c, move_type, game_time_ms):
        self.color = color
        self.piece_type = piece_type
        self.from_r, self.from_c = from_r, from_c
        self.to_r, self.to_c = to_r, to_c
        self.move_type = move_type
        self.game_time_ms = game_time_ms
        self.received_at = time.time()

    @staticmethod
    def _square_name(r, c):
        return f"{_FILES[c]}{8 - r}"

    @property
    def notation(self):
        """Simplified algebraic-style notation: destination square, prefixed
        with the piece letter for non-pawns. Real-time play means a move's
        eventual capture outcome isn't known when the command is received,
        so (unlike standard chess notation) no 'x'/'+' markers are added.
        Jumps are marked with a trailing '^'."""
        dest = self._square_name(self.to_r, self.to_c)
        prefix = '' if self.piece_type == 'P' else self.piece_type
        suffix = '^' if self.move_type == 'jump' else ''
        return f"{prefix}{dest}{suffix}"

    @property
    def elapsed_label(self):
        """mm:ss.mmm since the game started, based on the in-game clock."""
        total_ms = max(0, self.game_time_ms)
        minutes = total_ms // 60000
        seconds = (total_ms % 60000) / 1000.0
        return f"{minutes:02d}:{seconds:06.3f}"

    def __str__(self):
        return (f"[{self.received_at:.3f}] {self.color}{self.piece_type} "
                f"{self.move_type} ({self.from_r},{self.from_c})->({self.to_r},{self.to_c})")


class MoveHistory:
    """Chronological log of every move command received, interleaved across
    both players (real-time play means there's no single "turn order")."""

    def __init__(self):
        self._entries = []

    def record(self, color, piece_type, from_r, from_c, to_r, to_c, move_type, game_time_ms):
        entry = MoveHistoryEntry(color, piece_type, from_r, from_c, to_r, to_c, move_type, game_time_ms)
        self._entries.append(entry)
        return entry

    def all(self):
        return list(self._entries)

    def for_color(self, color):
        return [e for e in self._entries if e.color == color]

    def __len__(self):
        return len(self._entries)
