import os

from discord import Message
from discord.ext import commands
from openai import OpenAI
from patron import Patron
from logger import logger


class Tavern(commands.Cog, name="tavern"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        logger.info("Initializing Tavern cog...")
        logger.info("Creating LLM client...")
        self.client = OpenAI(
            base_url=f"{os.getenv('TAVERN_OPENAI_BASE')}/v1",
            api_key=os.getenv("TAVERN_OPENAI_API_KEY"),
        )

        self.patron = Patron("template", self.bot, self.client)

    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        logger.info(f"Received message: {message.content}")
        await self.patron.hear(message)

async def setup(bot: commands.Bot) -> None:
    logger.info("Setting up Tavern cog...")
    await bot.add_cog(Tavern(bot))
    logger.info("Tavern cog setup complete.")
