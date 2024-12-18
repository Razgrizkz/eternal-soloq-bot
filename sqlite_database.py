import sqlite3
from typing import Union
import logging

class Database:
    def __init__(self, players, lowprio, teammates, drops) -> None:
        self.players: Player = players
        self.lowprio: LowPrio = lowprio
        self.teammates: Teammates = teammates
        self.drops: Drops = drops

# -------------------------------------------------------------------------------------------------------------------------------------------

class Player:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    async def create(self, discord_id: int, mmr: float):
        cur = self.connection.cursor()
        try:
            cur.execute(f"INSERT OR REPLACE INTO player (discord_id, mmr) VALUES ({discord_id}, {mmr});")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
    async def read(self, discord_id: int):
        cur = self.connection.cursor()
        try:
            cur.execute(f"SELECT mmr FROM player WHERE discord_id={discord_id};")
            res = cur.fetchone()
            cur.close()
            return res
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
        return None
    
    async def read_all(self) -> tuple:
        cur = self.connection.cursor()
        try:
            cur.execute(f"SELECT * FROM player;")
            res = cur.fetchall()
            cur.close()
            return res
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
        return []
    
    async def delete_all(self):
        cur = self.connection.cursor()
        try:
            cur.execute(f"DELETE FROM player;")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True

# -------------------------------------------------------------------------------------------------------------------------------------------
    
class LowPrio:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    async def create(self, discord_id: int, role_id: int, remove_on: int):
        cur = self.connection.cursor()
        try:
            cur.execute(f"INSERT OR REPLACE INTO lowprio (discord_id, role_id, remove_on) VALUES ({discord_id}, {role_id}, {remove_on});")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
    async def read_all(self):
        cur = self.connection.cursor()
        try:
            cur.execute(f"SELECT * FROM lowprio;")
            res = cur.fetchall()
            cur.close()
            return res
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
        return []
    
    async def delete(self, discord_id: int):
        cur = self.connection.cursor()
        try:
            cur.execute(f"DELETE FROM lowprio WHERE discord_id={discord_id};")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True

# -------------------------------------------------------------------------------------------------------------------------------------------

class Teammates:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create(self, discord_id: int, players: list[int]):
        cur = self.connection.cursor()
        try:
            aux = '|'.join(map(str, players))
            cur.execute(f"INSERT OR REPLACE INTO teammates (discord_id, players) VALUES ({discord_id}, '{aux}');")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
    def read(self, discord_id: int):
        cur = self.connection.cursor()
        try:
            cur.execute(f"SELECT players FROM teammates WHERE discord_id={discord_id};")
            res = cur.fetchone()
            cur.close()
            if res is None:
                return []
            return res[0].split("|")
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
        return []
    
    def update(self, discord_id: int, players: list[int]):
        cur = self.connection.cursor()
        try:
            aux = '|'.join(map(str, players))
            cur.execute(f"UPDATE teammates SET players='{aux}' WHERE discord_id={discord_id}")
            self.connection.commit()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True

    
    def delete_all(self):
        cur = self.connection.cursor()
        try:
            cur.execute(f"DELETE FROM teammates;")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True

class Drops:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
    
    def create(self, discord_id: int, drops: list[str]):
        cur = self.connection.cursor()
        try:
            aux = '|'.join(drops)
            cur.execute(f"INSERT OR REPLACE INTO drops (discord_id, dropspots) VALUES ({discord_id}, '{aux}');")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
    def read(self, discord_id: int):
        cur = self.connection.cursor()
        try:
            cur.execute(f"SELECT dropspots FROM drops WHERE discord_id={discord_id};")
            res = cur.fetchone()
            cur.close()
            if res is None:
                return []
            return res[0].split("|")
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
        return []
    
    def update(self, discord_id: int, players: list[int]):
        cur = self.connection.cursor()
        try:
            aux = '|'.join(map(str, players))
            cur.execute(f"UPDATE drops SET dropspots='{aux}' WHERE discord_id={discord_id}")
            self.connection.commit()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
    def delete_all(self):
        cur = self.connection.cursor()
        try:
            cur.execute(f"DELETE FROM drops;")
            self.connection.commit()
            cur.close()
        except sqlite3.Error as exc:
            cur.close()
            logging.error(exc)
            return False
        return True
    
# -------------------------------------------------------------------------------------------------------------------------------------------

# Create a database connection to a SQLite database
def create_connection(db_file: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_file, timeout=10)
    return conn

def create_tables(conn: sqlite3.Connection):
    if conn is not None:
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS player (discord_id INTEGER PRIMARY KEY, mmr REAL);")
        conn.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS lowprio (discord_id INTEGER PRIMARY KEY, role_id INTEGER, remove_on INTEGER);")
        conn.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS teammates (discord_id INTEGER PRIMARY KEY, players VARCHAR);")
        conn.commit()
        cur.execute("CREATE TABLE IF NOT EXISTS drops (discord_id INTEGER PRIMARY KEY, dropspots VARCHAR);")
        conn.commit()

        cur.close()
    else:
        print("Failed to connect to database!")
        exit()
    return conn
