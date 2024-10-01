import os
from discord import Message
from discord.ext import commands
from openai import OpenAI
from bot.patron import Patron
from chat import Chat


class Tavern(commands.Cog, name="tavern"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

        self.client = OpenAI(
            base_url=f"{os.getenv('TAVERN_OPENAI_BASE')}/v1",
            api_key=os.getenv("TAVERN_OPENAI_API_KEY"),
        )

        self.patron = Patron("template", self.bot, self.client)

    # Listen to all messages
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        await self.patron.hear(message)


# And then we finally add the cog to the bot so that it can load, unload, reload and use it's content.
async def setup(bot) -> None:
    await bot.add_cog(Tavern(bot))
