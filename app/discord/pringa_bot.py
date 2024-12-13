import discord
import app
import os

from discord.ext import commands
from app.discord.embeds import get_introduction_embed, get_dataset_embed, get_info_datasets
from discord.ui import View


async def paginate(interaction, embeds, timeout=60):
    """
    Función para paginar contenido con botones.
    - interaction: La interacción del comando de Discord.
    - embeds: Lista de embeds a paginar.
    - timeout: Tiempo en segundos para esperar por la respuesta (por defecto 60s).
    """
    current_page = 0
    total_pages = len(embeds)

    embed = embeds[current_page]
    embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")

    # Crear el mensaje inicial con un embed
    await interaction.response.send_message(embed=embed, view=PaginatorView(embeds, current_page, total_pages))


class PaginatorView(View):
    def __init__(self, embeds, current_page, total_pages):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = current_page
        self.total_pages = total_pages
        self.update_buttons()

    async def update_page(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page]
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")
        self.update_buttons()
        await interaction.response.edit_message(embed=embed, view=self)

    def update_buttons(self):
        # Deshabilitar el botón "Anterior" si estamos en la primera página
        self.children[0].disabled = self.current_page == 0
        # Deshabilitar el botón "Siguiente" si estamos en la última página
        self.children[1].disabled = self.current_page == self.total_pages - 1

    @discord.ui.button(label="◀️ Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.Button):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_page(interaction)

    @discord.ui.button(label="▶️ Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await self.update_page(interaction)

    async def on_timeout(self):
        """Deshabilitar botones después de que se haya agotado el tiempo de espera."""
        for button in self.children:
            button.disabled = True
        if self.message:
            await self.message.edit(view=self)


def start_bot():
    from app.modules.dataset.services import DataSetService
    from app.modules.community.services import CommunityService
    from app.modules.explore.services import ExploreService
    app_create = app.create_app()

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
        embed = get_introduction_embed()
        # Enviar el embed en la respuesta al slash command
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="info_datasets", description="Learn how to manage datasets in UVLHub.")
    async def info_datasets(interaction: discord.Interaction):
        embed = get_info_datasets()
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="list_datasets", description="List all synchronized datasets.")
    async def list_datasets(interaction: discord.Interaction):
        try:
            with app_create.app_context():
                dataset_service = DataSetService()
                datasets = dataset_service.all_synchronized()

                if not datasets:
                    await interaction.response.send_message("No datasets found.")
                    return

                embeds = [get_dataset_embed(dataset) for dataset in datasets]

                # Llamar a la función de paginación
                await paginate(interaction, embeds)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error listing datasets: {str(e)}")
            else:
                await interaction.followup.send(f"Error listing datasets: {str(e)}")

    @bot.tree.command(name="list_communities", description="List all available communities.")
    async def list_communities(interaction: discord.Interaction):
        try:
            with app_create.app_context():
                community_service = CommunityService()
                communities = community_service.get_all_communities()

                if not communities:
                    await interaction.response.send_message("No communities found.")
                    return

                # Crear una lista de embeds
                embeds = []
                for community in communities:
                    embed = discord.Embed(
                        title=f"Community: {community.name}",
                        description=f"{community.description}",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Created at:",
                                    value=community.created_at.strftime('%B %d, %Y at %I:%M %p'), inline=False)
                    embed.add_field(name="Created by:", value=str(community.created_by_id), inline=False)
                    embed.add_field(name="Admin ID:", value=str(community.admin_by_id), inline=False)
                    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")

                    embeds.append(embed)

                # Llamar a la función de paginación
                await paginate(interaction, embeds)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error listing communities: {str(e)}")
            else:
                await interaction.followup.send(f"Error listing communities: {str(e)}")

    @bot.tree.command(name="filter_datasets", description="Filter datasets based on various criteria.")
    async def filter_datasets(
        interaction: discord.Interaction,
        query: str = "",
        query_author: str = "",
        query_tag: str = "",
        query_features: str = "",
        query_models: str = "",
        sorting: str = "newest",
        publication_type: str = "any"
    ):
        try:
            with app_create.app_context():
                # Llama al método de filtrado con los parámetros corregidos
                datasets = ExploreService().filter(query=query,
                                                   queryAuthor=query_author,
                                                   queryTag=query_tag,
                                                   queryFeatures=query_features,
                                                   queryModels=query_models,
                                                   sorting=sorting,
                                                   publication_type=publication_type
                                                   )

                if not datasets:
                    await interaction.response.send_message("No datasets matched the criteria.")
                    return

                # Crear una lista de embeds
                embeds = [get_dataset_embed(dataset) for dataset in datasets]

                # Llamar a la función de paginación
                await paginate(interaction, embeds)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error filtering datasets: {str(e)}")
            else:
                await interaction.followup.send(f"Error filtering datasets: {str(e)}")

    @bot.tree.command(name="filter_communities", description="Filter communities by name or description.")
    async def filter_communities(interaction: discord.Interaction, query: str):
        try:
            with app_create.app_context():
                community_service = CommunityService()
                communities = community_service.filter_communities(query)

                if not communities:
                    await interaction.response.send_message(f"No communities found for query: '{query}'.")
                    return

                # Crear una lista de embeds para mostrar los resultados
                embeds = []
                for community in communities:
                    embed = discord.Embed(
                        title=f"Community: {community.name}",
                        description=f"{community.description}",
                        color=discord.Color.purple()
                    )
                    embed.add_field(name="Created at:",
                                    value=community.created_at.strftime('%B %d, %Y at %I:%M %p'), inline=False)
                    embed.add_field(name="Created by:", value=str(community.created_by_id), inline=False)
                    embed.add_field(name="Admin ID:", value=str(community.admin_by_id), inline=False)
                    embed.set_thumbnail(url="https://www.uvlhub.io/static/img/icons/icon-250x250.png")
                    embeds.append(embed)

                # Llamar a la función de paginación para mostrar los resultados
                await paginate(interaction, embeds)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error filtering communities: {str(e)}")
            else:
                await interaction.followup.send(f"Error filtering communities: {str(e)}")

    # Función para correr el bot
    def run_discord_bot():
        bot.run(token)

    run_discord_bot()
