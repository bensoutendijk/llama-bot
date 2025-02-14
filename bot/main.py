import os

import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.message_content = True

PREFIX = "!"

class DiscordBot(commands.Bot):
    def __init__(self) -> None:
        print("Initializing bot...")
        super().__init__(
            command_prefix=commands.when_mentioned_or(PREFIX),
            intents=intents,
            help_command=None,
        )
        self.tavern = None

    async def setup_hook(self) -> None:
        print("Loading extension...")
        self.tavern = self.load_extension("tavern")

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user or message.author.bot:
            return
        await self.process_commands(message)

bot = DiscordBot()
bot.run(os.getenv("TAVERN_BOT_TOKEN"))
