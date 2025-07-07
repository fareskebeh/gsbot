from telegram import Bot
import asyncio

async def test():
    bot = Bot(token="8079180952:AAGZ5E--ih_CPe2_1tnMdWmW_gmCN_N40HA")
    me = await bot.get_me()
    print(f"✅ Bot is alive: {me.username}")

asyncio.run(test())