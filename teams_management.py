import random

from player import Player, Player_Test, Test
from team import Team
import sqlite_database as db
import logging

# ----------------------------------------------------------------------------------------------
def getPlayersAverage(players: list[Player]) -> float:
    return round(sum(player.MMR for player in players) / len(players), 3)

def sortPlayers(players: list[Player]) -> list[Player]:
    return sorted(players, key=lambda p: p.MMR, reverse=True)

def balancedTeams(players: list[Player], drops: list[str]):
    """
    Balanced Teams by MMR (needs an API Key from @seeescape) (WIP)
    """

    # Initialize empty teams
    n_teams = len(players) // 3
    teams = [Team() for _ in range(n_teams)]
    
    # Sort players by MMR
    players = sortPlayers(players)

    # Divide players into three groups
    T1players, T2players, T3players = players[:len(teams)], players[len(teams):2*len(teams)], players[2*len(teams):]

    # Shuffle and assign captains to teams
    random.shuffle(T1players)
    for i, player in enumerate(T1players):
        teams[i].P1 = player

    # Calculate average MMRs for each team and remaining players
    T1Avg, T2Avg, T3Avg = getPlayersAverage(T1players), getPlayersAverage(T2players), getPlayersAverage(T3players)

    # Assign second players to teams based on balancing criteria
    for team in teams:
        for t2p in T2players:
            if team.P1.MMR + t2p.MMR <= T1Avg + T2Avg + 200:
                team.P2 = t2p
                T2players.remove(t2p)
                break

    # Fill remaining slots in teams if needed
    for i, team in enumerate(teams):
        if team.P2 is None and T2players:
            team.P2 = T2players.pop(0)

    # Calculate average MMR of all teams
    teamsAvg = sum(sum(player.MMR for player in [team.P1, team.P2]) for team in teams) / len(teams)

    # Assign third players to teams based on balancing criteria
    for team in teams:
        for t3p in T3players:
            if team.P1.MMR + team.P2.MMR + t3p.MMR <= teamsAvg + T3Avg + 300:
                team.P3 = t3p
                T3players.remove(t3p)
                break

    # Fill remaining slots in teams if needed
    for team in teams:
        if not team.P3 and T3players:
            team.P3 = T3players.pop(0)
        if not team.P3 and not T3players:
            team.P3 = Player(None, 0.0)

    for team in teams:
        for poi in drops:
            if (poi not in team.P1.previous_POIs) and (poi not in team.P2.previous_POIs) and (poi not in team.P3.previous_POIs):
                drops.remove(poi)
                team.dropspot = poi
                break

    for team in teams:
        if team.dropspot is None:
            team.dropspot = drops.pop(0)

    # Assign Dropspot for Current Game
    for team in teams:
        team.P1.previous_POIs.append(team.dropspot)
        team.P2.previous_POIs.append(team.dropspot)
        team.P3.previous_POIs.append(team.dropspot)
    
    # Extract Players
    soloq_players = []
    for team in teams:
        soloq_players.append(team.P1)
        soloq_players.append(team.P2)
        soloq_players.append(team.P3)

    for player in players:
        if player not in soloq_players:
            soloq_players.append(player)

    # Shuffle teams for randomness
    random.shuffle(teams)
    return teams, soloq_players

def unbalancedTeams(player_list: list, drops: list[str]):
    """
    Fully Randomized Teams, without duplicate POI protection
    """
    random.shuffle(player_list)
    teams: list[Team] = []
    n_teams = len(player_list) // 3
    for i in range(n_teams):
        teams.append(Team())

    for i in range(n_teams):
        teams[i].P1 = player_list[(i * 3) + 0]
        teams[i].P2 = player_list[(i * 3) + 1]
        teams[i].P3 = player_list[(i * 3) + 2]
    
    for team in teams:
        team.dropspot = drops.pop(0)

    return teams

