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


def get_dataset_embed(dataset):
    """
    Crea un embed para un dataset proporcionado.
    - dataset: El dataset para el que se generará el embed.
    """
    metadata = dataset.ds_meta_data
    embed = discord.Embed(
        title=f"Dataset: {dataset.name()}",
        description=f"{metadata.description}",
        color=discord.Color.green()
    )
    embed.add_field(name="Publication type:",
                    value=dataset.get_cleaned_publication_type(), inline=False)
    embed.add_field(name="Created at: ",
                    value=dataset.created_at.strftime('%B %d, %Y at %I:%M %p'), inline=False)
    embed.add_field(name="Publication DOI: ", value=dataset.get_uvlhub_doi(), inline=False)

    tags = (', '.join(tag.strip() for tag in metadata.tags.split(','))
            if metadata.tags else 'No tags available')
    embed.add_field(name="Tags: ", value=tags, inline=False)
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")

    return embed
