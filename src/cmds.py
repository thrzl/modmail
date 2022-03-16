import random

import humanize
from aiohttp import ClientSession
from interactions import (
    CommandContext,
    Embed,
    EmbedAuthor,
    EmbedImageStruct,
    Extension,
    Option,
    extension_message_command,
    EmbedField,
    EmbedFooter,
    extension_listener,
    Member,
    Message,
    extension_command
)

import config
from .bot import ModMail

http = ClientSession()


class Commands(Extension):
    def __init__(self, bot: ModMail):
        self.bot = bot

    @extension_command(name="topic", description="Icebreakers!", scope=config.guild_id)
    async def topic(self, ctx):
        topics = [
            "When was the last time you stayed up through the entire night?",
            "What shouldn't have happened but happened anyway?",
            "How could carousels be spiced up so they are more exciting?",
            "Are you good at keeping secrets?",
            "What's the craziest thing one of your teachers' has done?",
            "What do you wish was illegal?",
            "What is your favorite video game console?",
            "Have you ever tried archery?",
            "What is the last “good” thing you ate?",
        ]
        embed = Embed(
            title="Topic", description=random.choice(topics), color=config.color
        )
        await ctx.send(embed=embed)

    @extension_command(
        name="letmegooglethat",
        description="For when someone can't just google it themselves",
        options=[
            Option(
                name="query",
                description="What they should have Googled.",
                type=3,
                required=True,
            )
        ],
        scope=config.guild_id,
    )
    async def lmgtfy(self, ctx: CommandContext, query: str):
        embed = Embed(
            description=f"https://letmegooglethat.com/?q={query.replace(' ', '+')}\n\nNext time, make sure to check Google before coming here!",
            color=config.color,
        )
        embed.thumbnail = EmbedImageStruct(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/2048px-Google_%22G%22_Logo.svg.png"
        )
        return await ctx.send(embeds=[embed])

    @extension_message_command(name="Let Me Google That", scope=config.guild_id)
    async def lmgtfy_comp(self, ctx):
        embed = Embed(
            description=f"https://letmegooglethat.com/?q={ctx.target_message.content.replace(' ', '+')}\n\nNext time, make sure to check Google before coming here!",
            color=config.color,
        )
        embed.thumbnail = EmbedImageStruct(
            url="https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Google_%22G%22_Logo.svg/2048px-Google_%22G%22_Logo.svg.png"
        )
        await ctx.target_message.reply(embeds=[embed])
        return await ctx.send("Done!", hidden=True, delete_after=3)

    @extension_message_command(
        name="Try It And See", scope=config.guild_id
    )
    async def tias(self, ctx):
        await ctx.target_message.reply("https://tryitands.ee")
        return await ctx.send("Success!", delete_after=2)

    @extension_listener()
    async def on_member_join(self, member: Member):
        if member.bot:
            return
        embed = Embed(
            description=f"""
      ```py
await ctx.send(f"Thanks for joining {member}!")```
      ↳ [`README.md`](https://discord.com/channels/876506256356048926/876506555997110324/907150424614789150)
      ↳ [`Releases`](https://discord.com/channels/876506256356048926/877761074907209748)
      ↳ [`Discussions`](https://discord.com/channels/876506256356048926/906962125661032479)

      ```js
console.log("Again, thanks for joining! Don't be afraid to ask any questions!")```
      And feel free to DM me ({self.bot.user.mention}) if you need anything.
      """,
            color=config.color,
        )
        embed.author = EmbedAuthor(
            name=f"Welcome to {member.guild.name}!", icon_url=member.avatar_url
        )
        role = "<@&914642374515388436>"
        c = await self.bot.fetch_channel(906962125661032479)
        await c.send(f"{role} | {member.mention} has joined!", embeds=[embed])

    @extension_listener()
    async def on_message(self, message: Message):
        if "pypi.org" in message.content:
            text = message.content
            if message.content[-1] == "/":
                text = message.content[:-1]
            project = text.split("/")[-1]
            r = await http.get(f"https://pypi.org/pypi/{project}/json")
            data = await r.json()
            d = await http.get(f"https://pypistats.org/api/packages/{project}/overall")
            dn = await d.json()
            embed = Embed(
                title=f"{data['info']['name']} {data['info']['version']}",
                url=data["info"]["project_url"],
                description=data["info"]["summary"],
                author=EmbedAuthor(name=data["info"]["author"]),
                footer=EmbedFooter(text=f"PyPi Package Index"),
                fields=[
                    EmbedField(
                        name="Requirements",
                        value="`" + "`\n`".join(data["info"]["requires_dist"]) + "`",
                    ),
                    EmbedField(
                        name="Python Version",
                        value=f"`{data['info']['requires_python']}`",
                    ),
                    EmbedField(
                        name="Total Downloads",
                        value=humanize.intword(
                            sum([i["downloads"] for i in dn["data"]])
                        ),
                    ),
                    EmbedField(
                        name="Install",
                        value=f"```sh\npip install {project}\n```",
                        inline=False,
                    ),
                ],
            )
            await message.reply(embeds=[embed])


def setup(bot):
    Commands(bot)
