import datetime
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


def get_info_datasets():
    embed = discord.Embed(
        title="Managing Datasets in UVLHub",
        description=(
            "UVLHub allows you to upload, store, and analyze your UVL models. All datasets are backed \
            up with Zenodo, ensuring data permanence and integrity.\n\n"
            "Steps to manage your datasets:\n"
            "1. Upload UVL models via the web app.\n"
            "2. Store related metadata like title, authors, and tags.\n"
            "3. Analyze models with integrated tools like Flamapy.\n"
            "4. Datasets are assigned a DOI for reference and retrieval via Zenodo.\n\n"
            "Resources:\n"
            "- [UVLHub Documentation](https://docs.uvlhub.io/)\n"
            "- [Zenodo Repository](https://zenodo.org/)"
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
    return embed


def get_info_uvl():
    embed = discord.Embed(
        title="Universal Variability Language (UVL)",
        description=(
            "UVL is a standardized language for representing variability models with a tree-like structure. \
            You can use concepts like mandatory, optional, or, alternative features, \
            and cross-tree constraints to build complex models.\n\n"
            "Here's a simple example:\n"
            "```\n"
            "features\n"
            "  Sandwich\n"
            "    mandatory\n"
            "      Bread\n"
            "    optional\n"
            "      Sauce\n"
            "        alternative\n"
            "          Ketchup\n"
            "          Mustard\n"
            "constraints\n"
            "  Ketchup => Cheese\n"
            "```\n"
            "Learn more about the core and advanced language levels in our \
                [UVL Documentation](https://universal-variability-language.github.io/). \n"
            "Want to tryout UVL yourself? Check [UVL playground](https://uvl.uni-ulm.de/)"
            ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
    return embed


def get_info_communities():
    embed = discord.Embed(
        title="What are Communities in uvlhub?",
        description=(
            "Communities in uvlhub are groups of users that share common interests. "
            "Registered users can create and join these communities to collaborate, "
            "discuss, and share knowledge. Some examples of popular communities include:\n\n"
            "**Open Source Enthusiasts**: Developers passionate about open source projects.\n"
            "**AI Researchers**: A group dedicated to advancements in AI and machine learning.\n"
            "**Scientific Community**: Researchers collaborating on scientific breakthroughs and papers.\n\n"
            "Each community has a creator and a manager, and members can contribute by sharing content and "
            "engaging in discussions related to their common interests."
        ),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
    embed.add_field(name="Creating Communities", value="Any registered user can create a new community.")
    embed.add_field(name="Managing Communities", value="The creator or manager oversees the community activities.")
    embed.add_field(name="Joining Communities",
                    value="Users can browse and join communities that align with their interests.")
    return embed


def get_info_zenodo():
    embed = discord.Embed(
        title="Zenodo and UVLHub Integration",
        description=(
            "Zenodo is a general-purpose open repository developed by CERN. It allows researchers \
            to share and preserve their datasets, software, and other digital research outputs. "
            "All datasets stored in UVLHub are backed up by Zenodo, \
                ensuring long-term preservation and accessibility.\n\n"
            "**Benefits of Zenodo in UVLHub:**\n"
            "✅ Permanent storage for all uploaded UVL models.\n"
            "✅ Each dataset is assigned a DOI for academic citation and referencing.\n"
            "✅ Supports Open Science principles, facilitating collaboration and data sharing among researchers.\n\n"
            "By integrating with Zenodo, UVLHub ensures that your data remains accessible and safe for future use."
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


def get_help():
    embed = discord.Embed(
        title="What commands can you use with Pringa bot in UVLHub?",
        description=("""
            **Available Commands:**

            **Text Commands**:
            - `ping`: Responds with "Pong!" to check if the bot is working.
            - `test`: Responds with "¡Estoy funcionando!" to confirm the bot's functionality.

            **Slash Commands**:
            - `/introduction`: Shows an introduction to UVLHub and commands to get started.
            - `/info_datasets`: Learn how to manage datasets in UVLHub.
            - `/info_uvl`: Learn the basics of UVL and how to create variability models.
            - `/info_communities`: Provides information about communities in UVLHub.
            - `/info_zenodo`: Learn about Zenodo and its integration with UVLHub.
            - `/list_datasets`: List all synchronized datasets.
            - `/list_communities`: List all available communities.
            - `/filter_datasets`: Filter datasets based on various criteria.
            - `/filter_communities`: Filter communities by name or description.

            Use `/` before a command to run slash commands or `!` to run text commands.
            """),
        color=discord.Color.red()
    )
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
    return embed


def download_embed(desc, title="Download Dataset of UVLHUb", name=None, field_desc=None, thumbnail=False):  
    embed = discord.Embed(
        title="Download Dataset of UVLHUb",
        description=desc,
        timestamp=datetime.datetime.now(),
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")

    return embed