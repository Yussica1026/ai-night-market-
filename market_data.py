"""夜市固定摊位、菜单与食材。"""

STALLS = {
    "烟火烧烤摊": {"owner": "炭火", "menu": {"蜜汁烤串": 12, "辣烤玉米": 10}, "ingredient": "炭火香料"},
    "月光糖水铺": {"owner": "月匙", "menu": {"桂花酒酿": 11, "椰奶冰粉": 9}, "ingredient": "桂花蜜"},
    "霓虹杂货铺": {"owner": "阿灯", "menu": {"幸运汽水": 8, "夜光贴纸": 6}, "ingredient": "霓虹玻璃珠"},
    "星签占卜摊": {"owner": "北斗", "menu": {"一张星签": 10, "月相挂件": 15}, "ingredient": "星砂"},
}

UPGRADES = {1: (0, 0), 2: (30, 2), 3: (70, 5), 4: (130, 9)}


def market_overview():
    return "\n".join(f"【{name}】摊主：{info['owner']}｜" + "、".join(f"{item} {price}币" for item, price in info["menu"].items()) for name, info in STALLS.items())
