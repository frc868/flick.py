# Flick

<img src="icon.png" alt="Flick Icon" align="right" width="256px">

The bot for the TechHOUNDS Discord server, named after our 2013 robot, [Flick](https://youtu.be/8Ls_uvX_NXE)!

Icon made by the wonderful [Bryce Castle](https://bcastle.net)!

## Commands
TODO

### Roulette

Run `;roulette 10` (or `/roulette bet:10`) and click **Red**, **Black**,
**Even**, or **Odd**. A win returns twice the stake, including the original
bet. Green 0 loses on all four choices. Bets must be positive whole numbers of frisbees within the player's balance. An unused menu expires without charging.

Everyone starts with **50 frisbees in the server's first week of roulette in this bot session**. At
**Sunday 12:00 a.m. America/New_York** (the start of Sunday), the new week starts
with **100 frisbees per player**. Winnings do not carry over. New players joining in a
later week also start with 100 frisbees while the bot stays running. For the week beginning
October 18, 2026, the next cutoff is October 25, 2026 at 12:00 a.m. Eastern.

- `;roulettebalance`: check your current balance.
- `;rouletteleaderboard`: current standings, ordered by balance.
- `;rouletteleaderboard true`: most recent completed week with players.
- `;roulettechannel`: choose the current channel for automatic weekly standings
  (requires Manage Server).

These commands also support slash commands. Load the updated games extension
and run the existing admin `;sync` command to register them.

Standings include players who opened roulette or checked their balance that
week. Tied balances share a rank. Past weeks are kept during the bot session. The weekly post
shows the top 15 and attaches a CSV with all registered players' final balances.
The bot needs View Channel, Send Messages, Embed Links, and Attach Files in the
chosen channel. Configure that channel once with `;roulettechannel`.

Balances, spin results, channels, and weekly standings are held in Python lists
in memory. There is no database or save file. Restarting the bot or reloading
the games extension clears all of these lists. Players then start at 50 frisbees again,
and an admin must run `;roulettechannel` again. Previously posted Discord
standings messages remain, but the bot cannot recover lost records or post
missed standings from before the restart.

While the bot stays running, it checks for completed weeks every minute.
Balances switch to the new week's allowance on the next interaction, even
before the standings post. Failed sends are retried. Use one bot process:
separate processes have separate lists.
