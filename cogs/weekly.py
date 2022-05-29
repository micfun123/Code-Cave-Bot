import json
import random
from datetime import time, datetime

import discord
from discord.ext import commands, tasks
import aiosqlite


class ChallengeListView(discord.ui.View):
    def __init__(self, ctx, ems):
        super().__init__(timeout=69)
        self.ctx = ctx
        self.em = ems
        self.index = 0

    @discord.ui.button(style=discord.ButtonStyle.green, emoji="⬅", custom_id="left")
    async def left(self, button, interaction):
        if self.index == 0:
            button = [x for x in self.children if x.custom_id == "left"][0]
            button.disabled = True
        else:
            button = [x for x in self.children if x.custom_id == "right"][0]
            button.disabled = False
            self.index -= 1
        em = self.em[self.index]
        await interaction.response.edit_message(view=self, embed=em)

    @discord.ui.button(style=discord.ButtonStyle.green, emoji="➡️", custom_id="right")
    async def right(self, button, interaction):
        if self.index == (len(self.em) - 1):
            button = [x for x in self.children if x.custom_id == "right"][0]
            button.disabled = True
        else:
            button = [x for x in self.children if x.custom_id == "left"][0]
            button.disabled = False
            self.index += 1
        em = self.em[self.index]
        await interaction.response.edit_message(view=self, embed=em)


class SuggestionModal(discord.ui.Modal):
    def __init__(self, client, ctx, accept_channel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.return_suggestion = None
        self.client = client
        self.ctx = ctx
        self.accept_channel = accept_channel

        self.add_item(
            discord.ui.InputText(
                style=discord.InputTextStyle.long,
                label="Challenge Suggestion:",
                required=True,
                max_length=2000,
                min_length=10,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        suggestion = self.children[0].value

        if suggestion is None:
            return await interaction.response.send_message(
                "An error occured while suggesting"
            )

        channel = self.accept_channel

        em = discord.Embed(
            title="Challenge Suggestion",
            description=suggestion,
            color=self.ctx.author.color,
            timestamp=datetime.now(),
        )
        em.add_field(name="Suggestor Name:", value=self.ctx.author.name)

        channel = await self.client.fetch_channel(channel)

        if channel is None:
            return await interaction.response.send_message(
                "An error occured while suggesting"
            )

        message = await channel.send(embed=em)
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        await interaction.response.send_message("Thank you for your suggestion :)")


class WeeklyChallenge(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

        with open("config.json") as f:
            data = json.load(f)

        self.post_channel = data["weekly_challenge_post"]
        self.accept_channel = data["weekly_challenge_get"]

        self.challenge_loop.start()

    async def setup_db():
        async with aiosqlite.connect("main.db") as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS Challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    challenge TEXT, 
                    author TEXT, 
                    accepted INTEGER
                )"""
            )
            await db.commit()

    @tasks.loop(time=time(8, 0))
    async def challenge_loop(self):

        day_int = datetime.today().weekday()
        if day_int not in [1, 4]:
            return 

        async with aiosqlite.connect("main.db") as db:
            cur = await db.execute("SELECT * FROM Challenges WHERE accepted=1")
            data = await cur.fetchall()

            if len(data) == 0:
                print("No challenges at the moment")
                return

            challenge = random.choice(data)

            await db.execute(f"DELETE FROM Challenges WHERE id={challenge[0]}")
            await db.commit()

        channel = await self.client.fetch_channel(self.post_channel)

        em = discord.Embed(
            title="Challenge Time!",
            description=f"Today's Challenge is: \n\n{challenge[1]}",
            color=discord.Color.random(),
        )
        em.set_footer(text=f"Challenge suggested by {challenge[2]}")
        await channel.send(content="<@&980462921740087336>", embed=em)

    # @commands.slash_command(name="challenge-suggest", description="Suggest a challenge")
    # async def challenge_suggest(self, ctx, suggestion: str = None):
    #     """
    #     Suggest a challenge to be sent for approval
    #     """
    #     if suggestion is None:
    #         return ctx.respond("An error occured while suggesting")

    #     channel = self.accept_channel

    #     em = discord.Embed(
    #         title="Challenge Suggestion",
    #         description=suggestion,
    #         color=ctx.author.color,
    #         timestamp=datetime.now(),
    #     )
    #     em.add_field(name="Suggestor Name:", value=ctx.author.name)

    #     channel = await self.client.fetch_channel(channel)

    #     if channel is None:
    #         return ctx.respond("An error occured while suggesting")

    #     message = await channel.send(embed=em)
    #     await message.add_reaction("✅")
    #     await message.add_reaction("❌")

    #     await ctx.respond("Thank you for your suggestion :)")

    @commands.slash_command(name="challenge-suggest", description="Suggest a challenge")
    async def challenge_suggest_modal(self, ctx):
        """
        Suggest a challenge to be sent for approval
        """

        modal = SuggestionModal(
            self.client, ctx, self.accept_channel, title="Suggest a challenge:"
        )
        await ctx.send_modal(modal)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.user_id == self.client.user.id:
            return
        if payload.channel_id != self.accept_channel:
            return

        channel = await self.client.fetch_channel(self.accept_channel)
        message: discord.Message = await channel.fetch_message(payload.message_id)

        if message.author.id != self.client.user.id:
            return

        try:
            embed = message.embeds[0]
        except AttributeError:
            return

        if payload.emoji.name == "❌":
            return await message.delete()

        elif payload.emoji.name == "✅":

            async with aiosqlite.connect("main.db") as db:
                await db.execute(
                    """INSERT INTO Challenges 
                    (challenge, author, accepted) VALUES (?, ?, ?)""",
                    (
                        embed.description,
                        embed.fields[0].value,
                        1,
                    ),
                )
                await db.commit()

            content = f"Suggestion approved!\n\nContent: {embed.description}\nAuthor: {embed.fields[0].value}"
            await message.edit(embed=None, content=content)
            await message.clear_reactions()
        else:
            return

    @commands.slash_command(name="list-challenges", description="Lists the challenges")
    @commands.has_permissions(manage_guild=True)
    async def list_challenge_suggestions(self, ctx):
        async with aiosqlite.connect("main.db") as db:
            cur = await db.execute("SELECT * FROM Challenges WHERE accepted=1")
            data = await cur.fetchall()

            if len(data) == 0:
                return await ctx.respond("No challenges")

        embeds_list = []

        counter = 0
        em_counter = 0
        embeds_list.append(
            discord.Embed(title=f"Page {em_counter+1}", color=discord.Color.random())
        )
        for id, challenge, author, accepted in data:
            counter += 1
            if counter >= 10:
                counter = 0
                em_counter += 1

                embeds_list.append(
                    discord.Embed(
                        title=f"Page {em_counter+1}", color=discord.Color.random()
                    )
                )

            embeds_list[em_counter].add_field(
                name=f"ID: {id} - {author}:", value=challenge, inline=False
            )

        view = ChallengeListView(ctx, ems=embeds_list)

        await ctx.respond(view=view, content="List of approved challenge suggestions")

    @commands.slash_command(
        name="challenge-delete", description="Delete a challenge suggestion"
    )
    @commands.has_permissions(manage_guild=True)
    async def delete_challenge_command(self, ctx, id: int):

        async with aiosqlite.connect("main.db") as db:
            await db.execute(f"DELETE FROM Challenges WHERE id=?", (id,))
            await db.commit()

        await ctx.respond("Suggestion deleted!")


def setup(client):
    client.add_cog(WeeklyChallenge(client))
