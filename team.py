from player import Player

class Team:
    def __init__(self) -> None:
        self.P1: Player = None
        self.P2: Player = None
        self.P3: Player = None
        self.dropspot: str = None

    def ToList(self) -> list[Player]:
        return [self.P1, self.P2, self.P3]


    def __str__(self) -> str:
        return f"{self.P1}\n{self.P2}\n{self.P3}"

    
class TDMTeam:
    def __init__(self, players: list[Player]) -> None:
        if len(players) == 6:
            self.P1: Player = players[0]
            self.P2: Player = players[1]
            self.P3: Player = players[2]
            self.P4: Player = players[3]
            self.P5: Player = players[4]
            self.P6: Player = players[5]
        else:
            self.P1 = None
            self.P2 = None
            self.P3 = None
            self.P4 = None
            self.P5 = None
            self.P6 = None

    def __str__(self) -> str:
        return f"{self.P1}\n{self.P2}\n{self.P3}\n{self.P4}\n{self.P5}\n{self.P6}"