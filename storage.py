import asyncio
import sqlite3
from contextlib import closing
from datetime import date
from pathlib import Path


class NightMarketDatabase:
    def __init__(self, path: Path, initial_coins: int):
        self.path, self.initial_coins = path, max(0, initial_coins)
        self.lock, self.initialized = asyncio.Lock(), False

    def _connect(self): return sqlite3.connect(self.path)

    async def initialize(self):
        if self.initialized: return
        async with self.lock:
            if not self.initialized:
                await asyncio.to_thread(self._setup); self.initialized = True

    def _setup(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as conn, conn:
            conn.executescript("CREATE TABLE IF NOT EXISTS players(user_id TEXT PRIMARY KEY,coins INTEGER NOT NULL,last_daily TEXT,stall_level INTEGER NOT NULL DEFAULT 1,favor INTEGER NOT NULL DEFAULT 0);CREATE TABLE IF NOT EXISTS inventory(user_id TEXT,item TEXT,amount INTEGER NOT NULL,PRIMARY KEY(user_id,item));CREATE TABLE IF NOT EXISTS orders(user_id TEXT,stall TEXT,item TEXT,amount INTEGER NOT NULL,PRIMARY KEY(user_id,stall,item));")

    def _player(self, conn, user_id): conn.execute("INSERT OR IGNORE INTO players(user_id,coins) VALUES(?,?)", (user_id,self.initial_coins))
    async def _run(self, func, *args):
        await self.initialize()
        async with self.lock: return await asyncio.to_thread(func,*args)

    async def daily(self,user,reward): return await self._run(self._daily,user,reward)
    def _daily(self,user,reward):
        today=date.today().isoformat()
        with closing(self._connect()) as conn,conn:
            self._player(conn,user); coins,last=conn.execute("SELECT coins,last_daily FROM players WHERE user_id=?",(user,)).fetchone()
            if last==today:return False,coins
            coins+=max(0,reward);conn.execute("UPDATE players SET coins=?,last_daily=? WHERE user_id=?",(coins,today,user));return True,coins

    async def visit(self,user,item,reward): return await self._run(self._visit,user,item,reward)
    def _visit(self,user,item,reward):
        with closing(self._connect()) as conn,conn:
            self._player(conn,user);conn.execute("UPDATE players SET coins=coins+?,favor=favor+1 WHERE user_id=?",(reward,user));conn.execute("INSERT INTO inventory VALUES(?,?,1) ON CONFLICT(user_id,item) DO UPDATE SET amount=amount+1",(user,item));coins=conn.execute("SELECT coins FROM players WHERE user_id=?",(user,)).fetchone()[0];return coins

    async def order(self,user,stall,item,price): return await self._run(self._order,user,stall,item,price)
    def _order(self,user,stall,item,price):
        with closing(self._connect()) as conn,conn:
            self._player(conn,user);coins=conn.execute("SELECT coins FROM players WHERE user_id=?",(user,)).fetchone()[0]
            if coins<price:return False,coins
            conn.execute("UPDATE players SET coins=coins-?,favor=favor+2 WHERE user_id=?",(price,user));conn.execute("INSERT INTO orders VALUES(?,?,?,1) ON CONFLICT(user_id,stall,item) DO UPDATE SET amount=amount+1",(user,stall,item));return True,coins-price

    async def upgrade(self,user,cost,need): return await self._run(self._upgrade,user,cost,need)
    def _upgrade(self,user,cost,need):
        with closing(self._connect()) as conn,conn:
            self._player(conn,user);coins,level=conn.execute("SELECT coins,stall_level FROM players WHERE user_id=?",(user,)).fetchone();ingredients=conn.execute("SELECT COALESCE(SUM(amount),0) FROM inventory WHERE user_id=?",(user,)).fetchone()[0]
            if coins<cost or ingredients<need:return False,coins,level
            conn.execute("UPDATE players SET coins=coins-?,stall_level=stall_level+1 WHERE user_id=?",(cost,user));conn.execute("DELETE FROM inventory WHERE user_id=?",(user,));return True,coins-cost,level+1

    async def profile(self,user): return await self._run(self._profile,user)
    def _profile(self,user):
        with closing(self._connect()) as conn,conn:
            self._player(conn,user);coins,level,favor=conn.execute("SELECT coins,stall_level,favor FROM players WHERE user_id=?",(user,)).fetchone();items=conn.execute("SELECT item,amount FROM inventory WHERE user_id=?",(user,)).fetchall();return coins,level,favor,items

    async def order_count(self,user): return await self._run(self._order_count,user)
    def _order_count(self,user):
        with closing(self._connect()) as conn,conn:
            self._player(conn,user)
            return conn.execute("SELECT COALESCE(SUM(amount),0) FROM orders WHERE user_id=?",(user,)).fetchone()[0]
