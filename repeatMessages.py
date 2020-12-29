import os
import asyncio

repeater = {
    "startWithBot": False,
    "s": 15*60,
    "messages": [
        "Join our inclusive discord community at https://discord.gg/TAfxrBzHv8 :)",
        "We're running a charity event! Help your LGBTQ community by donating at https://streamlabscharity.com/@4feetapart/the-trevor-project -- anything helps! Even a dollar!",
        "Say '!ttt start @user' to start a Tic-Tac-Toe game against someone! Or, say '!ttt help' to find more Tic-Tac-Toe commands :)"
    ]
}
async def repeatMessages(bot):
    if len(repeater["messages"]) == 0:
        return
    n = 0
    if repeater["startWithBot"] == True:
        await bot._ws.send_privmsg(os.environ['CHANNEL'], f"/me " + repeater["messages"][n])
        n = 1
        if n >= len(repeater["messages"]):
            n = 0
    while True:
        await asyncio.sleep(repeater["s"])
        await bot._ws.send_privmsg(os.environ['CHANNEL'], f"/me " + repeater["messages"][n])
        n = n+1
        if n >= len(repeater["messages"]):
            n = 0