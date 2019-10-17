# bot.py
import datetime
import os
import random as rnd

import discord
from discord import Game
from discord import Status

from dotenv import load_dotenv

from discord.ext import commands

from db import connect_database, db_add_data, db_update_data_by_id, db_get_data_by_id
from magical_beasts_manager import get_random_magical_beast, get_magical_beast_by_kind

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

db_guilds_data_table = os.getenv('DB_TABLE_GUILDS_DATA')
db_guilds_data_table_guild_id_field_name = os.getenv('DB_TABLE_GUILDS_DATA_ID_FIELD_NAME')

habitats_kinds = os.getenv('HABITATS_KINDS').split(", ")
ministry_of_magic_habitat_id = int(os.getenv('MINISTRY_OF_MAGIC_HABITAT_ID'))


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
            await ctx.send(self.get_player_data(author))

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
        @commands.has_role("Wizard")
        async def build_habitat(ctx, kind: str):
            author = ctx.author
            if kind not in habitats_kinds:
                await ctx.send("{0.mention} habitat kind does not exist!".format(author))
            price = self.get_habitat_building_price(author, kind)
            # player_data = self.get_player_data(author)
            # money = player_data["money"]
            if not self.change_money(author, -price):
                await ctx.send("{0.mention} you don't have enough money to build that habitat!".format(author))
                return
            self.add_habitat_to_player(author, kind)
            await ctx.send("{0.mention} habitat {1} has been successfully built!".format(author, kind))

        @self.bot.command(name='tame',
                          brief='The command to tame a spawned magical beast!',
                          help='Type hp!tame [magical beast name] to tame the spawned magical beast!')
        @commands.has_role("Wizard")
        async def tame(ctx, name: str):
            guild = ctx.guild
            author = ctx.author
            guild_data = self.get_guild_data(guild)
            if guild_data is None or guild_data["current_magical_beast"] is None:
                return
            if guild_data["current_magical_beast"] == name:
                self.set_server_current_magical_beast(guild, None)
                self.add_magical_beast_to_player(author, get_magical_beast_by_kind(name))
                message = "a "
                if name[0] in "aeuoi":
                    message = "an "
                message += name
                await ctx.send("{0.mention} you tamed ".format(author) + message + "!")
            else:
                await ctx.send("{0.mention} wrong magical beast name!".format(author))

        @self.bot.command(name='set_spawn_channel',
                          brief='The command to set the spawn magical beasts channel!',
                          help='Type hp!set_spawn_channel [channel] to set the spawn magical beasts channel!')
        @commands.has_permissions(manage_channels=True)
        async def set_spawn_channel(ctx, current_channel: discord.TextChannel):
            guild = ctx.guild
            author = ctx.author
            if not self.does_guild_exist(guild):
                self.add_server(guild)
            # if channel_name is None:
            #     current_channel = ctx.channel
            #     channel_name = current_channel.name
            # elif channel_name.startswith("<#") and channel_name.endswith(">"):
            #     current_channel = self.bot.get_channel(channel_name)
            #     channel_name = current_channel.name
            # else:
            #     current_channel = None
            #     for channel in guild.text_channels:
            #         if channel.name == channel_name:
            #             current_channel = channel
            #             break
            #     if current_channel is None:
            #         await ctx.send("{0.mention} channel ".format(author) + channel_name + " does not exist!")
            #         return
            self.update_data_by_id(db_guilds_data_table, db_guilds_data_table_guild_id_field_name, guild.id
                                   , [("magical_beasts_spawn_channel_id", current_channel.id)])
            await ctx.send("{0.mention} channel {1.mention}".format(author, current_channel) +
                           " has been set successfully to be magical beast spawn channel")

        @self.bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.errors.CheckFailure):
                await ctx.send('You do not have the permissions for this command.')
            elif isinstance(error, commands.errors.BadArgument) \
                    or isinstance(error, commands.errors.ArgumentParsingError):
                await ctx.send('Not valid argument for the command for help use hp!help')
            else:
                await ctx.send('There has been an error: ' + str(error))

        @self.bot.event
        async def on_message(message):
            if not message.author.bot and not message.content.startswith("hp!"):
                await self.spawn_magical_beast(message.guild, message.channel)
            await self.bot.process_commands(message)

        @self.bot.event
        async def on_guild_join(guild):
            # current_channel = None
            # for text_channel in guild.text_channels:
            #     current_channel = text_channel
            #     break
            self.add_server(guild)

    def update_data_by_id(self, table: str, id_field_name: str, id_value: str, fields_and_values: list):
        self.connect_db()
        db_update_data_by_id(self.db, table, [(id_field_name, id_value)], fields_and_values)

    def add_xp_to_player(self, xp, player):
        if xp <= 0:
            return
        else:
            self.update_data_by_id(db_player_table, db_player_table_player_id_field_name, player.id,
                                   [("xp_points", xp)])

    def add_player(self, player):
        self.connect_db()
        db_add_data(self.db, db_player_table, ["id", "join_date", "xp_points", "money", "tamed_magical_beasts_number"
                    , "next_magical_beast_id"], ["%s", "%s", "%s", "%s", "%s", "%s"]
                    , (player.id, str(datetime.date.today()), int(0), int(0), int(0), int(0)))

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
        player_data = db_get_data_by_id(self.db, db_player_table, [(db_player_table_player_id_field_name, str(player.id))]
                                        , ["*"])
        if player_data is not None:
            player_data = player_data[0]
        return player_data

    # def add_money_to_player(self, player, amount: int):
    #     player_data = self.get_player_data(player)
    #     self.update_data_by_id(db_player_table, player.id, [("money", player_data["money"] + amount)])

    def get_player_buildings(self, player):
        self.connect_db()
        return db_get_data_by_id(self.db, db_buildings_table
                                 , [(db_buildings_table_player_id_field_name, str(player.id))]
                                 , ["*"])

    def get_habitat_building_price(self, player, kind: str):
        player_habitats = self.get_habitats_of_player(player)
        if player_habitats.__len__() == 0:
            return 0
        return 100

    def get_buildings_of_player(self, player):
        self.connect_db()
        player_buildings = db_get_data_by_id(self.db, db_buildings_table, [(db_buildings_table_player_id_field_name
                                                                            , player.id)], ["*"])
        if player_buildings is None:
            player_buildings = []
        return player_buildings

    def get_habitats_of_player(self, player):
        player_buildings = self.get_buildings_of_player(player)
        player_habitats = []
        for item in player_buildings:
            if item["kind"] == "habitat":
                player_habitats.append(item)
        return player_habitats

    async def spawn_magical_beast(self, guild, current_channel):
        guild_data = self.get_guild_data(guild)
        if guild_data is not None and guild_data["magical_beasts_spawn_channel_id"] is not None:
            current_channel_temp = await self.bot.fetch_channel(guild_data["magical_beasts_spawn_channel_id"])
            if current_channel_temp is not None:
                current_channel = current_channel_temp
        # elif guild_data is None:
        #     self.connect_db()
        #     db_add_data(self.db, db_guilds_data_table, ["guild_id", "magical_beasts_spawn_channel_id"], ["%s", "%s"],
        #                 (guild.id, current_channel.id))
        # else:
        #     self.connect_db()
        #     db_update_data_player(self.db, db_guilds_data_table, )
        magical_beast = get_random_magical_beast()
        self.set_server_current_magical_beast(guild, magical_beast)
        await current_channel.send("A magical beast has just spawned!\n"
                                   "Type hp!tame [name of the magical beast] to catch it!\n"
                                   "{0.picture_uri}".format(magical_beast))

    def get_guild_data(self, guild):
        self.connect_db()
        guild_data = db_get_data_by_id(self.db, db_guilds_data_table, [(db_guilds_data_table_guild_id_field_name
                                       , guild.id)], ["*"])
        if guild_data is not None:
            guild_data = guild_data[0]
        return guild_data

    def change_money(self, player, amount):
        player_data = self.get_player_data(player)
        money = player_data["money"] + amount
        if money < 0:
            return False
        self.update_data_by_id(db_player_table, db_player_table_player_id_field_name, player.id, [("money", money)])
        return True

    def add_habitat_to_player(self, player, habitat_kind):
        player_buildings_amount = self.get_buildings_of_player(player).__len__()
        self.connect_db()
        db_add_data(self.db, db_buildings_table, ["building_id", "kind", "owner", "sub_kind"], ["%s", "%s", "%s", "%s"]
                    , (player_buildings_amount, "habitat", player.id, habitat_kind))

    def set_server_current_magical_beast(self, guild, magical_beast):
        if magical_beast is None:
            self.update_data_by_id(db_guilds_data_table, db_guilds_data_table_guild_id_field_name, guild.id
                                   , [("current_magical_beast", "NULL")])
            return
        self.update_data_by_id(db_guilds_data_table, db_guilds_data_table_guild_id_field_name, guild.id
                               , [("current_magical_beast", "\"" + magical_beast.kind + "\"")])

    def get_magical_beasts_of_player(self, player):
        self.connect_db()
        magical_beasts = db_get_data_by_id(self.db, db_magical_beasts_table
                                           , [(db_magical_beasts_table_player_id_field_name,
                                               player.id)], ["*"])
        if magical_beasts is ():
            magical_beasts = []
        return magical_beasts

    def add_magical_beast_to_player(self, player, magical_beast):
        # magical_beasts_of_player = self.get_magical_beasts_of_player(player)
        player_data = self.get_player_data(player)
        if player_data is None:
            return
        self.connect_db()
        db_add_data(self.db, db_magical_beasts_table,
                    ["id", "name", "type", "gender", db_magical_beasts_table_player_id_field_name, "habitat_id"]
                    , ["%s", "%s", "%s", "%s", "%s", "%s"], (player_data["next_magical_beast_id"], magical_beast.kind
                                                             , magical_beast.kind, bool(rnd.randint(0, 1))
                                                             , player.id, ministry_of_magic_habitat_id))
        self.update_data_by_id(db_player_table, db_player_table_player_id_field_name, player.id
                               , [("tamed_magical_beasts_number", player_data["tamed_magical_beasts_number"] + 1)])
        self.update_data_by_id(db_player_table, db_player_table_player_id_field_name, player.id
                               , [("next_magical_beast_id", player_data["next_magical_beast_id"] + 1)])

    def add_server(self, guild):
        self.connect_db()
        db_add_data(self.db, db_guilds_data_table, [db_guilds_data_table_guild_id_field_name
                    , "magical_beasts_spawn_channel_id", "current_magical_beast"]
                    , ["%s", "%s", "%s"], (guild.id, None, None))

    def does_guild_exist(self, guild):
        if self.get_guild_data(guild) is None:
            return False
        return True


if __name__ == '__main__':
    bot = PotterCord(token)
    bot.run()
