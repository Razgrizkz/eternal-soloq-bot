import random

from player import Player, Player_Test, Test
from team import Team

# ----------------------------------------------------------------------------------------------
def getPlayersAverage(players: list[Player]) -> float:
    return round(sum(player.MMR for player in players) / len(players), 3)

def sortPlayers(players: list[Player]) -> list[Player]:
    return sorted(players, key=lambda p: p.MMR, reverse=True)

def balancedTeams(players: list[Player]) -> list[Team]:

    # Initialize empty teams
    teams = [Team() for _ in range(len(players) // 3)]
    
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

    # Shuffle teams for randomness
    random.shuffle(teams)
    return teams

def unbalancedTeams(player_list: list, n_teams: int):
    teams: list[Team] = []
    for i in range(n_teams):
        teams.append(Team())

    for i in range(n_teams):
        teams[i].P1 = player_list[(i * 3) + 0]
        teams[i].P2 = player_list[(i * 3) + 1]
        teams[i].P3 = player_list[(i * 3) + 2]
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
    