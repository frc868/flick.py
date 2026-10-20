import asyncio
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import discord
from discord.ext import commands

from bot.cogs.games import Roulette, RouletteView
from bot.helpers.roulette_bank import CHOICES, RouletteBank, current_week, is_winner, number_color


MONDAY = datetime(2026, 10, 19, 12, tzinfo=timezone.utc)
NEXT_MONDAY = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


class BankTests(unittest.TestCase):
    def setUp(self):
        self.bank = RouletteBank()

    def play(self, number=1, bet=10, choice='red', user=10, round_id=100, now=MONDAY):
        with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=number):
            return self.bank.play(round_id, 1, user, current_week(now), choice, bet, now)

    def test_all_numbers_and_choices(self):
        reds = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        for number in range(37):
            for choice in CHOICES:
                with self.subTest(number=number, choice=choice):
                    expected = number != 0 and {
                        'red': number in reds,
                        'black': number not in reds,
                        'even': number % 2 == 0,
                        'odd': number % 2 == 1,
                    }[choice]
                    self.assertEqual(is_winner(choice, number), expected)
                    identifier = 1000 + number * 4 + CHOICES.index(choice)
                    result = self.play(number, choice=choice, user=identifier, round_id=identifier)
                    self.assertEqual(result['balance'], 60 if expected else 40)
                    self.assertEqual(result['payout'], 20 if expected else 0)

    def test_wheel_colors_balanced(self):
        colors = [number_color(n) for n in range(37)]
        self.assertEqual([colors.count(c) for c in ('red', 'black', 'green')], [18, 18, 1])

    def test_invalid_wheel_or_choice(self):
        for value in [-1, 37, 1.5, True]:
            with self.assertRaises(ValueError):
                number_color(value)
        with self.assertRaises(ValueError):
            is_winner('purple', 1)

    def test_initial_money_and_server_isolation(self):
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 50)
        self.play()
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 60)
        self.assertEqual(self.bank.balance(2, 10, MONDAY), 50)
        self.assertEqual(self.bank.balance(1, 11, MONDAY), 50)

    def test_invalid_bets_do_not_spend_money_or_roll(self):
        for amount in [0, -1, 51, 1.5, '10', True]:
            with self.subTest(amount=amount), patch('bot.helpers.roulette_bank.secrets.randbelow') as roll:
                with self.assertRaises(ValueError):
                    self.bank.play(100, 1, 10, current_week(MONDAY), 'red', amount, MONDAY)
                roll.assert_not_called()
                self.assertEqual(self.bank.balance(1, 10, MONDAY), 50)

    def test_all_in_win(self):
        self.assertEqual(self.play(bet=50)['balance'], 100)

    def test_broke_player_waits_until_next_week(self):
        self.assertEqual(self.play(number=0, bet=50)['balance'], 0)
        with self.assertRaises(ValueError):
            self.play(round_id=101, bet=1)
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 100)

    def test_duplicate_round_is_not_paid_twice(self):
        first = self.play()
        with patch('bot.helpers.roulette_bank.secrets.randbelow') as roll:
            second = self.bank.play(100, 1, 10, current_week(MONDAY), 'red', 10, MONDAY)
            roll.assert_not_called()
        self.assertEqual(first, second)
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 60)

    def test_duplicate_round_cannot_change_player_choice_or_stake(self):
        self.play()
        for args in [(1, 11, 'red', 10), (1, 10, 'black', 10), (1, 10, 'red', 20), (2, 10, 'red', 10)]:
            guild, user, choice, bet = args
            with self.assertRaises(ValueError):
                self.bank.play(100, guild, user, current_week(MONDAY), choice, bet, MONDAY)

    def test_separate_menus_cannot_overspend(self):
        self.play(number=0, bet=40)
        with self.assertRaises(ValueError):
            self.play(round_id=101, bet=40)
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 10)

    def test_failed_roll_does_not_spend(self):
        with patch('bot.helpers.roulette_bank.secrets.randbelow', side_effect=RuntimeError):
            with self.assertRaises(RuntimeError):
                self.bank.play(100, 1, 10, current_week(MONDAY), 'red', 10, MONDAY)
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 50)
        self.assertEqual(self.bank.rounds, [])

    def test_restart_clears_money_history_and_channel(self):
        self.play()
        self.bank.set_channel(1, 999)
        self.bank = RouletteBank()
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 50)
        self.assertEqual(self.bank.leaderboard(1, current_week(MONDAY)), [])
        self.assertIsNone(self.bank.previous_week(1, NEXT_MONDAY))
        self.assertEqual(self.bank.pending_announcements(NEXT_MONDAY), [])
        self.assertEqual(self.bank.channels, [])
        self.assertEqual(self.bank.rounds, [])

    def test_returned_records_cannot_change_money_or_rounds(self):
        result = self.play()
        result['balance'] = 999
        rows = self.bank.leaderboard(1, current_week(MONDAY))
        rows[0]['balance'] = 999
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 60)
        self.assertEqual(self.play()['balance'], 60)

    def test_channel_can_be_changed_without_duplicate_posts(self):
        self.play()
        self.bank.set_channel(1, 999)
        self.bank.set_channel(1, 888)
        pending = self.bank.pending_announcements(NEXT_MONDAY)
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]['channel_id'], 888)

    def test_weekly_reset_preserves_final_standings(self):
        self.play()
        self.play(number=0, user=11, round_id=101)
        old_week = current_week(MONDAY)
        self.assertEqual([(r['user_id'], r['balance']) for r in self.bank.leaderboard(1, old_week)], [(10, 60), (11, 40)])
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 100)
        self.assertEqual(self.bank.balance(1, 11, NEXT_MONDAY), 100)
        self.assertEqual(self.bank.previous_week(1, NEXT_MONDAY), old_week)
        self.assertEqual(self.bank.leaderboard(1, old_week)[0]['balance'], 60)

    def test_menu_from_old_week_is_rejected_without_charge(self):
        self.bank.balance(1, 10, MONDAY)
        with self.assertRaisesRegex(ValueError, 'new week'):
            self.bank.play(100, 1, 10, current_week(MONDAY), 'red', 10, NEXT_MONDAY)
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 100)

    def test_eastern_midnight_and_daylight_saving_boundaries(self):
        for instant, expected in [
            ('2026-10-25T03:59:59+00:00', '2026-10-18'),
            ('2026-10-25T04:00:00+00:00', '2026-10-25'),
            ('2026-11-01T03:59:59+00:00', '2026-10-25'),
            ('2026-11-01T04:00:00+00:00', '2026-11-01'),
            ('2026-11-08T04:59:59+00:00', '2026-11-01'),
            ('2026-11-08T05:00:00+00:00', '2026-11-08'),
            ('2026-03-08T04:59:59+00:00', '2026-03-01'),
            ('2026-03-08T05:00:00+00:00', '2026-03-08'),
            ('2026-03-15T03:59:59+00:00', '2026-03-08'),
            ('2026-03-15T04:00:00+00:00', '2026-03-15'),
            ('2027-01-01T12:00:00+00:00', '2026-12-27'),
        ]:
            with self.subTest(instant=instant):
                self.assertEqual(current_week(datetime.fromisoformat(instant)), expected)
        with self.assertRaises(ValueError):
            current_week(datetime(2026, 10, 19))

    def test_missed_weeks_announced_once(self):
        self.play()
        self.bank.set_channel(1, 999)
        self.assertEqual(len(self.bank.pending_announcements(MONDAY)), 0)
        pending = self.bank.pending_announcements(NEXT_MONDAY)
        self.assertEqual(len(pending), 1)
        self.bank.mark_announced(1, pending[0]['week'], 123)
        self.bank.mark_announced(1, pending[0]['week'], 123)
        self.assertEqual(len(self.bank.pending_announcements(NEXT_MONDAY)), 0)

    def test_without_channel_keeps_standings_for_session(self):
        self.play()
        self.assertEqual(len(self.bank.pending_announcements(NEXT_MONDAY)), 0)
        self.assertEqual(self.bank.previous_week(1, NEXT_MONDAY), current_week(MONDAY))
        self.bank.set_channel(1, 999)
        self.assertEqual(len(self.bank.pending_announcements(NEXT_MONDAY)), 1)

    def test_every_first_week_player_gets_fifty_without_refills(self):
        for user in range(10, 15):
            self.assertEqual(self.bank.balance(1, user, MONDAY), 50)
        self.play(number=0, user=10, bet=50)
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 0)
        self.assertEqual(self.bank.balance(1, 11, MONDAY), 50)

    def test_sunday_cutoff_gives_returning_and_new_players_one_hundred(self):
        self.play(number=1, bet=50)
        before = datetime(2026, 10, 25, 3, 59, 59, tzinfo=timezone.utc)
        after = datetime(2026, 10, 25, 4, tzinfo=timezone.utc)
        self.assertEqual(self.bank.balance(1, 10, before), 100)
        self.assertEqual(self.bank.balance(1, 11, before), 50)
        self.assertEqual(self.bank.balance(1, 10, after), 100)
        self.assertEqual(self.bank.balance(1, 11, after), 100)
        self.assertEqual(self.bank.balance(1, 12, after), 100)
        self.assertEqual(self.bank.balance(2, 10, after), 50)

    def test_reset_discards_winnings_during_session(self):
        self.play(number=1, bet=50)
        self.play(number=1, bet=100, round_id=101)
        self.assertEqual(self.bank.balance(1, 10, MONDAY), 200)
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 100)
        self.assertEqual(self.bank.balance(1, 11, NEXT_MONDAY), 100)
        self.play(number=0, bet=100, round_id=102, now=NEXT_MONDAY)
        self.assertEqual(self.bank.balance(1, 10, NEXT_MONDAY), 0)
        later = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)
        self.assertEqual(self.bank.balance(1, 10, later), 100)

    def test_first_bet_in_later_week_receives_hundred_without_balance_command(self):
        self.bank.balance(1, 10, MONDAY)
        result = self.play(number=1, bet=100, user=11, round_id=101, now=NEXT_MONDAY)
        self.assertEqual(result['balance'], 200)


class DiscordTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.bank = RouletteBank()
        self.player = SimpleNamespace(id=10, mention='<@10>')

    def interaction(self, user=10, message_id=100):
        return SimpleNamespace(
            user=SimpleNamespace(id=user), message=SimpleNamespace(id=message_id),
            response=SimpleNamespace(defer=AsyncMock(), send_message=AsyncMock()),
            edit_original_response=AsyncMock(),
        )

    async def test_all_four_actual_button_callbacks(self):
        for index, choice in enumerate(CHOICES):
            with self.subTest(choice=choice):
                player = SimpleNamespace(id=100 + index, mention=f'<@{100 + index}>')
                view = RouletteView(player, 1, 10, self.bank)
                interaction = self.interaction(user=player.id, message_id=1000 + index)
                button = next(b for b in view.children if b.label.lower() == choice)
                with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=1), patch('bot.cogs.games.asyncio.sleep', new_callable=AsyncMock):
                    await button.callback(interaction)
                self.assertEqual(interaction.edit_original_response.await_count, 5)
                embed = interaction.edit_original_response.call_args.kwargs['embed']
                self.assertIn('1', embed.description)
                self.assertTrue(all(b.disabled for b in view.children))
                self.assertTrue(view.is_finished())
                self.assertEqual(self.bank.balance(1, player.id), 60 if choice in ('red', 'odd') else 40)

    async def test_other_player_cannot_bet(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        interaction = self.interaction(user=11)
        await view.red.callback(interaction)
        interaction.response.send_message.assert_awaited_once()
        interaction.response.defer.assert_not_awaited()
        self.assertEqual(self.bank.balance(1, 10), 50)
        self.assertFalse(view.finished)
        view.stop()

    async def test_simultaneous_clicks_pay_once(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        first, second = self.interaction(), self.interaction()
        with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=1) as roll, patch('bot.cogs.games.asyncio.sleep', new_callable=AsyncMock):
            await asyncio.gather(view.red.callback(first), view.black.callback(second))
        roll.assert_called_once_with(37)
        self.assertEqual(self.bank.balance(1, 10), 60)
        second.response.send_message.assert_awaited_once()

    async def test_timeout_charges_nothing_and_disables_buttons(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        view.msg = SimpleNamespace(edit=AsyncMock())
        await view.on_timeout()
        self.assertTrue(all(b.disabled for b in view.children))
        self.assertEqual(self.bank.balance(1, 10), 50)
        await view.red.callback(self.interaction())
        self.assertEqual(self.bank.balance(1, 10), 50)
        view.stop()

    async def test_menu_rechecks_balance_at_click(self):
        view = RouletteView(self.player, 1, 40, self.bank)
        with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=0):
            self.bank.play(99, 1, 10, current_week(), 'red', 40)
        interaction = self.interaction()
        await view.red.callback(interaction)
        self.assertIn('only have $10', interaction.edit_original_response.call_args.kwargs['embed'].description)
        self.assertEqual(self.bank.balance(1, 10), 10)

    async def test_failed_interaction_ack_does_not_spend(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        interaction = self.interaction()
        interaction.response.defer.side_effect = RuntimeError('connection lost')
        with self.assertRaises(RuntimeError):
            await view.red.callback(interaction)
        self.assertEqual(self.bank.balance(1, 10), 50)
        self.assertTrue(view.is_finished())

    async def test_failed_animation_still_shows_final_result(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        interaction = self.interaction()
        error = discord.HTTPException(SimpleNamespace(status=500, reason='test'), 'test')
        interaction.edit_original_response.side_effect = [error, None]
        with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=1), self.assertLogs(level='WARNING'):
            await view.red.callback(interaction)
        self.assertEqual(interaction.edit_original_response.await_count, 2)
        self.assertEqual(self.bank.balance(1, 10), 60)

    async def test_failed_final_message_does_not_repeat_payment(self):
        view = RouletteView(self.player, 1, 10, self.bank)
        interaction = self.interaction()
        error = discord.HTTPException(SimpleNamespace(status=500, reason='test'), 'test')
        interaction.edit_original_response.side_effect = [None, None, None, None, error]
        with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=1), patch('bot.cogs.games.asyncio.sleep', new_callable=AsyncMock):
            with self.assertRaises(discord.HTTPException):
                await view.red.callback(interaction)
        await view.red.callback(self.interaction())
        self.assertEqual(self.bank.balance(1, 10), 60)

    async def test_weekly_post_and_retry(self):
        self.bank.balance(1, 10, MONDAY)
        self.bank.set_channel(1, 999)
        channel = SimpleNamespace(guild=SimpleNamespace(id=1), send=AsyncMock(return_value=SimpleNamespace(id=123)))
        bot = SimpleNamespace(get_channel=Mock(return_value=channel))
        cog = Roulette(bot)
        cog.bank = self.bank
        with patch('bot.helpers.roulette_bank.current_week', return_value=current_week(NEXT_MONDAY)):
            error = discord.HTTPException(SimpleNamespace(status=500, reason='test'), 'test')
            channel.send.side_effect = error
            with self.assertLogs(level='ERROR'):
                await cog.weekly_results()
            self.assertEqual(len(self.bank.pending_announcements()), 1)
            channel.send.side_effect = None
            await cog.weekly_results()
            self.assertEqual(len(self.bank.pending_announcements()), 0)
            await cog.weekly_results()
        self.assertEqual(channel.send.await_count, 2)
        self.assertIn('Final roulette standings', channel.send.call_args.kwargs['embed'].title)

    async def test_leaderboard_ties_and_pagination(self):
        for user in range(35):
            self.bank.balance(1, user)
        cog = Roulette(SimpleNamespace())
        cog.bank = self.bank
        rows, lines = cog.standings(1, current_week())
        self.assertTrue(all(line.startswith('**1.**') for line in lines))
        ctx = SimpleNamespace(guild=SimpleNamespace(id=1), author=self.player, send=AsyncMock())
        await cog.rouletteleaderboard.callback(cog, ctx)
        view = ctx.send.call_args.kwargs['view']
        self.assertEqual(len(view.embeds), 3)
        self.assertEqual(sum(len(e.description.splitlines()) for e in view.embeds), 35)
        view.stop()

    async def test_whole_review_extension_loads_and_unloads(self):
        async with commands.Bot(command_prefix=';', intents=discord.Intents.none()) as bot:
            await bot.load_extension('bot.cogs.games')
            names = {command.name for command in bot.commands}
            self.assertTrue({'tictactoe', 'blackjack', 'roulette', 'roulettebalance', 'rouletteleaderboard', 'roulettechannel'} <= names)
            self.assertEqual(len(bot.tree.get_commands()), 6)
            cog = bot.get_cog('Roulette')
            cog.bank.balance(1, 10)
            with patch('bot.helpers.roulette_bank.secrets.randbelow', return_value=1):
                cog.bank.play(100, 1, 10, current_week(), 'red', 10)
            await bot.reload_extension('bot.cogs.games')
            self.assertEqual(bot.get_cog('Roulette').bank.balance(1, 10), 50)
            await bot.unload_extension('bot.cogs.games')
            self.assertIsNone(bot.get_cog('Roulette'))


    async def test_command_offers_four_buttons_without_spending(self):
        cog = Roulette(SimpleNamespace())
        cog.bank = self.bank
        ctx = SimpleNamespace(guild=SimpleNamespace(id=1), author=self.player, send=AsyncMock())
        with patch.object(RouletteView, 'wait', new_callable=AsyncMock):
            await cog.roulette.callback(cog, ctx, 10)
        view = ctx.send.call_args.kwargs['view']
        self.assertEqual([button.label.lower() for button in view.children], list(CHOICES))
        self.assertFalse(view.finished)
        self.assertEqual(self.bank.balance(1, 10), 50)
        view.stop()

    async def test_slash_command_only_asks_for_bet(self):
        async with commands.Bot(command_prefix=';', intents=discord.Intents.none()) as bot:
            command = Roulette.roulette.app_command
            bot.tree.add_command(command, guild=discord.Object(id=123))
            schema = bot.tree.get_command('roulette', guild=discord.Object(id=123)).to_dict(bot.tree)
            self.assertEqual([option['name'] for option in schema['options']], ['bet'])
            self.assertTrue(schema['options'][0]['required'])
            self.assertEqual(bot.tree.get_commands(), [])


if __name__ == '__main__':
    unittest.main()
