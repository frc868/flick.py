import secrets
from datetime import datetime, timedelta
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
    def __init__(self):
        # These lists live only for this bot session.
        self.guild_weeks = []
        self.balances = []
        self.rounds = []
        self.channels = []
        self.announcements = []

    def starting_balance(self, guild_id, week):
        for guild in self.guild_weeks:
            if guild["guild_id"] == guild_id:
                return (
                    STARTING_BALANCE if week == guild["first_week"] else WEEKLY_BALANCE
                )
        self.guild_weeks.append({"guild_id": guild_id, "first_week": week})
        return STARTING_BALANCE

    def player(self, guild_id, user_id, week):
        for row in self.balances:
            if (row["guild_id"], row["user_id"], row["week"]) == (
                guild_id,
                user_id,
                week,
            ):
                return row
        row = {
            "guild_id": guild_id,
            "user_id": user_id,
            "week": week,
            "balance": self.starting_balance(guild_id, week),
        }
        self.balances.append(row)
        return row

    def balance(self, guild_id, user_id, now=None):
        return self.player(guild_id, user_id, current_week(now))["balance"]

    def play(self, round_id, guild_id, user_id, week, choice, bet, now=None):
        if choice not in CHOICES:
            raise ValueError("Choose red, black, even, or odd.")
        if type(bet) is not int or bet < 1:
            raise ValueError("Bet a positive whole number of frisbees.")
        for previous in self.rounds:
            if previous["round_id"] == round_id:
                if (
                    previous["guild_id"],
                    previous["user_id"],
                    previous["week"],
                    previous["choice"],
                    previous["bet"],
                ) != (guild_id, user_id, week, choice, bet):
                    raise ValueError("This spin has already been played.")
                return previous.copy()
        if week != current_week(now):
            raise ValueError(
                "A new week started. Start a new roulette game to use your 100 frisbees."
            )
        player = self.player(guild_id, user_id, week)
        balance = player["balance"]
        if bet > balance:
            raise ValueError(
                f"You only have {balance:,} frisbees. Choose a smaller bet."
            )
        if balance + bet > 2**63 - 1:
            raise ValueError("That bet would exceed the balance limit.")
        number = secrets.randbelow(37)
        payout = bet * 2 if is_winner(choice, number) else 0
        result = {
            "round_id": round_id,
            "guild_id": guild_id,
            "user_id": user_id,
            "week": week,
            "choice": choice,
            "bet": bet,
            "number": number,
            "payout": payout,
            "balance": balance + payout - bet,
        }
        # No await here: record the spin before the animation yields to other clicks.
        self.rounds.append(result)
        player["balance"] = result["balance"]
        return result.copy()

    def leaderboard(self, guild_id, week):
        rows = [
            row.copy()
            for row in self.balances
            if row["guild_id"] == guild_id and row["week"] == week
        ]
        return sorted(rows, key=lambda row: (-row["balance"], row["user_id"]))

    def previous_week(self, guild_id, now=None):
        week = current_week(now)
        return max(
            (
                row["week"]
                for row in self.balances
                if row["guild_id"] == guild_id and row["week"] < week
            ),
            default=None,
        )

    def set_channel(self, guild_id, channel_id):
        for channel in self.channels:
            if channel["guild_id"] == guild_id:
                channel["channel_id"] = channel_id
                return
        self.channels.append({"guild_id": guild_id, "channel_id": channel_id})

    def pending_announcements(self, now=None):
        week = current_week(now)
        pending = []
        for channel in self.channels:
            guild_id = channel["guild_id"]
            weeks = sorted(
                {
                    row["week"]
                    for row in self.balances
                    if row["guild_id"] == guild_id and row["week"] < week
                }
            )
            for finished_week in weeks:
                if not any(
                    row["guild_id"] == guild_id and row["week"] == finished_week
                    for row in self.announcements
                ):
                    pending.append({**channel, "week": finished_week})
        return sorted(pending, key=lambda row: (row["week"], row["guild_id"]))

    def mark_announced(self, guild_id, week, message_id):
        if not any(
            row["guild_id"] == guild_id and row["week"] == week
            for row in self.announcements
        ):
            self.announcements.append(
                {
                    "guild_id": guild_id,
                    "week": week,
                    "message_id": message_id,
                }
            )
