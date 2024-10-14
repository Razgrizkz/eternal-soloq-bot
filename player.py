import discord
from typing import Union

class Player:
    def __init__(self, user: Union[discord.Member, None], mmr: float = 800) -> None:
        self.discord_user = user
        self.MMR = mmr
        return
    
    def __str__(self) -> str:
        if self.discord_user is None:
            return "<None>"
        else:
            return f"<@{self.discord_user.id}> - {int(self.MMR)}"
        
    def debug(self) -> str:
        if self.discord_user is None:
            return "<None>"
        else:
            return self.discord_user.name
        
    def __hash__(self):
        if self.discord_user is None:
            return 0
        else:
            return hash(self.discord_user.id)
    
    def __eq__(self, other): 
        if not isinstance(other, Player):
            # don't attempt to compare against unrelated types
            return NotImplemented
        if self.discord_user is None or other.discord_user is None:
            return False
        else:
            return self.discord_user.id == other.discord_user.id


class Test:
    def __init__(self, id: int) -> None:
        self.id = id
        return
    
    def __str__(self) -> str:
        return f"{self.id}"
    
class Player_Test:
    def __init__(self, user: Test, mmr: float = 800) -> None:
        self.discord_user = user
        self.MMR = mmr
        return
    
    def __str__(self) -> str:
        if self.discord_user is None:
            return "<None>"
        else:
            return f"{self.discord_user.id}"
    
    def __hash__(self):
        return hash(self.discord_user.id)
    
    def __eq__(self, other): 
        if not isinstance(other, Player):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.discord_user.id == other.discord_user.id
