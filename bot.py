import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from dateutil import parser as dateparser

# Carregar variáveis de ambiente
load_dotenv()
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
API_URL = os.environ.get('QUOTES_API_URL')

if not DISCORD_TOKEN:
    raise RuntimeError("Defina a variável de ambiente DISCORD_TOKEN.")

# Bot + intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Formatador de quote
def format_quote(data: dict):
    msg = data.get("message", "").replace("<br>", "\n")
    created_at = data.get("created_at")
    footer_parts = []

    if created_at:
        try:
            dt = dateparser.parse(created_at)
            footer_parts.append(f"Criado em: {dt.strftime('%d/%m/%Y')}")
        except Exception:
            footer_parts.append(f"Criado em: {created_at}")

    if author := data.get("author"):
        footer_parts.append(f"por {author}")
    if table := data.get("table"):
        footer_parts.append(f"em {table}")

    return msg, " • ".join(footer_parts)

# Slash command: /quote
@bot.tree.command(name="quote", description="Mostra uma quote aleatória")
async def quote_random(interaction: discord.Interaction):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/quote_random.php") as res:
            if res.status != 200:
                await interaction.response.send_message("Erro ao buscar quote aleatória.", ephemeral=True)
                return
            data = await res.json()

    desc, footer = format_quote(data)
    embed = discord.Embed(description=desc, color=discord.Color.blurple())
    embed.set_author(name=f"Quote #{data.get('id')}")
    if footer:
        embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed)

# Slash command: /quote_id
@bot.tree.command(name="quote_id", description="Busca uma quote pelo ID")
@app_commands.describe(quote_id="ID numérico da quote")
async def quote_id(interaction: discord.Interaction, quote_id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/quote_id.php?id={quote_id}") as res:
            if res.status != 200:
                await interaction.response.send_message(f"Quote {quote_id} não encontrada.", ephemeral=True)
                return
            data = await res.json()

    desc, footer = format_quote(data)
    embed = discord.Embed(description=desc, color=discord.Color.green())
    embed.set_author(name=f"Quote #{data.get('id')}")
    if footer:
        embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed)

# Slash command: /quote_add
@bot.tree.command(name="quote_add", description="Adiciona uma nova quote")
@app_commands.describe(message="Texto da quote")
async def quote_add(interaction: discord.Interaction, message: str):
    payload = {
        "message": message.replace("\n", "<br>"),
        "table": None,
        "author": interaction.user.display_name,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{API_URL}/quote_add.php", json=payload) as res:
            if res.status != 200:
                await interaction.response.send_message("Erro ao adicionar quote.", ephemeral=True)
                return
            data = await res.json()

    # Buscar a quote adicionada
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_URL}/quote_id.php?id={data.get('id')}") as res:
            quote_data = await res.json()

    desc, footer = format_quote(quote_data)
    embed = discord.Embed(description=desc, color=discord.Color.purple())
    embed.set_author(name=f"Quote #{quote_data.get('id')}")
    if footer:
        embed.set_footer(text=footer)
    await interaction.response.send_message(embed=embed)

# Sincroniza comandos
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot online como {bot.user}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)