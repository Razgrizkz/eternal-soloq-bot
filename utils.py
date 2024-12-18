import datetime
import discord
import requests

from player import Player

EMBED_COLOR = 0x8D00C5

COLOR_LIST = ["#067d8e", "#1a4868", "#2154cc", "#432a61",
              "#6c2d6f", "#aa2e7a", "#b01c50", "#c1000a",
              "#c5431f", "#761c12", "#a03a0e", "#764b01",
              "#cd7914", "#947a00", "#7b831d", "#4a5802",
              "#6f9742", "#388834", "#2f5919", "#007357"]

OVERSTAT_MAPS = {
    "World's Edge": "mp_rr_desertlands_hu_lc",
    "Storm Point": "mp_rr_tropic_island_mu2",
    "Olympus": "mp_rr_olympus_mu2",
    "King's Canyon": "mp_rr_canyonlands_hu",
    "Broken Moon": "mp_rr_divided_moon"
}

# OVERSTAT_API = open("OverstatAPI", encoding="ISO-8859-1").read()
# OVERSTAT_KEY = open("OverstatKey", encoding="ISO-8859-1").read()

def notify_command(message: str):
    print(f"\033[1m\033[90m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \033[96mCOMMAND  \033[0m{message}")
    return

def notify_success(message: str):
    print(f"\033[1m\033[90m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \033[92mSUCCESS  \033[94m{message}\033[0m")
    return

def notify_error(message: str):
    print(f"\033[1m\033[90m{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \033[91mERROR    \033[94m{message}\033[0m")
    return

# -------------------------------------------------------------------------------------------------------------------------------------------

# def overstat_drops(session: requests.Session, team_n: int, POIs: list[str], match_id: int, map_string: str, password: str):
#     # Add Teams to Overstat
#     url = "https://overstat.gg/api/drop"
#     for i in POIs:
#         params = {"matchId":match_id, "teamName":f"Team {(team_n + 1)}", "map":map_string, "pass":password, "color":COLOR_LIST[team_n], "drop":i}
#         res = session.post(url, json=params)
#         print(res.status_code)

# def delete_drops(session: requests.Session, match_id: int, map_string: str):
#     # Clear Previous Map
#     url = f"https://overstat.gg/api/drop_delete_admin/{match_id}/{OVERSTAT_MAPS[map_string]}"
#     hdrs = {"x-organizer-name": OVERSTAT_API, "x-organizer-key": OVERSTAT_KEY}
#     session.delete(url, headers=hdrs)
#     return

# ---------------- Players MMR -----------------------
async def download_mmr() -> list:
    # Download MMR Data
    hdrs = {"apiKey": ""}
    res = requests.get("https://api.eternalesports.club/api/Players", headers=hdrs)
    players = []
    for player in res.json():
        players.append((player["discordID"], player["MMR"]))
    return players

# ---------------- Get Apex Clients -----------------

def get_apex_clients() -> list:
    res = requests.get("https://overstat.gg/api/live/clients/eternal")
    data: dict[str, str] = res.json()
    observers = []
    for client in data:
        observers.append(client)
    return observers[3:]

def get_connected_apex_clients() -> list:
    res = requests.get("https://overstat.gg/api/live/clients/eternal")
    data: dict[str, str] = res.json()
    connected = []
    for client in data:
        if data[client]["connected"]:
            connected.append(client)
    return connected

def clients_to_options():
    clients = get_apex_clients()
    options = [discord.SelectOption(label=client) for client in clients]
    return options

def admincodes_to_options(admincodes: list):
    options = []
    for idx, x in enumerate(admincodes):
        options.append(discord.SelectOption(label=f"Lobby Code {idx + 1}", value=str(x)))
    return options
