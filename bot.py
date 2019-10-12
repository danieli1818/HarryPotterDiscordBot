# bot.py
import datetime
import os

import discord
from discord import Game
from discord import Status

from dotenv import load_dotenv

from discord.ext import commands

from db import connect_database, db_add_data, db_update_data_player, db_get_data_player

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
bot_prefix = os.getenv('BOT_PREFIX')

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
db = os.getenv('DB_NAME')

db_player_table = os.getenv('DB_TABLE_PLAYERS')
db_player_table_player_id_field_name = os.getenv('DB_TABLE_PLAYERS_ID_FIELD_NAME')

db_magical_beasts_table = os.getenv('DB_TABLE_MAGICAL_BEASTS')
db_magical_beasts_table_player_id_field_name = os.getenv('DB_TABLE_MAGICAL_BEASTS_ID_FIELD_NAME')

db_buildings_table = os.getenv('DB_TABLE_BUILDINGS')
db_buildings_table_player_id_field_name = os.getenv('DB_TABLE_BUILDING_ID_FIELD_NAME')


class PotterCord:

    def __init__(self, bot_token):
        self.bot = commands.Bot(command_prefix=bot_prefix)
        self.token = bot_token
        self.prepare_client()
        self.db = None

    def run(self):
        self.bot.run(self.token)

    def prepare_client(self):

        @self.bot.event
        async def on_ready():
            await self.bot.change_presence(activity=Game(name="PotterCord"), status=Status.online)
            print(f'{self.bot.user.name} has connected to Discord!')

        @self.bot.command(name='start',
                          brief='The start command to start playing the game!',
                          help='The start command to start playing the game!')
        async def start(ctx):
            guild = ctx.guild
            # channel = ctx.channel
            author = ctx.author
            if self.does_player_exist(author):
                await ctx.send("{0.mention} You have already started!".format(author))
                return
            self.add_player(author)
            role = discord.utils.get(guild.roles, name="Wizard")
            if role is None:
                await guild.create_role(name="Wizard")
                role = discord.utils.get(guild.roles, name="Wizard")
            await author.add_roles(role)
            await ctx.send("{0.mention} welcome to the wizarding world!\n"
                           "You are a magizoologist working for the Ministry Of Magic!\n"
                           "Here is a magical suitcase it has room for 1 habitat!\n"
                           "Use it to collect magical beasts, take care of them, raise, tame and heal them\n"
                           "You can watch and research them and send the info to the Ministry Of Magic "
                           "for reward!\n"
                           "You can build habitats with hp!build command."
                           "For help and more commands type: hp!help".format(author))

        @self.bot.command(name='set_xp')
        @commands.has_role("Wizard")
        async def set_xp(ctx, xp):
            # guild = ctx.guild
            # channel = ctx.channel
            author = ctx.author
            # self.add_player(author)
            xp = int(xp)
            self.add_xp_to_player(xp, author)
            await ctx.send("{0.mention} xp points were set to {1}".format(author, xp))

        @self.bot.command(name='stats',
                          brief='The command to get your stats info',
                          help='The command to get your stats info')
        @commands.has_role("Wizard")
        async def get_stats(ctx):
            author = ctx.author
            await ctx.send(db_get_data_player(self.db, db_player_table, db_player_table_player_id_field_name
                                              , str(author.id), ["*"]))


        @self.bot.group(name='build',
                        brief='The command to build buildings in your suitcase',
                        help='The command to build buildings in your suitcase\n'
                             'buildings: habitats')
        @commands.has_role("Wizard")
        async def build(ctx):
            pass
            # await ctx.send("No Command Like That Exists!")
            # author = ctx.author
            # kind = kind.upper()
            # if kind == "HABITAT":
            #     self.build_habitat(author, args)

        @build.command(name='habitat')
        async def build_habitat(ctx, kind: str):
            pass

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.errors.CheckFailure):
                await ctx.send('You do not have the correct role for this command.')

    def update_data_player(self, table: str, player_id: str, fields_and_values: list):
        self.connect_db()
        db_update_data_player(self.db, table, player_id, fields_and_values)

    def add_xp_to_player(self, xp, player):
        if xp <= 0:
            return
        else:
            self.update_data_player(db_player_table, player.id, [("xp_points", xp)])

    def add_player(self, player):
        self.connect_db()
        db_add_data(self.db, db_player_table, ["id", "join_date", "xp_points", "money"], ["%s", "%s", "%s", "%s"]
                    , (player.id, str(datetime.date.today()), int(0), int(0)))

    def does_player_exist(self, player):
        return self.get_player_data(player) is not None

    def connect_db(self):
        if not self.is_db_connected():
            self.db = connect_database(host, user, password, db)
        # print("connected to database!")

    def close_db(self):
        if self.db is None or self.db.open():
            pass
        else:
            self.db.close()

    def is_db_connected(self):
        return self.db is not None and self.db.open

    def get_player_data(self, player):
        self.connect_db()
        return db_get_data_player(self.db, db_player_table, db_player_table_player_id_field_name, str(player.id)
                                  , ["*"])

    def add_money_to_player(self, player, amount: int):
        player_data = self.get_player_data(player)
        self.update_data_player(db_player_table, player.id, [("money", player_data["money"] + amount)])

    def get_player_buildings(self, player):
        self.connect_db()
        return db_get_data_player(self.db, db_buildings_table, db_buildings_table_player_id_field_name, str(player.id)
                                  , ["*"])

    def build_habitat(self, player, kind):
        pass


if __name__ == '__main__':
    bot = PotterCord(token)
    bot.run()
