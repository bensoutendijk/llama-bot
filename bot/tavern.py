import os

import requests
from discord import Message
from discord.ext import commands
from logger import logger
from openai import OpenAI
from patron import Patron


class Tavern(commands.Cog, name="tavern"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        logger.info("Initializing Tavern cog...")
        logger.info("Creating LLM client...")
        self.client = OpenAI(
            base_url=f"{os.getenv('TAVERN_OPENAI_BASE')}/v1",
            api_key=os.getenv("TAVERN_OPENAI_API_KEY"),
        )

        logger.info("Performing health check on LLM...")
        res = self.check_health()
        logger.info(f"Health check result: {res}")
        self.patron = Patron("template", self.bot, self.client)

    def check_health(self):
        try:
            logger.info(f"Connecting to url: {os.getenv('TAVERN_OPENAI_BASE')}/health")
            response = requests.get(f"{os.getenv('TAVERN_OPENAI_BASE')}/health")
            response.raise_for_status()  # Raises an error for bad status codes
            return response.status_code == 200
        except requests.RequestException as e:
            print(f"Error checking health: {e}")
            return False
    
    @commands.Cog.listener()
    async def on_message(self, message: Message) -> None:
        logger.info(f"Received message: {message.content}")
        await self.patron.hear(message)

async def setup(bot: commands.Bot) -> None:
    logger.info("Setting up Tavern cog...")
    await bot.add_cog(Tavern(bot))
    logger.info("Tavern cog setup complete.")
