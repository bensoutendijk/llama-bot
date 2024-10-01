import json
from typing import List, Dict, Any
from openai import OpenAI
import discord
import random
from discord.ext import commands

# Global constants for prompt components
SYSTEM_HEADER = "<|start_header_id|>system<|end_header_id|>"
USER_HEADER = "<|start_header_id|>user<|end_header_id|>"
ASSISTANT_HEADER = "<|start_header_id|>assistant<|end_header_id|>"
EOT_TOKEN = "<|eot_id|>"


class Patron:
    def __init__(self, patron_id: str, bot: commands.Bot, client: OpenAI):
        self.patron_id = patron_id
        self.bot = bot
        self.client = client
        self.json = None
        self.name = None
        self.description = None
        self.personality = None
        self.scenario = None
        self.shots = None

        # Load the patron
        with open(f"patrons/{patron_id}.json", "r") as file:
            self.json = json.load(file)["data"]
            self.name = self.json.get("name", "")
            self.description = self.json.get("description", "")
            self.personality = self.json.get("personality", "")
            self.scenario = self.json.get("scenario", "")
            self.shots = self.json.get("shots", [])
            self.vocab: List[str] = self.json.get("vocab", [])

    async def hear(self, message: discord.Message) -> None:
        """
        This function is called when the patron hears a message.
        """
        if message.author == self.bot.user:
            return

        if message.channel.name != "general" and message.channel.name != "bot-test":
            return

        if message.channel.name == "general" and not message.content.startswith(
            "Hey John"
        ):
            return

        await self.respond(message)

    async def respond(self, message: discord.Message) -> str:
        """
        This function is called when the patron responds.
        """

        system_message = await self._get_system_prompt(message)

        messages = [
            {"role": "system", "content": system_message},
        ]

        history = [message async for message in message.channel.history(limit=50)]
        history.pop()
        history.reverse()

        for msg in history:
            if msg.author == message.author:
                messages.append({"role": "user", "content": msg.content})
            if msg.author == self.bot.user:
                messages.append({"role": "assistant", "content": msg.content})

        messages.append({"role": "user", "content": message.content})
        completion = self.client.chat.completions.create(
            model=self.client.models.list().data[0].id,
            messages=messages,
            stop=EOT_TOKEN,
        )

        response = completion.choices[0].message.content
        await message.channel.send(response)

    async def _get_system_prompt(self, message: discord.Message) -> str:
        prompt_components: List[str] = []
        prompt_components.extend(self._instruction_component())
        prompt_components.extend(self._character_component())
        prompt_components.extend(self._scene_component())
        # prompt_components.extend(await self._history_component(message))

        prompt = "\n".join(prompt_components)

        debug(f"\nSystem Prompt: {prompt}", color="green")

        return prompt

    # async def _summarize_chat(self, history: list[discord.Message]) -> str:
    #     system_components: List[str] = []
    #     system_components.extend(
    #         [
    #             "You are a helpful assistant that can summarize a never ending conversation.",
    #             "Generate a response thatutputs a detailed paragraph summarizing the conversation so far.",
    #         ]
    #     )

    #     system_prompt = "\n".join(system_components)

    #     user_components: List[str] = []
    #     for msg in history:
    #         name = msg.author.name
    #         if msg.author == self.bot.user:
    #             name = "Assistant"

    #         user_components.append(f"{name}: {msg.content}")

    #     user_prompt = "\n".join(user_components)
    #     debug(f"\nSummary User Prompt: {user_prompt}", color="green")

    #     prompt = f"{SYSTEM_HEADER}{system_prompt}{EOT_TOKEN}"
    #     prompt += f"{USER_HEADER}{user_prompt}{EOT_TOKEN}"
    #     prompt += f"{ASSISTANT_HEADER}Summary:\n"

    #     completion = self.client.completions.create(
    #         model=self.client.models.list().data[0].id,
    #         prompt=prompt,
    #         stop=[EOT_TOKEN],
    #     )
    #     summary = completion.content

    #     debug(f"\nSummary: {summary}", color="yellow")

    #     return summary

    def _character_component(self) -> List[str]:
        return [
            f"Character name: {self.name}",
            f"Character description: {self.description}",
            f"Character personality: {self.personality}",
            f"Character vocabulary: {', '.join(self.vocab)}",
        ]

    def _scene_component(self) -> List[str]:
        scene = self.scenario
        return [f"Current scene: {scene}"]

    def _instruction_component(self) -> List[str]:
        return [
            "You are participating in a roleplaying session and follow these rules:",
            "- Only generate dialogue for the character you are playing"
            "- Avoid describing emotions or actions of the character",
            "- Match the character's traits and speech pattern",
        ]
