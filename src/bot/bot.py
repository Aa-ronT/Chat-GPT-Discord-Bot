from src.bot.gpt_requests import send_prompt
from src.db.db_helpers import *
from dotenv import load_dotenv, find_dotenv
import os
import discord


class Bot(discord.Client):

    def __init__(self, api_key: str = None, token: str = None, rate_limit: int = 10, command_prefix: str = '!'):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        backup_auto()
        load_dotenv(find_dotenv())
        self.rate_limit = rate_limit
        self.rate_limit_storage = {}
        self.api_key = token or os.environ['API_KEY']
        self.token = api_key or os.environ['TOKEN']
        self.command_prefix = command_prefix

    def limit_user(self, user_id: str):
        def queue_user():
            self.rate_limit_storage[user_id] = True
            time.sleep(self.rate_limit)
            self.rate_limit_storage.pop(user_id)
        threading.Thread(target=queue_user).start()

    def run_bot(self):
        @self.event
        async def on_message(message):
            if message.author == self.user:
                return

            if message.content[0] == self.command_prefix:
                if message.content[1:4] == 'ask':
                    if message.author.id in self.rate_limit_storage:
                        await message.channel.send('** -CURRENTLY RATE-LIMITED- **')
                        return

                    if not user_exists(message.author.id):
                        user_create(message.author.id)

                    if usage_available(message.author.id):
                        self.limit_user(message.author.id)

                        tokens_used, string_response = send_prompt(self.api_key, system_message=get_system_message(str(message.author.id)), prompt_message=message.content[5:])

                        append_user_usage(str(message.author.id), tokens_used)
                        for substring in string_response:
                            await message.channel.send(substring)
                        return

                    else:
                        get_user_usage(message.author.id)
                        await message.channel.send(f'** -ERROR (Free Trial Ended)- **')
                        return

                if message.content[1:6] == 'usage':
                    if user_exists(message.author.id):
                        usage = get_user_usage(message.author.id)
                        await message.channel.send(
                            f"**You've currently used {usage['current_usage']} out of {usage['max_usage']} tokens**"
                        )

                    else:
                        await message.channel.send(
                            '** -Account not found. Create an account by using the /ask command- **'
                        )
                    return

                if message.content[1:7] == 'system':
                    system_message = message.content[8:]
                    if not user_exists(message.author.id):
                        user_create(message.author.id)

                    update_user_settings(str(message.author.id), system_message)
                    await message.channel.send('**Set System Message**')
                    return

                if message.content[1:5] == 'help':
                    await message.channel.send(
                        '__COMMANDS LIST__\n'
                        f'**{self.command_prefix}help** *Get a list of useful commands*\n'
                        f'**{self.command_prefix}usage** *Get the current token usage for your account*\n'
                        f'**{self.command_prefix}ask (Message)** *Ask Chat-GPT a question*\n'
                        f'**{self.command_prefix}system (Message)** *Set a system message to give the AI initial instructions*\n'
                        f'**{self.command_prefix}upgrade** *Upgrade your account to a premium user*\n'
                    )
                    return

                else:
                    await message.channel.send(' -**UNKNOWN COMMAND**- ')
                    return

        self.run(token=self.token)
