from datetime import datetime, timedelta
import discord
import random
import asyncio
import sys
import os
from discord.ext import commands, tasks
from typing import Literal
import json
import logging
import requests

import sqlite_database as db
from pois import SP_POIs, WE_POIs, KC_POIs, OL_POIs, ED_POIs, SP_POIs_SHORT, WE_POIs_SHORT, ED_POIs_SHORT
from player import Player
from team import Team
import utils
import teams_management
import ws_r5

# Initialize the bot
intents = discord.Intents.all()
client = commands.Bot(command_prefix="$", intents=intents)

logging.basicConfig(level=logging.INFO, format="\033[1m\033[90m%(asctime)s \033[94mLOGGING \033[90m [%(levelname)s] \033[0m %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
# logging.debug('This is a debug message')
# logging.info('This is an info message')
# logging.warning('This is a warning message')
# logging.error('This is an error message')
# logging.critical('This is a critical message')

DATABASE: db.Database
EMBED_COLOR = 0x8D00C5
VARIABLES = json.loads(open("variables.json", encoding="ISO-8859-1").read())

CURRENT_GUILD = discord.Object(id=VARIABLES["EternalServerID"])
DEV_GUILD = discord.Object(id=VARIABLES["DevServerID"])

LOBBY_COUNT = int(open("LobbyCount", encoding="ISO-8859-1").read())

QUEUE_VC: discord.VoiceChannel = None
WAITING_ROOM_VC: discord.VoiceChannel = None
ASYNC_WAITING_TIME: float = 0.1

LAST_UPDATE: datetime = datetime.now()
IS_CREATING_QUEUE: bool = False
CURRENT_HOST = ""
BALANCER = ""
OVERSTAT_API_KEY = ""

TEAMS: int = 20

@client.event
async def on_ready():

    global LAST_UPDATE, IS_CREATING_QUEUE

    try:
        # Add Cogs (Groups of Commands)
        #await client.add_cog(BRCog(client))
        await client.add_cog(SoloQCog(client))
    except discord.ClientException as exc:
        logging.error(f"Failed to load Cogs: {exc}")

    # Sync Commands with Eternal EC
    client.tree.copy_global_to(guild=CURRENT_GUILD)
    await client.tree.sync(guild=CURRENT_GUILD)

    # Sync Commands with Raz's Dev Server
    client.tree.copy_global_to(guild=DEV_GUILD)
    await client.tree.sync(guild=DEV_GUILD)

    # Create DB file if not exists
    open("eternal.db", "a+").close()

    # Create connection
    global DATABASE
    db.create_tables(db.create_connection("eternal.db"))
    DATABASE = db.Database(
        db.Player(db.create_connection("eternal.db")),
        db.LowPrio(db.create_connection("eternal.db"))
    )

    # Download VizBot MMR
    logging.debug("Downloading MMR...")
    for player in await utils.download_mmr():
        if not await DATABASE.players.create(player[0], player[1]):
            logging.error(f"Failed to Update {player[0]}'s MMR")
    logging.info("Updated MMR")

    # Log when Bot is Ready
    utils.notify_success(f'We have logged in as {client.user}')
    return

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    global LAST_UPDATE, LOBBY_COUNT, IS_CREATING_QUEUE

    # Check if more than 5 seconds have passed since the last update
    current_time = datetime.now()
    if ((current_time - LAST_UPDATE) > timedelta(seconds=5)) and (not IS_CREATING_QUEUE):

        # Update last update
        LAST_UPDATE = current_time

        # Check VC state
        guild = client.get_guild(CURRENT_GUILD.id)

        if (after.channel is not None) and (QUEUE_VC is not None) and (after.channel.guild.id == CURRENT_GUILD.id) and (after.channel.id == QUEUE_VC.id):
            if (len(after.channel.members) == TEAMS * 3) and (not IS_CREATING_QUEUE):

                # Lock QUEUE_VC
                everyone_role = guild.default_role
                await QUEUE_VC.set_permissions(everyone_role, connect=False)

                # Get VC members list
                members_list = QUEUE_VC.members

                # Notify Lobby Starting
                logging.info(f"Lobby {LOBBY_COUNT} Starting")
                await guild.get_channel(VARIABLES["SoloQCommandsID"]).send(embed=discord.Embed(title=f"Creating Lobby {LOBBY_COUNT}. Starting in ~2 minutes!", color=EMBED_COLOR))
                await guild.get_channel(VARIABLES["SoloQGeneralID"]).send(embed=discord.Embed(title=f"Creating Lobby {LOBBY_COUNT}. Starting in ~2 minutes!", color=EMBED_COLOR))

                # Prevent Lobby Duplication
                IS_CREATING_QUEUE = True

                # Assign Dropspots
                logging.debug("Assigning Dropspots...")
                drops: list[str] = []
                short_drops: list[str] = []
                title: str = ""
                if LOBBY_COUNT % 4 <= 1:
                    drops = SP_POIs.copy()
                    random.shuffle(drops)
                    short_drops = [SP_POIs_SHORT[poi] for poi in drops]
                    title = "Storm Point"
                # elif LOBBY_COUNT % 3 == 1:
                #     drops = WE_POIs.copy()
                #     random.shuffle(drops)
                #     short_drops = [WE_POIs_SHORT[poi] for poi in drops]
                #     title = "World's Edge"
                elif LOBBY_COUNT % 4 >= 2:
                    drops = ED_POIs.copy()
                    random.shuffle(drops)
                    short_drops = [ED_POIs_SHORT[poi] for poi in drops]
                    title = "E-District"
                logging.debug("Dropspots Assigned")
                
                # Get Players List
                players: list[Player] = []
                for member in members_list:
                    # Attempt to Read Player's MMR
                    res = await DATABASE.players.read(member.id)
                    if res is not None:
                        # Save Player
                        player = Player(member, res[0])
                    else:
                        # Assign Role if Not Paired
                        await member.add_roles(after.channel.guild.get_role(VARIABLES["NotPairedRoleID"]), atomic=True)
                        logging.info(f"Gave {member.name} NotPaired role.")
                        player = Player(member, 800)
                    players.append(player)

                # Create Roles
                lobby_role = await guild.create_role(name=f"SoloQLobby {LOBBY_COUNT}", mentionable=True)
                
                # Create Category and set Permissions
                lobby_category = await guild.create_category(name=f"Lobby {LOBBY_COUNT}")
                await lobby_category.set_permissions(lobby_role, view_channel=True, connect=True, speak=True, read_message_history=True, read_messages=True)
                await lobby_category.set_permissions(everyone_role, view_channel=True, connect=False, speak=True, read_message_history=False, read_messages=False)
                
                try:
                    # Setup SoloQ Host Role
                    soloqhost_role = guild.get_role(VARIABLES["SoloQHostRoleID"])
                    await lobby_category.set_permissions(soloqhost_role, view_channel=True, connect=True, speak=True, read_message_history=True, read_messages=True)
                except Exception as exc:
                    logging.error(f"Failed to Setup SoloQ Host Role: {str(exc)}")

                # Create Text Channel
                lobby_channel = await guild.create_text_channel(name=f"soloqlobby-{LOBBY_COUNT}", category=lobby_category)

                # Info people
                allowed_mentions = discord.AllowedMentions(roles = True)
                await lobby_channel.send(f"## Creating Lobby, should take a minute or two...")
                try:
                    await lobby_channel.send(f"## {soloqhost_role.mention} - Use Lobby Code {(LOBBY_COUNT % len(VARIABLES['LobbyCodes'])) + 1} for this Lobby | `{title}`", allowed_mentions=allowed_mentions)
                except Exception as exc:
                    logging.warning(f"Failed to Send Lobby Code: {str(exc)}")
                    await lobby_channel.send(f"## Use Lobby Code {(LOBBY_COUNT % len(VARIABLES['LobbyCodes'])) + 1} for this Lobby | `{title}`", allowed_mentions=allowed_mentions)

                # Send Dropdown to Setup Lobby
                try:
                    await guild.get_channel(VARIABLES["SoloQCommandsID"]).send(embed=discord.Embed(title=f"Setup In-Game Lobby within the next 2 minutes; Select an Apex Client below. (MAKE SURE GAME IS OPEN, NOT IN CUSTOM GAME)!", color=EMBED_COLOR), view=SoloQCog.ApexClientsView(LOBBY_COUNT, short_drops))
                except Exception as exc:
                    aux = '\n'.join(short_drops)
                    await guild.get_channel(VARIABLES["SoloQCommandsID"]).send(f"`{aux}`")
                    logging.error(f"Failed to Send Dropdown Message: {str(exc)}")

                # Give roles
                logging.info("Giving Roles...")
                for player in players:
                    await player.discord_user.add_roles(lobby_role, atomic=True)
                    await asyncio.sleep(ASYNC_WAITING_TIME)
                logging.info("Roles Given")

                # Download VizBot MMR
                try:
                    logging.debug("Downloading MMR...")
                    for player in await utils.download_mmr():
                        if not await DATABASE.players.create(player[0], player[1]):
                            logging.error(f"Failed to Update {player[0]}'s MMR")
                    logging.info("Updated MMR")
                except Exception as exc:
                    logging.error(f"Error while trying to update MMR: {str(exc)}")

                # Make Teams
                logging.debug("Making Teams...")
                if BALANCER == "Average MMR":
                    teams, _ = teams_management.balancedTeams(players)
                elif BALANCER == "Fully Random":
                    teams, _ = teams_management.unbalancedTeams(players, TEAMS)
                random.shuffle(teams)
                logging.debug("Teams Made")

                # Create Channels & Move Players
                logging.debug("Creating Channels & Moving Players...")
                e = discord.Embed(title=f"Lobby {LOBBY_COUNT} | {title}", color=EMBED_COLOR)
                for i in range(TEAMS):

                    # Create VC
                    team_vc = await guild.create_voice_channel(name=f"T{i + 1} - {teams[i].dropspot}", category=lobby_category, user_limit=3)
                    await asyncio.sleep(ASYNC_WAITING_TIME)

                    # Assign Player 1
                    try:
                        if teams[i].P1 is not None:
                            await teams[i].P1.discord_user.move_to(team_vc)
                        else:
                            logging.error(f"Player 1 is None for Team {i + 1} in Lobby {LOBBY_COUNT}")
                        await asyncio.sleep(ASYNC_WAITING_TIME)
                    except Exception as exc1:
                        logging.warning(str(exc1))
                        await guild.get_channel(VARIABLES["SoloQDodgersID"]).send(embed=discord.Embed(title=f"Error trying to move user {teams[i].P1.discord_user.name} to {team_vc.name}.", color=EMBED_COLOR))

                    # Assign Player 2
                    try:
                        if teams[i].P2 is not None:
                            await teams[i].P2.discord_user.move_to(team_vc)
                        else:
                            logging.error(f"Player 2 is None for Team {i + 1} in Lobby {LOBBY_COUNT}")
                        await asyncio.sleep(ASYNC_WAITING_TIME)
                    except Exception as exc2:
                        logging.warning(str(exc2))
                        await guild.get_channel(VARIABLES["SoloQDodgersID"]).send(embed=discord.Embed(title=f"Error trying to move user {teams[i].P2.discord_user.name} to {team_vc.name}.", color=EMBED_COLOR))

                    # Assign Player 3
                    try:
                        if teams[i].P3 is not None:
                            await teams[i].P3.discord_user.move_to(team_vc)
                        else:
                            logging.error(f"Player 3 is None for Team {i + 1} in Lobby {LOBBY_COUNT}")
                        await asyncio.sleep(ASYNC_WAITING_TIME)
                    except Exception as exc3:
                        logging.warning(str(exc3))
                        await guild.get_channel(VARIABLES["SoloQDodgersID"]).send(embed=discord.Embed(title=f"Error trying to move user {teams[i].P3.discord_user.name} to {team_vc.name}.", color=EMBED_COLOR))

                    # Add Players to Message
                    e.add_field(name=f"T{i + 1} - {teams[i].dropspot}", value=f"{teams[i]}")

                    # Add Dropspots
                    teams[i].dropspot = f"T{i + 1} - {teams[i].dropspot}"
                
                # Publish Teams
                allowed_mentions = discord.AllowedMentions(roles = True)
                await lobby_channel.send(embed=e)
                await lobby_channel.send(f"# {lobby_role.mention} - Lobby Code: {VARIABLES['LobbyCodes'][LOBBY_COUNT % len(VARIABLES['LobbyCodes'])]}", allowed_mentions=allowed_mentions)
                logging.debug("Channels Created")

                await lobby_channel.send("### If you can access this channel, make sure you bind your accounts after your first game in <#1192705204169232384> !!!")

                # Save Dropspots
                # session = requests.Session()
                # for i in range(TEAMS):
                #     utils.overstat_drops(session, i, teams[i].dropspot, match_id, title, "eec")
                # session.close()

                # Unlock QUEUE_VC
                await QUEUE_VC.set_permissions(everyone_role, connect=True)
                #await QUEUE_VC.edit(name="Queue")
                IS_CREATING_QUEUE = False
                logging.info("Queue Unlocked")

                # Save Lobby Data
                # try:
                #     with open(f"LobbyData/Lobby-{LOBBY_COUNT}-{datetime.now().strftime('%Y-%m-%d-%H')}.csv", "w") as f:
                #         for team in teams:
                #             f.write(f"{team.dropspot};{team.P1.discord_user.id};{team.P2.discord_user.id};{team.P3.discord_user.id}\n")
                # except Exception as exc:
                #     logging.error(f"Error while trying to save LobbyData: {str(exc)}")

                # Increase LOBBY_COUNT so a new Lobby can start
                LOBBY_COUNT += 1
                with open("LobbyCount", "w") as lc:
                    lc.write(str(LOBBY_COUNT))
                logging.debug("Lobby Count Increased")

                await guild.get_channel(VARIABLES["SoloQCommandsID"]).send(embed=discord.Embed(title=f"Lobby {LOBBY_COUNT - 1} Setup Completed!", color=EMBED_COLOR))
                logging.info(f"Lobby {LOBBY_COUNT - 1} Setup Completed!")

                # Just in case
                await asyncio.sleep(60)

                # Send Messages to the lobby
                logging.debug(f"Starting Lobby {LOBBY_COUNT - 1} Countdown...")
                # Send 3-min message
                try:
                    websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{CURRENT_HOST}/{OVERSTAT_API_KEY}"
                    command_send_message_lobby = {"type": "command",
                              "cmd": {
                                  "withAck": True,
                                  "customMatch_SendChat": {
                                      "text": "[BOT] STARTING IN 3 MINUTES"
                                  }
                        }
                    }
                    await ws_r5.send_ws(websocket_server_url, command_send_message_lobby)
                    logging.info(f"Message '3 min' sent!")
                    await asyncio.sleep(60)
                except Exception as exc:
                    logging.error(str(exc))

                # Send 2-min message
                try:
                    websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{CURRENT_HOST}/{OVERSTAT_API_KEY}"
                    command_send_message_lobby = {"type": "command",
                              "cmd": {
                                  "withAck": True,
                                  "customMatch_SendChat": {
                                      "text": "[BOT] STARTING IN 2 MINUTES"
                                  }
                        }
                    }
                    await ws_r5.send_ws(websocket_server_url, command_send_message_lobby)
                    logging.info(f"Message '2 min' sent!")
                    await asyncio.sleep(60)
                except Exception as exc:
                    logging.error(str(exc))
                
                # Send 1-min message
                try:
                    websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{CURRENT_HOST}/{OVERSTAT_API_KEY}"
                    command_send_message_lobby = {"type": "command",
                              "cmd": {
                                  "withAck": True,
                                  "customMatch_SendChat": {
                                      "text": "[BOT] STARTING IN 1 MINUTE"
                                  }
                        }
                    }
                    await ws_r5.send_ws(websocket_server_url, command_send_message_lobby)
                    logging.info(f"Message '1 min' sent!")
                    await asyncio.sleep(60)
                except Exception as exc:
                    logging.error(str(exc))
                
                # Send starting message and start the lobby
                try:
                    websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{CURRENT_HOST}/{OVERSTAT_API_KEY}"
                    command_send_message_lobby = {"type": "command",
                              "cmd": {
                                  "withAck": True,
                                  "customMatch_SendChat": {
                                      "text": "[BOT] STARTING GLHF"
                                  }
                        }
                    }
                    await asyncio.sleep(10)
                    await ws_r5.send_ws(websocket_server_url, command_send_message_lobby)
                    logging.info(f"Message 'starting' sent!")
                    
                    command_start_lobby = {"type": "command",
                        "cmd": {
                            "withAck": True,
                            "customMatch_SetMatchmaking": {
                                "enabled": True
                            }
                        }
                    }

                    await ws_r5.send_ws(websocket_server_url, command_start_lobby)
                    logging.info(f"In-Game Lobby {LOBBY_COUNT - 1} Started!")

                except Exception as exc:
                    logging.error(str(exc))
                
                # try:
                #     await asyncio.sleep(3 * 60)
                #     websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{CURRENT_HOST}/{OVERSTAT_API_KEY}"
                #     command_leave_lobby = {"type": "command",
                #         "cmd": {
                #             "withAck": True,
                #             "customMatch_LeaveLobby": {}
                #         }
                #     }

                #     await ws_r5.send_ws(websocket_server_url, command_leave_lobby)
                #     logging.info(f"Left In-Game Lobby {LOBBY_COUNT - 1}!")

                # except Exception as exc:
                #     logging.error(str(exc))


                

    return

@tasks.loop(minutes=1)
async def remove_temproles():
    for row in await DATABASE.lowprio.read_all():
        if (datetime.now() - datetime.fromtimestamp(row[2])) > timedelta(minutes=1):
            if await DATABASE.lowprio.delete(row[0]):
                role = client.get_guild(CURRENT_GUILD.id).get_role(row[1])
                member = client.get_guild(CURRENT_GUILD.id).get_member(row[0])
                await member.remove_roles(role)
                logging.info(f"Removed {member.display_name}'s Low Priority Role")
    return

@tasks.loop(minutes=10)
async def get_players():
    active_players = client.get_channel(VARIABLES["SoloQGeneralID"])
    num_play = len(client.get_guild(CURRENT_GUILD.id)._voice_states)
    await active_players.send(embed=discord.Embed(description=f"Active Players: {num_play}", color=EMBED_COLOR))
    logging.info(f"Active Players - {num_play}")
    return

# -----------------------------------------------------------------------------------------------------------------------------------------
# |                                                               Solo Queue                                                              |
# -----------------------------------------------------------------------------------------------------------------------------------------
# Setup Queue with queue_vc waiting_room_vc
# Ask for what roles are allowed, this starts the queue and changes the permissions of queue-vc
# Create lobby category, role, lobby-text AND vc's
# Load/Save Lobby Number in a text file
# Start checking Queue VC's
# Once Queue Fills, assign roles, post teams, move players
# Increase Lobby nummber by one, reset other values, start queue again with same values

# Create command to stop queue, without deleting current lobby, move everyone to waiting_room_vc

class SoloQCog(commands.GroupCog, name="soloq"):
    def __init__(self, bot: commands.Bot) -> None:
        self.client = bot
        super().__init__()

    class ApexClientsView(discord.ui.View):
        def __init__(self, lobby_number, team_list):
            super().__init__(timeout=None)
            self.lobby_number = lobby_number
            self.team_list = team_list
            return
        
        @discord.ui.select(placeholder="Select Apex Client", options=utils.clients_to_options())
        async def apexclient_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
            global CURRENT_HOST
            if select.values[0] not in utils.get_connected_apex_clients():
                await interaction.response.send_message("Apex Client is not connected.", ephemeral=True)
                logging.warning(f"Apex Client {select.values[0]} is not connected")
                return
            try:
                await interaction.response.edit_message(embed=discord.Embed(title=f"Selected Apex Client for Lobby {self.lobby_number}: {select.values[0]}", color=EMBED_COLOR), view=None)
            except Exception as exc:
                logging.warning(f"Most Likely Interaction has already been responded to. {exc}")
                await interaction.followup.edit_message(interaction.message.id, embed=discord.Embed(title=f"Selected Apex Client for Lobby {self.lobby_number}: {select.values[0]}", color=EMBED_COLOR), view=None)
            await interaction.followup.send(f"Creating and Setting Up In-Game Lobby {self.lobby_number}. This should take a minute..")

            CURRENT_HOST = select.values[0]

            websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{select.values[0]}/{OVERSTAT_API_KEY}"

            command_join_lobby = {"type": "command", "cmd": { "withAck": True, "customMatch_JoinLobby":
                                                            { "roleToken": VARIABLES["AdminCodes"][self.lobby_number % len(VARIABLES["AdminCodes"])] }
                                                            }}
            
            await ws_r5.send_ws(websocket_server_url, command_join_lobby)
            logging.debug(f"In-Game Lobby {self.lobby_number} Created")

            if self.team_list:
                for team_num, team_name in enumerate([i for i in self.team_list]):
                    command_set_teamname = {"type": "command", "cmd": { "withAck": True, "customMatch_SetTeamName":
                                                                    { "teamId": team_num + 2, "teamName": team_name }
                                                                    }}
                    
                    await ws_r5.send_ws(websocket_server_url, command_set_teamname)
                logging.debug(f"Team Names Set up for Lobby {self.lobby_number}!")

                await interaction.followup.send(embed=discord.Embed(title=f"In-Game Lobby {self.lobby_number} Created.", color=EMBED_COLOR), ephemeral=True)
                logging.info(f"In-Game Lobby {self.lobby_number} Created")
            else:
                await interaction.followup.send(embed=discord.Embed(title=f"No Teams Found for Lobby {self.lobby_number}!", color=EMBED_COLOR))
                logging.warning(f"No Teams Found for Lobby {self.lobby_number}!")
            return 


    @discord.app_commands.command(name="setup-queue", description="Start Queue for Solo Queue.")
    async def setup_queue(self, interaction: discord.Interaction, balancer: Literal["Average MMR", "Fully Random"]):

        # Defer Interaction so Discord doesn't complain
        await interaction.response.defer()

        # Save queue and waiting-room
        global QUEUE_VC, WAITING_ROOM_VC, BALANCER
        BALANCER = balancer
        QUEUE_VC = interaction.guild.get_channel(VARIABLES["QueueVC"])
        WAITING_ROOM_VC = interaction.guild.get_channel(VARIABLES["WaitingRoomVC"])


        # Unlock QUEUE_VC
        everyone_role = interaction.guild.default_role
        await QUEUE_VC.set_permissions(everyone_role, connect=True)

        # Start Checking LowPrio
        remove_temproles.start()
        get_players.start()

        # Send Status
        await interaction.followup.send(embed=discord.Embed(title=f"Solo Queue has been Setup: {QUEUE_VC.mention} & {WAITING_ROOM_VC.mention}", color=EMBED_COLOR))
        logging.info(f"Solo Queue has been Setup: {QUEUE_VC.name} & {WAITING_ROOM_VC.name}")

        return
    
    @discord.app_commands.command(name="stop-queue", description="Stop Queue.")
    async def stop_queue(self, interaction: discord.Interaction):
        logging.debug("Stopping Queue")

        # Defer interaction so Discord doesn't complain
        await interaction.response.defer()

        # Lock QUEUE_VC
        everyone_role = interaction.guild.default_role
        await QUEUE_VC.set_permissions(everyone_role, connect=False)

        # Get Players
        players = QUEUE_VC.members

        # Move players from QUEUE_VC to WAITING_ROOM
        for player in players:
            try:
                await player.move_to(WAITING_ROOM_VC)
            except Exception as exc:
                logging.error(f"Error while trying to move {player.display_name} to {WAITING_ROOM_VC.name}: {str(exc)}")

        remove_temproles.stop()
        get_players.stop()
        # Send Status
        await interaction.followup.send(embed=discord.Embed(title="Queue Stopped.", color=EMBED_COLOR))
        logging.info("Queue Stopped")
        return

    # Delete Category, Role, Voice Channels and Text Channels.
    @discord.app_commands.command(name="delete-lobby", description="Delete Category, Role, Voice Channels and Text Channels.")
    async def delete_lobby(self, interaction: discord.Interaction, lobby_channel: discord.TextChannel):
        logging.debug(f"Deleting Lobby {lobby_channel.name}")

        # Defer interaction so Discord doesn't complain
        await interaction.response.defer()

        # Get Category
        category = lobby_channel.category
        deleted_lobby = category.name

        # Synth3tk: 09-March - Deleted Queue while it was being created
        if str(LOBBY_COUNT) in deleted_lobby:
            logging.warning("BRO")
            await interaction.followup.send(embed=discord.Embed(title="Cannot delete current queue while it's creating."))
            return
        
        connected_users = 0
        for vc in category.voice_channels:
            connected_users += len(vc.voice_states)
        
        if connected_users >= 10:
            logging.warning("Can't delete lobby: >10 users connected.")
            await interaction.followup.send(embed=discord.Embed(title="Cannot delete current queue while a game is happening."))
            return

        # Delete Role
        role = discord.utils.get(interaction.guild.roles, name=f"SoloQ{category.name}")
        await role.delete()

        # Delete Channels
        for channel in category.channels:
            await channel.delete()
        await category.delete()

        await interaction.followup.send(embed=discord.Embed(title=f"{deleted_lobby} Deleted.", color=EMBED_COLOR))
        logging.info(f"{deleted_lobby} Deleted.")
        return
    
    # Create In-Game Lobby for Solo Queue
    @discord.app_commands.command(name="create-apex-lobby", description="Create In-Game Lobby for Solo Queue.")
    async def create_apex_lobby(self, interaction: discord.Interaction, apex_client: str, admin_code: str, team_list: str):
        logging.debug("Creating In-Game Lobby")

        connected = await utils.get_apex_clients()
        
        if apex_client not in connected:
            await interaction.response.send_message(embed=discord.Embed(title="Apex Client not connected", color=EMBED_COLOR))
            return
        
        # Defer interaction so Discord doesn't complain
        await interaction.response.defer()

        websocket_server_url = f"wss://overstat.gg/api/live/read/eternal/{apex_client}/{OVERSTAT_API_KEY}"

        command_join_lobby = {"type": "command", "cmd": { "withAck": True, "customMatch_JoinLobby":
                                                         { "roleToken": admin_code }
                                                         }}
        
        await ws_r5.connect_send_receive_close(websocket_server_url, command_join_lobby)
        logging.debug("In-Game Lobby Created")

        for team_num, team_name in enumerate(team_list.split("\\n")):
            command_set_teamname = {"type": "command", "cmd": { "withAck": True, "customMatch_SetTeamName":
                                                               { "teamId": team_num + 2, "teamName": team_name }
                                                               }}
            
            await ws_r5.connect_send_receive_close(websocket_server_url, command_set_teamname)
        logging.debug("Team names Set up!")

        await interaction.followup.send(embed=discord.Embed(title="In-Game Lobby Created.", color=EMBED_COLOR))
        logging.info("In-Game Lobby Created")
        return

    
    # Get Active Users in Voice Channels in the server.
    @discord.app_commands.command(name="active-players", description="Get Active Users in Voice Channels in the server.")
    async def active_players(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(title=f"Active Users in Voice Channels: {len(interaction.guild._voice_states)}", color=EMBED_COLOR))
        return

    # Gives a Discord Member LowPrio for SoloQ.
    @discord.app_commands.command(name="give-lowprio", description="Gives a Discord Member LowPrio for SoloQ.")
    async def give_lowprio(self, interaction: discord.Interaction, member: discord.Member, duration: Literal["1 hour", "2 hours", "3 hours", "4 hours", "1 day", "1 week"]):
        utils.notify_command(f"Give {member.name} LowPrio")

        if duration == "1 hour":
            time = timedelta(minutes=60)
        elif duration == "2 hours":
            time = timedelta(minutes=120)
        elif duration == "3 hours":
            time = timedelta(minutes=180)
        elif duration == "4 hours":
            time = timedelta(minutes=240)
        elif duration == "1 day":
            time = timedelta(days=1)
        elif duration == "1 week":
            time = timedelta(weeks=1)

        lowpriorole = interaction.guild.get_role(VARIABLES["LowPrioRoleID"])
        if await DATABASE.lowprio.create(member.id, VARIABLES["LowPrioRoleID"], int(round((datetime.now() + time).timestamp()))):
            await member.add_roles(lowpriorole)
            await interaction.response.send_message(embed=discord.Embed(description=f"{member.mention} has been given LowPrio for {duration}.", color=EMBED_COLOR))
        return
    
    # Removes a Discord Member's LowPrio for SoloQ.
    @discord.app_commands.command(name="remove-lowprio", description="Removes a Discord Member's LowPrio for SoloQ.")
    async def remove_lowprio(self, interaction: discord.Interaction, member: discord.Member):
        logging.debug(f"Removing LowPrio for {member.display_name}")

        if await DATABASE.lowprio.delete(member.id):
            role = interaction.guild.get_role(VARIABLES["LowPrioRoleID"])
            await member.remove_roles(role)
            logging.info(f"Removed {member.display_name}'s Low Priority Role")


# -----------------------------------------------------------------------------------------------------------------------------------------
    
# Get User MMR.
@client.tree.command(name="get-user-mmr", description="Get User MMR.", guilds=[CURRENT_GUILD, DEV_GUILD])
async def get_user(interaction: discord.Interaction, user: discord.Member):
    utils.notify_command(f"Get {user.name}'s MMR")

    # Defer interaction so Discord doesn't complain
    await interaction.response.defer()
    
    # Get MMR
    res = await DATABASE.players.read(user.id)
    if res is None:
        await interaction.followup.send(embed=discord.Embed(description=f"{user.mention} 's MMR is not paired.", color=EMBED_COLOR))
    else:
        await interaction.followup.send(embed=discord.Embed(description=f"{user.mention} 's MMR is {res[0]}", color=EMBED_COLOR))
    return

#
@client.tree.command(name="restart-bot", description="Restart Bot.", guilds=[CURRENT_GUILD, DEV_GUILD])
async def restart_bot(interaction: discord.Interaction):
    utils.notify_command("Restart Bot")
    await interaction.response.send_message(embed=discord.Embed(description="Restarting Bot...", color=EMBED_COLOR))
    os.execv(sys.executable, ['python'] + sys.argv)

#

@client.tree.command(name="test", description="Test Command", guilds=[CURRENT_GUILD, DEV_GUILD])
async def test(interaction: discord.Interaction):

    
    # Send starting message and start the lobby
    
    return

# Read Discord API Token
client.run(VARIABLES["DiscordAPIKey"])

# results = await asyncio.gather(*coros, return_exceptions=True)
# for result_or_exc in results:
#     if isinstance(result_or_exc, Exception):
#         print("I caught:", repr(result_or_exc))

"""
wss://overstat.gg/api/live/read/eternal/<clientname>/<api_key>

format:
{
  type: "command",
  cmd: <command>
}

commands: 
JOIN LOBBY
customMatch_JoinLobby: {
    roleToken: <admincode>
}

LEAVE LOBBY
customMatch_LeaveLobby: {}

SEND CHAT
customMatch_SendChat: {
   text: <msg>
}

SETTINGS
customMatch_SetSettings: {
  playlistName: <name>, // map name?
  adminChat: <bool>
  teamRename: bool,
  selfAssign: bool,
  aimAssist: bool,
  anonMOde: bool,
}

START GAME
customMatch_SetMatchmaking: {
    enabled: true,
}

SET TEAM NAME
// You'll want to add a second or 2 delay between setting each team otherwise the client misses it

 customMatch_SetTeamName: {
    teamId: <teamid>, // starts at 2
    teamName: <teamname>
}
"""