from typing import List
import config
from interactions import Client, Channel, Guild, Message, ClientPresence, PresenceActivity, PresenceActivityType, Intents
from os import environ

i = Intents.DEFAULT | Intents.GUILD_MEMBERS

class ModMail(Client):
    def __init__(self, *args, **kwargs):
        super().__init__(
            token=environ["TOKEN"] if not hasattr(config, "token") else config.token, # basically, if config.token exists, use that, otherwise use the token in the environment
            presence=ClientPresence(activities=[
                PresenceActivity(type=PresenceActivityType.WATCHING, name="my dms for modmail!")
                ]),
            *args,
            **kwargs,
        )
        self.guild_id = config.guild_id
        self.color: int = config.color
        self.category_id = config.category_id
        self.partnering: List[int] = []
        self.is_ready = False

    async def on_ready(self):
        self.guild: Guild = Guild(**(await self._http.get_guild(self.guild_id)), client=self._http)
        self.category: Channel = Channel(**(await self._http.get_channel(self.category_id)), client=self._http)
        self.log: Channel = Channel(**(await self._http.get_channel(config.log_channel_id)), client=self._http)
        self.help_channel: Channel = Channel(**(await self._http.get_channel(config.help_channel)), client=self._http)
        cog = self.get_extension("Modmail")
        cog.load_variables()
        self.is_ready = True
        print("Bot ready!")

    async def on_message(self, message: Message):
        if message.channel_id == config.help_channel:
            content = message.content if len(message.content < 100) else message.content[:97] + "..."
            t = await self.help_channel.create_thread(content)
            m: Message = await t.send(content=message.author.mention)
            await m.delete()