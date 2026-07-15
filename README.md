# AI Night Market

面向 AstrBot 的 AI 夜市经营游戏：和 AI 摊主聊天点单、砍价、逛夜市收集食材，并升级自己的小摊。使用异步 SQLite 保存进度，提供 MCP 工具和可选网页前端。

设计及编写：阿栈

## 功能

- 四个 AI 摊位与固定菜单
- 签到、逛夜市、随机事件、点单、砍价、订单目标、背包、摊位升级
- 异步 SQLite 持久化
- MCP：逛夜市、点单、查看状态、查看菜单
- 静态网页试玩版

## AstrBot 指令

- `/夜市`、`/夜市签到`、`/夜市逛逛`
- `/夜市点单 摊位 菜品`
- `/夜市砍价 摊位`、`/夜市背包`、`/夜市升级`
- `/夜市事件`、`/夜市任务`

## MCP

安装 `requirements-mcp.txt` 后运行 `mcp_server.py`，以 stdio MCP 方式注册到 AstrBot。

插件同时原生注册 `visit_night_market`、`order_night_market`、`night_market_profile`、`night_market_menu` 四个 AstrBot LLM 工具，不需要外置 MCP 才能由 AI 调用。

## 开源协议

MIT License.
