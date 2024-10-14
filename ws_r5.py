import asyncio
import websockets
import json
import logging
        
async def send_ws(url, message):
    async with websockets.connect(url) as websocket:
        #logging.debug("Connected to WebSocket server")

        # Sending message
        await websocket.send(json.dumps(message))
        logging.debug(f"Sent message: {message}")

        await asyncio.sleep(2)

        # Waiting for response
        response = await websocket.recv()
        #logging.debug(f"Received response: {response}")

        # Closing connection
        await websocket.close()
        #logging.debug("Connection closed")
        return

# # Provide the WebSocket server URL

# command_join_lobby = {"type": "command",
#                         "cmd": {
#                             "withAck": True,
#                             "customMatch_JoinLobby": {
#                                 "roleToken": "<admin_code>"
#                             }
#                         }
# }

# command_leave_lobby = {"type": "command",
#                         "cmd": {
#                             "withAck": True,
#                             "customMatch_LeaveLobby": {}
#                         }
# }

# command_start_lobby = {"type": "command",
#                         "cmd": {
#                             "withAck": True,
#                             "customMatch_SetMatchmaking": {
#                                 "enabled": True
#                             }
#                         }
# }

# command_settings_lobby = {"type": "command",
#                         "cmd": {
#                             "withAck": True,
#                             "customMatch_SetSettings": {
#                                 "adminChat": False,
#                                 "teamRename": False,
#                                 "selfAssign": True,
#                                 "aimAssist": True,
#                                 "anonMode": True
#                             }
#                         }
# }

# command_send_message_lobby = {"type": "command",
#                               "cmd": {
#                                   "withAck": True,
#                                   "customMatch_SendChat": {
#                                       "text": "Testing Messages!"
#                                   }
#                         }
# }

# command_set_teamname = {"type": "command",
#                         "cmd": {
#                             "withAck": True,
#                             "customMatch_SetTeamName": {
#                                 "teamId": 2,
#                                 "teamName": "TestingTrio"
#                             }
#                         }}

# # Connect and listen to messages
# asyncio.run(connect_send_receive_close(websocket_server_url, command_join_lobby))
# asyncio.run(connect_send_receive_close(websocket_server_url, command_set_teamname))

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
    roleToken: <admin_code>
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
  anonMode: bool,
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
