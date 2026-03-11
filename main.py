import discord
from discord.ext import commands

import os
import sys

from dotenv import load_dotenv
import asyncio

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=">", intents=intents)

# bot está online
@bot.event
async def on_ready():
    print(f"Bot {bot.user} está online!")

# hello world
@bot.command()
async def axolotl(ctx):
    await ctx.send("Hello World!")

# restart
@bot.command()
@commands.is_owner()
async def restart(ctx):
    await bot.close()  # fecha o bot corretamente antes de reiniciar
    os.execv(sys.executable, [sys.executable] + sys.argv)
# latencia
@bot.command()
async def ping(ctx):
    await ctx.send(f'pong!: {round(bot.latency*1000)}ms')


async def load_extensions():
    await bot.load_extension("cogs.auto_response")
    await bot.load_extension("cogs.jogos")
    await bot.load_extension("cogs.niveis")
    await bot.load_extension("cogs.tickets")

    async def main():
        async with bot:
            # carrega as cogs aqui
            await bot.start(TOKEN)

asyncio.run(load_extensions())

bot.run(TOKEN)