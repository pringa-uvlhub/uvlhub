import discord
from discord.ext import commands
import os


def start_bot():
    token = os.getenv("DISCORD_TOKEN")
    intents = discord.Intents.all()
    intents.message_content = True
    # Crear el bot con el prefijo '!' y los intents definidos
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f'Bot conectado como {bot.user}')
        try:
            synced = await bot.tree.sync()
            print(f'Successfully synced {len(synced)} slash commands.')
        except Exception as e:
            print(f'Failed to sync commands: {e}')

    @bot.command(name='ping')
    async def ping(ctx):
        await ctx.send('Pong!')

    @bot.command(name='test')
    async def test(ctx):
        await ctx.send('¡Estoy funcionando!')

    @bot.tree.command(name="introduction", description="Shows an introduction to uvlhub and commands to get started.")
    async def introduction(interaction: discord.Interaction):
        # Crear el embed de introducción
        embed = discord.Embed(
            title="Welcome to uvlhub!",
            description=(
                "Hello, I am **pringa_bot**, a uvlhub assistant bot. \
                    I can help you find and download datasets, and much more!\n\n"
                "**What is uvlhub?**\n"
                "uvlhub is a complete repository for feature models in UVL format, \
                    integrated with Zenodo for data storage and flamapy for advanced model analysis. "
                "It supports Open Science principles and facilitates \
                    collaboration among researchers and developers.\n\n"
                "**Bot Functions:**\n"
                "✅ Dataset search\n"
                "✅ Dataset download\n"
                "✅ Helping commands\n"
                "✅ And much more...\n\n"
                "Keep exploring to discover how uvlhub can optimize your workflow!"
            ),
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
        # Enviar el embed en la respuesta al slash command
        await interaction.response.send_message(embed=embed)

    # Función para correr el bot
    def run_discord_bot():
        bot.run(token)

    run_discord_bot()
