import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
CHOICES = ("red", "black", "even", "odd")
WEEK_TIMEZONE = ZoneInfo("America/New_York")
STARTING_BALANCE = 50
WEEKLY_BALANCE = 100


def current_week(now=None):
    now = now or datetime.now(WEEK_TIMEZONE)
    if now.tzinfo is None:
        raise ValueError("The reset time needs a timezone.")
    today = now.astimezone(WEEK_TIMEZONE).date()
    return (today - timedelta(days=(today.weekday() + 1) % 7)).isoformat()


def number_color(number):
    if type(number) is not int or not 0 <= number <= 36:
        raise ValueError("The wheel must land on a number from 0 to 36.")
    if number == 0:
        return "green"
    return "red" if number in RED_NUMBERS else "black"


def is_winner(choice, number):
    color = number_color(number)
    if choice not in CHOICES:
        raise ValueError("Choose red, black, even, or odd.")
    if number == 0:
        return False
    if choice in ("red", "black"):
        return choice == color
    return number % 2 == (0 if choice == "even" else 1)


class RouletteBank:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS guild_weeks (
                guild_id INTEGER PRIMARY KEY,
                first_week TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS balances (
                guild_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                balance INTEGER NOT NULL CHECK(balance >= 0),
                PRIMARY KEY (guild_id, week, user_id)
            );
            CREATE TABLE IF NOT EXISTS rounds (
                round_id INTEGER PRIMARY KEY,
                guild_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                choice TEXT NOT NULL,
                bet INTEGER NOT NULL,
                number INTEGER NOT NULL,
                payout INTEGER NOT NULL,
                balance INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS announcements (
                guild_id INTEGER NOT NULL,
                week TEXT NOT NULL,
                message_id INTEGER NOT NULL,
                PRIMARY KEY (guild_id, week)
            );
        """)

    def close(self):
        self.db.close()

    def starting_balance(self, guild_id, week):
        # Remember the server's first week so late joiners get the same allowance.
        self.db.execute(
            "INSERT OR IGNORE INTO guild_weeks VALUES (?, ?)", (guild_id, week)
        )
        first_week = self.db.execute(
            "SELECT first_week FROM guild_weeks WHERE guild_id=?", (guild_id,)
        ).fetchone()["first_week"]
        return STARTING_BALANCE if week == first_week else WEEKLY_BALANCE

    def balance(self, guild_id, user_id, now=None):
        week = current_week(now)
        with self.db:
            allowance = self.starting_balance(guild_id, week)
            self.db.execute(
                "INSERT OR IGNORE INTO balances VALUES (?, ?, ?, ?)",
                (guild_id, week, user_id, allowance),
            )
        return self.db.execute(
            "SELECT balance FROM balances WHERE guild_id=? AND week=? AND user_id=?",
            (guild_id, week, user_id),
        ).fetchone()["balance"]

    def play(self, round_id, guild_id, user_id, week, choice, bet, now=None):
        if choice not in CHOICES:
            raise ValueError("Choose red, black, even, or odd.")
        if type(bet) is not int or bet < 1:
            raise ValueError("Bet a positive whole-dollar amount.")

        # Save the result and money together, before showing the animation.
        # A repeated button event for this message cannot charge or pay twice.
        with self.db:
            self.db.execute("BEGIN IMMEDIATE")
            previous = self.db.execute(
                "SELECT * FROM rounds WHERE round_id=?", (round_id,)
            ).fetchone()
            if previous:
                if (previous["guild_id"], previous["user_id"], previous["week"],
                        previous["choice"], previous["bet"]) != (
                        guild_id, user_id, week, choice, bet):
                    raise ValueError("This spin has already been played.")
                return dict(previous)
            if week != current_week(now):
                raise ValueError("A new week started. Start a new roulette game to use your $100.")
            allowance = self.starting_balance(guild_id, week)
            self.db.execute(
                "INSERT OR IGNORE INTO balances VALUES (?, ?, ?, ?)",
                (guild_id, week, user_id, allowance),
            )
            balance = self.db.execute(
                "SELECT balance FROM balances WHERE guild_id=? AND week=? AND user_id=?",
                (guild_id, week, user_id),
            ).fetchone()["balance"]
            if bet > balance:
                raise ValueError(f"You only have ${balance:,}. Choose a smaller bet.")
            if balance + bet > 2**63 - 1:
                raise ValueError("That bet would exceed the balance limit.")
            number = secrets.randbelow(37)
            payout = bet * 2 if is_winner(choice, number) else 0
            balance += payout - bet
            self.db.execute(
                "UPDATE balances SET balance=? WHERE guild_id=? AND week=? AND user_id=?",
                (balance, guild_id, week, user_id),
            )
            self.db.execute(
                "INSERT INTO rounds VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (round_id, guild_id, week, user_id, choice, bet, number, payout, balance),
            )
            return dict(self.db.execute(
                "SELECT * FROM rounds WHERE round_id=?", (round_id,)
            ).fetchone())

    def leaderboard(self, guild_id, week):
        return self.db.execute(
            "SELECT user_id, balance FROM balances WHERE guild_id=? AND week=? "
            "ORDER BY balance DESC, user_id ASC", (guild_id, week)
        ).fetchall()

    def previous_week(self, guild_id, now=None):
        return self.db.execute(
            "SELECT MAX(week) FROM balances WHERE guild_id=? AND week<?",
            (guild_id, current_week(now)),
        ).fetchone()[0]

    def set_channel(self, guild_id, channel_id):
        with self.db:
            self.db.execute(
                "INSERT INTO channels VALUES (?, ?) ON CONFLICT(guild_id) "
                "DO UPDATE SET channel_id=excluded.channel_id", (guild_id, channel_id)
            )

    def pending_announcements(self, now=None):
        return self.db.execute(
            "SELECT DISTINCT b.guild_id, b.week, c.channel_id FROM balances b "
            "JOIN channels c ON b.guild_id=c.guild_id "
            "LEFT JOIN announcements a ON b.guild_id=a.guild_id AND b.week=a.week "
            "WHERE b.week<? AND a.message_id IS NULL ORDER BY b.week, b.guild_id",
            (current_week(now),),
        ).fetchall()

    def mark_announced(self, guild_id, week, message_id):
        with self.db:
            self.db.execute(
                "INSERT OR IGNORE INTO announcements VALUES (?, ?, ?)",
                (guild_id, week, message_id),
            )
