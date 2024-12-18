# eternal-soloq-bot
 Python Discord bot for Eternal eSports Club.

## Setup Instructions
You can modify `variables.json` for general options, but this requires the bot to restart

### Commands
- `setup-queue` - Start Queue for Solo Queue.
- `stop-queue` - Stop Queue and clear POI and Previos Teammates Data.
- `delete-lobby` - Delete Category, Role, Voice Channels and Text Channels.
- `clear-previous-drops` - Delete Previous Records of POIs that prevent repetition.
- `active-players` - Get Active Users in Voice Channels in the server.
- `give-lowprio` - Gives a Discord Member Temporary LowPrio for SoloQ.
- `remove-lowprio` - Removes a Discord Member's LowPrio for SoloQ.
- `add-immune` - Add Users to be skipped from the Queue.
- `remove-immune` - Remove Users to be skipped from the Queue.
- `check-immune` - Displays Users to be skipped from the Queue.
- `restart-bot` - Restarts the bot, reloading the file `variables.json`.

# SoloQ Bot Algorithm
- /soloq setup-queue `balancer` `maps` `dropships_settings`
    - Opens `queue-vc` 
    - Starts Checking for # of users in `queue-vc`
    - Downloads MMR data
- `queue-vc` reaches 60 users
    -  Closes  `queue-vc`
    - Splits users in 20 teams: `balanced based on MMR`, `fully random` or `improved random` (minimizes the chance of getting the same POI or the same teammates)
    - Randomize POIs, Map is based on Lobby number
    - Creates Category, Text channel & 20 VCs with team numbers and assigned dropspots
    - Move users to their VCs
    - Post Teams List & Dropspots
    - Increase Lobby number for next lobby to be filled
    - Opens `queue-vc`
- /soloq stop-queue
  - Closes `queue-vc` and moves everyone to `waiting-room``
  - Doesn't stop lobbies already running