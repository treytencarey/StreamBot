from twitchio.ext import commands
import os
import asyncio


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            irc_token=os.environ['TMI_TOKEN'],
            client_id=os.environ['CLIENT_ID'],
            nick=os.environ['BOT_NICK'],
            prefix=os.environ['BOT_PREFIX'],
            initial_channels=[os.environ['CHANNEL']]
        )

    # Events don't need decorators when subclassed
    async def event_ready(self):
        print(f'Ready | {self.nick}')
        
        from repeatMessages import repeatMessages
        asyncio.ensure_future(repeatMessages(bot))

    async def event_message(self, message):
        print(message.content)
        await self.handle_commands(message)

    @commands.command(name='draw')
    async def draw(self, ctx):
        from draw import gameMain
        await gameMain(ctx)
        
    @commands.command(name='ttt')
    async def tictactoe(self, ctx):
        from tictactoe import gameMain
        asyncio.ensure_future(gameMain(ctx))
        
    @commands.command(name='discord')
    async def discord(self, ctx):
        await ctx.send('Hey, @' + ctx.author.name + '! Find our Discord using link https://discord.gg/TAfxrBzHv8')
        
    @commands.command(name='charity')
    async def charity(self, ctx):
        await ctx.send('Hey, @' + ctx.author.name + '! Contribute to our charity event (for The Trevor Project) using link https://streamlabscharity.com/@4feetapart/the-trevor-project')

    @commands.command(name='commands')
    async def commands(self, ctx):
        await ctx.send('Hey, @' + ctx.author.name + '! Here\'s a list of available commands:')
        await ctx.send('Tic-Tac-Toe: !ttt help')
        await ctx.send('Discord: !discord')
        await ctx.send('Charity event: !charity')

bot = Bot()
bot.run()