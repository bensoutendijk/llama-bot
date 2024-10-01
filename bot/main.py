import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True

PREFIX = "!"


class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            help_command=None,
        )
        self.tavern = None

    async def setup_hook(self) -> None:
        print("Setup...")
        self.tavern = self.load_extension("tavern")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)


load_dotenv(override=True)

bot = DiscordBot()
bot.run(os.getenv("TAVERN_BOT_TOKEN"), log_level=0)
