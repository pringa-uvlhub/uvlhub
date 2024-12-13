import discord


def get_introduction_embed():
    # Crear el embed de introducción
    embed = discord.Embed(
        title="Welcome to uvlhub!",
        description=(
            "Hello, I am **pringa_bot**, a uvlhub assistant bot. "
            "I can help you find and download datasets, and much more!\n\n"
            "**What is uvlhub?**\n"
            "uvlhub is a complete repository for feature models in UVL format, "
            "integrated with Zenodo for data storage and flamapy for advanced model analysis. "
            "It supports Open Science principles and facilitates "
            "collaboration among researchers and developers.\n\n"
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

    return embed