def improvedUnbalancedTeams(player_list: list, drops: list[str], database: db.Database):
    """
    Randomized Teams, with duplicate POI protection & repeated teammates protection
    """
    random.shuffle(player_list)
    teams: list[Team] = []
    n_teams = len(player_list) // 3
    for i in range(n_teams):
        teams.append(Team())

    for i in range(n_teams):
        teams[i].P1 = player_list[(i * 3) + 0]
        teams[i].P2 = player_list[(i * 3) + 1]
        teams[i].P3 = player_list[(i * 3) + 2]

    # Parameters
    num_iterations = 100
    best_combination = n_teams
    best_teams = []

    # ------   Swap Teammates around to minimize repeated teammates   ------
    for _ in range(num_iterations):

        temp_teams = teams.copy()

        # Check if there are teams with repeated teammates
        repeated_players = 0
        for team in temp_teams:

            # Check P1
            p1_previous_teammates = [int(x) for x in database.teammates.read(team.P1.discord_user.id)]
            if ((team.P2.discord_user.id in p1_previous_teammates) or (team.P3.discord_user.id in p1_previous_teammates)):
                repeated_players += 1

            # Check P2
            p2_previous_teammates = [int(x) for x in database.teammates.read(team.P2.discord_user.id)]
            if ((team.P1.discord_user.id in p2_previous_teammates) or (team.P3.discord_user.id in p2_previous_teammates)):
                repeated_players += 1

            # Check P3
            p3_previous_teammates = [int(x) for x in database.teammates.read(team.P3.discord_user.id)]
            if ((team.P1.discord_user.id in p3_previous_teammates) or (team.P2.discord_user.id in p3_previous_teammates)):
                repeated_players += 1

        # Check if it's better than the best saved iterations
        if repeated_players < best_combination:
            best_combination = repeated_players
            best_teams = temp_teams.copy()

        # Shift Teammates by 1 and 3
        for idx, team in enumerate(temp_teams):
            aux_p2 = temp_teams[(idx + 1) % n_teams].P2
            aux_p3 = temp_teams[(idx + 3) % n_teams].P3
            temp_teams[(idx + 1) % n_teams].P2 = team.P2
            temp_teams[(idx + 3) % n_teams].P3 = team.P3
            team.P2 = aux_p2
            team.P3 = aux_p3
    
    teams = best_teams
    logging.info(f"Repeated teammates: {best_combination}")

    # Parameters
    num_iterations = 100
    best_combination = n_teams
    best_teams = []

    # ---------   Swap POIs around to minimize repeated POIs   ---------
    for _ in range(num_iterations):
        temp_teams = teams.copy()
        temp_drops = drops.copy()
        random.shuffle(temp_drops)
        for team in temp_teams:
            for poi in temp_drops:
                if (poi not in database.drops.read(team.P1)) and (poi not in database.drops.read(team.P2)) and (poi not in database.drops.read(team.P3)):
                    temp_drops.remove(poi)
                    team.dropspot = poi
                    break
        for team in temp_teams:
            if team.dropspot is None:
                team.dropspot = drops.pop(0)
        # Check if there are teams with repeated dropspots
        repeated_pois = []
        for team in temp_teams:
            if (team.dropspot in database.drops.read(team.P1)) or (team.dropspot in database.drops.read(team.P2)) or (team.dropspot in database.drops.read(team.P3)):
                repeated_pois.append(team)

        if len(repeated_pois) < best_combination:
            best_combination = len(repeated_pois)
            best_team = temp_teams.copy()  
    
    teams = best_team
    logging.info(f"Repeated POIs: {best_combination}")
    
    # Assign Dropspot for Current Game
    for team in teams:
        # Save Player 1's drops
        aux1 = database.drops.read(team.P1.discord_user.id)
        if aux1 == [""]:
            aux1 = [team.dropspot]
        else:
            aux1.append(team.dropspot)
        if not database.drops.update(team.P1.discord_user.id, aux1):
            logging.warning(f"Failed to update {team.P1.discord_user.id}")
        
        # Save Player 2's drops
        aux2 = database.drops.read(team.P2.discord_user.id)
        if aux2 == [""]:
            aux2 = [team.dropspot]
        else:
            aux2.append(team.dropspot)
        if not database.drops.update(team.P2.discord_user.id, aux1):
            logging.warning(f"Failed to update {team.P2.discord_user.id}")
        
        # Save Player 3's drops
        aux3 = database.drops.read(team.P3.discord_user.id)
        if aux3 == [""]:
            aux3 = [team.dropspot]
        else:
            aux3.append(team.dropspot)
        if not database.drops.update(team.P3.discord_user.id, aux1):
            logging.warning(f"Failed to update {team.P3.discord_user.id}")
    return teams

# ----------------------------------------------------------------------------------------------
def find_duplicates(teams_list: list[Team]):
    strings = []
    for team in teams_list:
        strings.append(team.P1.discord_user.id)
        strings.append(team.P2.discord_user.id)
        strings.append(team.P3.discord_user.id)
    # Dictionary to store counts of each string
    counts = {}

    # List to store duplicates
    duplicates = []

    # Count occurrences of each string
    for string in strings:
        counts[string] = counts.get(string, 0) + 1

    # Find duplicates
    for string, count in counts.items():
        if count > 1:
            duplicates.append(string)

    return duplicates
    