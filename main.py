"""AstrBot AI 夜市插件。"""
import random
from pathlib import Path
from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.core.utils.astrbot_path import get_astrbot_data_path
from .market_data import EVENTS, STALL_LOOKS, STALLS, UPGRADES, market_overview
from .storage import NightMarketDatabase


class AINightMarket(Star):
    def __init__(self, context: Context, config: AstrBotConfig | None = None):
        super().__init__(context);self.config=config
        self.database=NightMarketDatabase(Path(get_astrbot_data_path())/"plugin_data"/"astrbot_plugin_ai_night_market"/"market.sqlite3",self.number("initial_coins",50))
    def number(self,key,default):
        if self.config is None:return default
        value=self.config.get(key,default);return value if isinstance(value,int) else default
    def user(self,event): return str(event.get_sender_id())
    @filter.command("夜市")
    async def market(self,event:AstrMessageEvent):
        """查看夜市摊位与菜单。""";yield event.plain_result("AI 夜市开张：\n"+market_overview()+"\n\n/夜市逛逛｜/夜市点单 摊位 菜品｜/夜市砍价 摊位｜/夜市背包｜/夜市升级")
    @filter.command("夜市签到")
    async def daily(self,event:AstrMessageEvent):
        """领取每日夜市币。""";ok,coins=await self.database.daily(self.user(event),self.number("daily_coins",20));yield event.plain_result(f"{'签到成功。' if ok else '今天已经签到过了。'}当前夜市币：{coins}。");
    @filter.command("夜市逛逛")
    async def visit(self,event:AstrMessageEvent):
        """随机拜访摊位并收集食材。""";stall=random.choice(list(STALLS));info=STALLS[stall];coins=await self.database.visit(self.user(event),info['ingredient'],self.number("event_coins",5));yield event.plain_result(f"你逛到【{stall}】，摊主 {info['owner']} 送了你一份 {info['ingredient']}。\n获得夜市币，当前：{coins}。");
    @filter.command("夜市点单")
    async def order(self,event:AstrMessageEvent,stall:str,item:str):
        """点单，例如 /夜市点单 月光糖水铺 桂花酒酿。"""
        if stall not in STALLS or item not in STALLS[stall]['menu']:yield event.plain_result("没有这份菜单。发送 /夜市 查看摊位。 ");return
        price=STALLS[stall]['menu'][item];ok,coins=await self.database.order(self.user(event),stall,item,price)
        text=f"点单成功：{item}。\n{STALLS[stall]['line']}" if ok else "夜市币不足。"
        yield event.plain_result(f"{text}\n当前夜市币：{coins}。")
    @filter.command("夜市砍价")
    async def bargain(self,event:AstrMessageEvent,stall:str):
        """和指定摊主砍价。"""
        if stall not in STALLS:yield event.plain_result("没有这个摊位。");return
        lines=["摊主笑着点头：这单给你打九折。","摊主摇头：这个价已经很实在啦。","摊主递来一份试吃：下次来给你留份大的。"]
        yield event.plain_result(f"【{stall}】{random.choice(lines)}")
    @filter.command("夜市背包")
    async def bag(self,event:AstrMessageEvent):
        """查看夜市币、食材和摊位等级。""";coins,level,favor,items=await self.database.profile(self.user(event));yield event.plain_result(f"夜市币：{coins}\n我的摊位：Lv.{level}｜{STALL_LOOKS[level]}\n摊主好感：{favor}\n食材："+("、".join(f"{name}×{amount}" for name,amount in items) or "暂无"))
    @filter.command("夜市升级")
    async def upgrade(self,event:AstrMessageEvent):
        """消耗夜市币和食材升级自己的摊位。""";_,level,_,_=await self.database.profile(self.user(event));cost,need=UPGRADES.get(level+1,(0,0))
        if not cost:yield event.plain_result("你的摊位已经是当前最高等级。 ");return
        ok,coins,new_level=await self.database.upgrade(self.user(event),cost,need);yield event.plain_result(f"{'升级成功，摊位达到 Lv.'+str(new_level)+'！' if ok else f'升级需要 {cost} 夜市币和 {need} 份食材。'}当前夜市币：{coins}。")
    @filter.command("夜市事件")
    async def event(self,event:AstrMessageEvent):
        """触发一次随机夜市事件。"""
        text,reward=random.choice(EVENTS);coins=await self.database.visit(self.user(event),random.choice([info['ingredient'] for info in STALLS.values()]),reward)
        yield event.plain_result(f"{text}\n获得食材与 {reward} 夜市币。当前：{coins}。")
    @filter.command("夜市任务")
    async def task(self,event:AstrMessageEvent):
        """查看下一阶段订单目标。"""
        count=await self.database.order_count(self.user(event));target=((count//5)+1)*5
        yield event.plain_result(f"夜市订单：{count} 单。\n下一目标：完成 {target} 单订单，解锁一段摊主小故事。")

    @filter.llm_tool(name="visit_night_market")
    async def llm_visit(self,event:AstrMessageEvent,note:str=""):
        """带当前用户随机逛一个夜市摊位并收集食材。

        Args:
            note(string): 可选的逛夜市请求说明。
        """
        stall=random.choice(list(STALLS));info=STALLS[stall]
        coins=await self.database.visit(self.user(event),info['ingredient'],self.number("event_coins",5))
        yield event.plain_result(f"来到【{stall}】。{info['line']}\n获得 {info['ingredient']}，当前夜市币：{coins}。")

    @filter.llm_tool(name="order_night_market")
    async def llm_order(self,event:AstrMessageEvent,stall:str,item:str):
        """让当前用户在夜市指定摊位点单。

        Args:
            stall(string): 摊位名称。
            item(string): 菜品或商品名称。
        """
        if stall not in STALLS or item not in STALLS[stall]['menu']:
            yield event.plain_result("菜单不存在。")
            return
        ok,coins=await self.database.order(self.user(event),stall,item,STALLS[stall]['menu'][item])
        yield event.plain_result(f"{'点单成功：'+item+'。' if ok else '夜市币不足。'}当前夜市币：{coins}。")

    @filter.llm_tool(name="night_market_profile")
    async def llm_profile(self,event:AstrMessageEvent,note:str=""):
        """查看当前用户的夜市经营状态。

        Args:
            note(string): 可选的状态查询说明。
        """
        coins,level,favor,items=await self.database.profile(self.user(event))
        yield event.plain_result(f"夜市币：{coins}\n摊位：Lv.{level}｜{STALL_LOOKS[level]}\n好感：{favor}\n食材："+("、".join(f"{name}×{amount}" for name,amount in items) or "暂无"))

    @filter.llm_tool(name="night_market_menu")
    async def llm_menu(self,event:AstrMessageEvent,note:str=""):
        """查看 AI 夜市全部摊位与菜单。

        Args:
            note(string): 可选的菜单查询说明。
        """
        yield event.plain_result(market_overview())
