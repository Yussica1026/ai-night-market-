"""AI 夜市 stdio MCP 服务。"""
import asyncio, os, random
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from market_data import STALLS, market_overview
from storage import NightMarketDatabase
mcp=FastMCP("AI 夜市",json_response=True)
database=NightMarketDatabase(Path(os.environ.get("NIGHT_MARKET_DATA_DIR",Path.home()/".ai-night-market"))/"market.sqlite3",50)
@mcp.tool()
async def visit_night_market(player_id:str)->dict:
    """随机逛一个夜市摊位并收集食材。"""
    stall=random.choice(list(STALLS));info=STALLS[stall];coins=await database.visit(player_id,info['ingredient'],5);return {"stall":stall,"owner":info['owner'],"ingredient":info['ingredient'],"coins":coins}
@mcp.tool()
async def order_night_market(player_id:str,stall:str,item:str)->dict:
    """在指定摊位点单。"""
    if stall not in STALLS or item not in STALLS[stall]['menu']:return {"ok":False,"error":"菜单不存在"}
    ok,coins=await database.order(player_id,stall,item,STALLS[stall]['menu'][item]);return {"ok":ok,"coins":coins,"item":item}
@mcp.tool()
async def night_market_profile(player_id:str)->dict:
    """查看夜市玩家状态。"""
    coins,level,favor,items=await database.profile(player_id);return {"coins":coins,"stall_level":level,"favor":favor,"inventory":dict(items)}
@mcp.tool()
def night_market_menu()->str:
    """查看当前夜市菜单。""";return market_overview()
if __name__=="__main__":
    asyncio.run(database.initialize());mcp.run()
