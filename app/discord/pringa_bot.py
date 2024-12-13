import discord
import app
import os

from discord.ext import commands
from app.discord.embeds import get_introduction_embed
from discord.ui import View


async def paginate(interaction, embeds, timeout=60):
    """
    Función para paginar contenido con botones.
    - interaction: La interacción del comando de Discord.
    - embeds: Lista de embeds a paginar.
    - timeout: Tiempo en segundos para esperar por la respuesta (por defecto 60s).
    """
    current_page = 0
    embed = embeds[current_page]

    # Crear el mensaje inicial con un embed
    await interaction.response.send_message(embed=embed, view=PaginatorView(embeds, current_page))


class PaginatorView(View):
    def __init__(self, embeds, current_page):
        super().__init__(timeout=60)
        self.embeds = embeds
        self.current_page = current_page

    async def update_page(self, interaction: discord.Interaction):
        embed = self.embeds[self.current_page]
        await interaction.response.edit_message(embed=embed, view=self)

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

    @bot.tree.command(name="list_datasets", description="List all synchronized datasets.")
    async def list_datasets(interaction: discord.Interaction):
        try:
            with app_create.app_context():
                dataset_service = DataSetService()
                datasets = dataset_service.all_synchronized()

                if not datasets:
                    await interaction.response.send_message("No datasets found.")
                    return

                # Crear una lista de embeds
                embeds = []
                for dataset in datasets:
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
                    embeds.append(embed)

                # Llamar a la función de paginación
                await paginate(interaction, embeds)

        except Exception as e:
            if not interaction.response.is_done():
                await interaction.response.send_message(f"Error listing datasets: {str(e)}")
            else:
                await interaction.followup.send(f"Error listing datasets: {str(e)}")

    # Función para correr el bot
    def run_discord_bot():
        bot.run(token)

    run_discord_bot()
