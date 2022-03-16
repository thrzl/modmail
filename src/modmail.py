from interactions import Member, Embed, Message, User, Channel, EmbedAuthor, EmbedFooter, EmbedImageStruct, EmbedField
from .bot import ModMail
import asyncio
import datetime
from interactions import (
    CommandContext,
    Option,
    SelectMenu,
    SelectOption,
    ComponentContext,
)
from interactions import (
    Extension,
    extension_command,
    extension_component,
    extension_listener,
)

import config


class Modmail(Extension):
    def __init__(self, bot: ModMail):
        self.bot = bot
        if bot.is_ready:
            self.load_variables()

    def load_variables(self):
        self.bot = self.bot
        self.guild = self.bot.guild
        while not self.guild.members:
            self.guild = self.bot.get_guild(config.guild_id)
        self.category = self.bot.category
        self.color = self.bot.color
        self.log = self.bot.log

    @extension_command(
        name="anonymous",
        description="Send a message anonymously.",
        options=[
            Option(
                name="message",
                description="The message to send anonymously.",
                type=3,
                required=True,
            )
        ],
        scope=config.guild_id,
    )
    async def _anonreply(self, ctx: CommandContext, message: str):
        if config.support_role_id not in [r.id for r in ctx.author.roles]:
            return
        user = self.guild.get_member(int(ctx.channel.topic))
        embed = Embed(description=message, color=self.color)
        embed.footer = EmbedFooter(text="POP Staff Team", icon_url=self.guild.icon_url)
        try:
            await user.send(embeds=[embed])
            await ctx.send(embeds=[embed])
        except Exception as e:
            print(e.__class__.__name__)
            pass

    @extension_command(
        name="open",
        description="Open a new modmail thread.",
        options=[
            Option(
                name="user", description="The user to open the ticket to.", type=6, required=True
            )
        ],
        scope=config.guild_id,
    )
    async def _open(self, ctx: CommandContext, *, user: User):
        if config.support_role_id not in [r.id for r in ctx.author.roles]:
            embed = Embed(description="If you'd like to open a ticket, DM me!", color=self.color, author=EmbedAuthor(name=ctx.guild.name, icon_url=ctx.author.avatar_url))
        cat = self.category
        for i in cat.text_channels:
            if str(user.id) == i.topic:
                await ctx.send(
                    f"A ticket for that user is already open! Go to {i.mention}!"
                )
                return
        mc: Channel = await cat.create_text_channel(
            "thread-" + user.name, reason=f"Modmail channel opened by {ctx.author}"
        )
        await mc.edit(topic=user.id)
        embed = Embed(
            title=f"{ctx.author} opened a support ticket on {user}!",
            color=self.bot.color,
        )
        embed.fields.append(EmbedField(name="ID", value=user.id, inline=True))
        embed.fields.append(EmbedField(name="Created on: ", value=user.created_at.date(), inline=True))
        embed.fields.append(EmbedField(name="Joined on: ", value=user.joined_at.date(), inline=True))
        embed.fields.append(EmbedField(name="Highest Role", value=user.top_role.mention, inline=True))
        roleslist = [role for role in user.roles if role.name != "@everyone"]
        roles: str = (
            ", ".join(role.mention for role in roleslist) or "User has no roles..."
        )
        embed.fields.append(EmbedField(name="Roles", value=roles, inline=True))
        embed.thumbnail = EmbedImageStruct(url=user.avatar_url)
        embed.footer = EmbedFooter(
            icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author.name}"
        )
        menu = SelectMenu(
            placeholder="🔒 Close...",
            custom_id="modmailclose",
            options=[
                SelectOption(
                    label="Troll Modmail",
                    emoji="👺",
                    description="The user didn't need help, they trolling.",
                    value="Troll",
                ),
                SelectOption(
                    label="Modmail Complete",
                    description="The user has gotten the help they need.",
                    emoji="✔",
                    value="Ticket Complete",
                ),
                SelectOption(
                    label="Will Be Reopened",
                    emoji="🕰",
                    description="Will be reopened soon.",
                    value="Will Be Reopened",
                ),
            ],
        )

        await mc.send(embeds=[embed], components=menu)
        embed = Embed(description=f"Go to {mc.mention}!", color=self.bot.color, author=EmbedAuthor(name="Ticket Created Successfully!"))
        await ctx.send(embeds=[embed])

    @extension_command(
        name="close",
        description="Close a modmail thread.",
        options=[
            Option(
                name="dm_user",
                description="Message the user that the ticket is closed",
                type=5,
                required=True,
            ),
            Option(
                name="reason",
                description="The reason for closing the ticket",
                type=3,
                required=False,
            ),
        ],
        scope=config.guild_id,
    )
    async def _close(
        self, ctx: CommandContext, dm_user: bool, *, reason="None Provided"
    ):
        if config.support_role_id not in [r.id for r in ctx.author.roles]:
            return
        await ctx.defer()
        cat = self.category
        if ctx.channel in cat.text_channels:
            user = await self.bot.guild.fetch_member(int(ctx.channel.topic))
            for ch in cat.channels:
                if str(ch.topic) == str(user.id):
                    ts = self.log
                    embed = Embed(
                        title=f"Ticket for {user} has been closed by {ctx.author}.",
                        description=f"Reason closed: `{reason}`",
                        color=self.bot.color,
                    )
                    embed.author = EmbedAuthor(
                        name=ctx.author.name, icon_url=ctx.author.avatar_url
                    )
                    await ts.send(embeds=[embed])
                    embed = Embed(
                        description="This channel will be deleted in 10 seconds!",
                        color=self.bot.color,
                    )
                    embed.author = EmbedAuthor(
                        name="POP Modmail", icon_url=ctx.bot.user.avatar_url
                    )
                    await ctx.reply(embeds=[embed])
                    if dm_user:
                        clem = Embed(
                            description=f"Your ticket has been closed. To get more support, you can DM the bot again",
                            color=self.bot.color,
                        )
                        clem.author = EmbedAuthor(
                            name="Ticket Closed", icon_url=ctx.bot.user.avatar_url
                        )
                        await user.send(embed=clem)
                    await asyncio.sleep(10)
                    await ch.delete(reason=f"Modmail thread closed by {ctx.author}.")
        else:
            await ctx.send("That user doesn't have a ticket opened yet!")

    @extension_listener
    async def on_member_remove(self, member: Member):
        cat = self.category
        for channel in cat.channels:
            if str(member.id) == channel.topic:
                ts = self.log
                embed = Embed(
                    title=f"{member}'s ticket has been closed successfully.",
                    description=f"Reason closed: `Member Left`",
                    color=self.bot.color,
                )
                embed.author = EmbedAuthor(name=member.name, icon_url=member.avatar_url)
                await ts.send(embeds=[embed])
                await channel.delete(
                    reason=f"Modmail Thread Recipient ({member}) left the guild."
                )

    def getchannel(self, channels, id):
        ch = [i for i in channels if i.topic == str(id)]
        if len(ch) == 1:
            return ch[0]
        if not ch:
            return None
        return ch[0]

    @extension_listener
    async def on_error(self, error):
        self.load_variables()

    @extension_listener
    async def on_message(self, message: Message):
        if (message.author.bot) or (message.author.id in self.bot.partnering):
            return
        g = self.guild
        ml = [str(m.id) for m in g.members]
        if str(message.channel.type) == "private":
            cat = self.category
            channels = [c for c in g.text_channels]
            ca = self.getchannel(channels, message.author.id)
            if not ca:
                log = self.log
                embed = Embed(
                    title=f"New ticket opened by {message.author}", color=self.color
                )
                embed.timestamp = datetime.datetime.now()
                await log.send(embeds=[embed])
                cat = self.category
                mc = await cat.create_text_channel("thread-" + message.author.name)
                await mc.edit(topic=message.author.id)
                newticketem = Embed(
                    title="Thanks for making a new ticket!",
                    description="A message has been sent to the support team and a staff member will get to you shortly!\nPlease state your issue in as much detail as possible, so that the staff may help you with speed and accuracy.",
                    color=self.color,
                )
                newticketem.set_thumbnail(url=self.guild.icon_url)
                await message.channel.send(embed=newticketem)
                user = g.get_member(message.author.id)
                ping = await mc.send(f"<@&{config.support_role_id}>")
                await ping.delete()
                embed = Embed(
                    title=f"{message.author} opened a support ticket!",
                    color=self.bot.color,
                )
                embed.fields.append(EmbedField(name="ID", value=user.id, inline=True))
                embed.fields.append(EmbedField(
                    name="Created on: ", value=user.created_at.date(), inline=True
                ))
                embed.fields.append(EmbedField(
                    name="Joined on: ", value=user.joined_at.date(), inline=True
                ))
                embed.fields.append(EmbedField(
                    name="Highest Role", value=user.top_role.mention, inline=True
                ))
                roles = ", ".join(
                    [role for role in user.roles if role.name != "@everyone"]
                )

                embed.fields.append(EmbedField(name="Roles", value=roles, inline=True))
                embed.thumbnail = EmbedImageStruct(url=user.avatar_url)
                embed.footer = EmbedFooter(icon_url=message.author.avatar_url, text="User Info")
                menu = SelectMenu(
                    placeholder="🔒 Close...",
                    custom_id="modmailclose",
                    options=[
                        SelectOption(
                            label="Troll Modmail",
                            emoji="👺",
                            description="The user didn't need help, they trolling.",
                            value="Troll",
                        ),
                        SelectOption(
                            label="Modmail Complete",
                            description="The user has gotten the help they need.",
                            emoji="✔",
                            value="Ticket Complete",
                        ),
                        SelectOption(
                            label="Will Be Reopened",
                            emoji="🕰",
                            description="Will be reopened soon.",
                            value="Will Be Reopened",
                        ),
                    ],
                )
                await mc.send(embeds=[embed], components=[menu])
                ca = mc
            modmail_channel = ca
            if not modmail_channel:
                modmail_channel = self.getchannel(channels, message.author.id)
            user = g.get_member(message.author.id)
            embed = Embed(
                description=f"{message.content}",
                color=self.color,
            )
            embed.author = EmbedAuthor(name=user, icon_url=user.avatar_url)
            if message.attachments:
                files = message.attachments
                embed.image = EmbedImageStruct(url=message.attachments[0].url)
            try:
                await modmail_channel.send(embeds=[embed])
            except Exception:
                await message.add_reaction("❌")
                await message.channel.send("The message could not be delivered.")
            return
        if message.channel.topic in ml:
            user = g.get_member(int(message.channel.topic))
            if message.content.startswith("//") or message.content.startswith("s."):
                return

            member_object = g.get_member(int(message.channel.topic))
            mod_message = message.content
            embed = Embed(description=mod_message, color=self.color)
            embed.author = EmbedAuthor(
                name=str(message.author), icon_url=message.author.avatar_url
            )
            embed.footer = EmbedFooter(text="Staff Team", icon_url=self.guild.icon_url)
            if message.attachments:
                files = message.attachments
                embed.image = EmbedImageStruct(url=files[0].url)
            try:
                await member_object.send(embeds=[embed])
                await message.delete()
                await message.channel.send(embeds=[embed])
            except Exception:
                await message.add_reaction("❌")

    @extension_component("modmailclose")
    async def close_thread(self, ctx: ComponentContext):
        await self._close.invoke(ctx, dm_user=True, reason=ctx.selected_options[0])

    #! likely won't work, yet to be tried
    # @extension_listener
    # async def on_typing(self, channel, user, when):
    #     if user.id in self.bot.partnering:
    #         return
    #     if channel.type == ChannelType.:
    #         for i in self.category.text_channels:
    #             try:
    #                 if int(i.topic) == user.id:
    #                     channel = i
    #                     break
    #             except ValueError:
    #                 continue
    #             except TypeError:
    #                 continue
    #         if not channel:
    #             return
    #         await channel.trigger_typing()
    #     elif channel.type == ChannelType.text:
    #         if channel in self.category.text_channels:
    #             try:
    #                 member = self.guild.get_member(int(channel.topic))
    #                 await member.trigger_typing()
    #             except:
    #                 return


def setup(bot):
    Modmail(bot)
