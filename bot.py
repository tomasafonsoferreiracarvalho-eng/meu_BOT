import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import io
import os
import json
import time
import random

# --------------------------
# CONFIGURAÇÕES
# --------------------------

GUILD_ID = 1483763424524501105

# Cargos
VISITANTE_ID = 1483790734279577650
LEI_ID = 1483775243859394560
DTAG_ID = 1483781348253503578
TPSI_ID = 1483781578110009398
TQ_ID = 1483781848164466870
GE_ID = 1483782119841992817
GRHCO_ID = 1483787961060294747
CR_ID = 1483788147706822667
ELETRO_ID = 1483788942322176010
TGPC_ID = 1483789143753363568
CONTABILIDADE_ID = 1483789347718168688
EC_ID = 1483790725102436363
IG_ID = 1483889520096317541
MD_ID = 1483889977283711026

# Anos
ANO1_ID = 1484567602830250044
ANO2_ID = 1484567828085604443
ANO3_ID = 1484567870280302772
ANO4_ID = 1484567905067864207
ANO5_ID = 1484567933635006484
ANO6_ID = 1484567968477220944
ANONAO_ID = 1484568002396688545

WELCOME_CHANNEL_ID = 1483763425296515155

# --------------------------
# BOT + INTENTS
# --------------------------

intents = discord.Intents.default()
intents.members = True
intents.message_content = True  # para o on_message funcionar bem

bot = commands.Bot(command_prefix="!", intents=intents)

# --------------------------
# SISTEMA DE XP E NÍVEIS
# --------------------------

MAX_LEVEL = 100
DATA_FILE = "xp_data.json"

# Estrutura: { user_id: {"xp": int, "level": int} }
user_data = {}

def load_data():
    global user_data
    try:
        with open(DATA_FILE, "r") as f:
            user_data = json.load(f)
    except FileNotFoundError:
        user_data = {}

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def xp_needed(level):
    return int(50 * (level ** 1.5) + 100)

xp_cooldown = {}
COOLDOWN_SECONDS = 10

# --------------------------
# EVENTO ON_READY
# --------------------------

@bot.event
async def on_ready():
    load_data()
    print(f"Bot ligado como {bot.user}")
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f"Slash commands sincronizados: {len(synced)}")
    except Exception as e:
        print("Erro ao sincronizar:", e)

# --------------------------
# BOAS-VINDAS COM IMAGEM
# --------------------------

async def gerar_boas_vindas(member):
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url

    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avatar_bytes = await resp.read()

    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

    img = Image.new("RGBA", (900, 450), (0, 0, 0, 0))
    grad = Image.new("RGBA", (900, 450))
    draw_grad = ImageDraw.Draw(grad)

    for i in range(450):
        cor = (
            int(40 + (i / 450) * 20),
            int(180 - (i / 450) * 80),
            int(120 + (i / 450) * 120),
            255
        )
        draw_grad.line([(0, i), (900, i)], fill=cor)

    img.paste(grad, (0, 0))

    mask = Image.new("L", (900, 450), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([(0, 0), (900, 450)], radius=40, fill=255)
    img.putalpha(mask)

    draw = ImageDraw.Draw(img)

    draw.rounded_rectangle([(20, 280), (880, 430)], radius=30, fill=(0, 0, 0, 150))

    texto = (
        f"Olá {member.name}, chegaste de paraquedas então!\n"
        f"Bem-vindo ao {member.guild.name}! Usa e abusa!"
    )

    font = ImageFont.truetype("arial.ttf", 32)
    draw.text((40, 310), texto, font=font, fill=(255, 255, 255))

    avatar_circ = avatar.resize((200, 200))
    mask_avatar = Image.new("L", (200, 200), 0)
    draw_avatar = ImageDraw.Draw(mask_avatar)
    draw_avatar.ellipse((0, 0, 200, 200), fill=255)

    img.paste(avatar_circ, (650, 60), mask_avatar)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer

@bot.event
async def on_member_join(member):
    canal = bot.get_channel(WELCOME_CHANNEL_ID)
    if canal is None:
        return

    imagem = await gerar_boas_vindas(member)

    await canal.send(
        content=f"👋 **Bem-vindo, {member.mention}!**",
        file=discord.File(imagem, filename="welcome.png")
    )

# --------------------------
# MENU DE CURSOS
# --------------------------

class CursoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="LEI", value="lei"),
            discord.SelectOption(label="DTAG", value="dtag"),
            discord.SelectOption(label="TPSI", value="tpsi"),
            discord.SelectOption(label="TQ", value="tq"),
            discord.SelectOption(label="GE", value="ge"),
            discord.SelectOption(label="GRHCO", value="grhco"),
            discord.SelectOption(label="CR", value="cr"),
            discord.SelectOption(label="Eletro", value="eletro"),
            discord.SelectOption(label="TGPC", value="tgpc"),
            discord.SelectOption(label="Contabilidade", value="contabilidade"),
            discord.SelectOption(label="EC", value="ec"),
            discord.SelectOption(label="IG", value="ig"),
            discord.SelectOption(label="MD", value="md"),
        ]

        super().__init__(
            placeholder="Escolhe o teu curso",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="curso_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        visitante = guild.get_role(VISITANTE_ID)

        roles_map = {
            "lei": guild.get_role(LEI_ID),
            "dtag": guild.get_role(DTAG_ID),
            "tpsi": guild.get_role(TPSI_ID),
            "tq": guild.get_role(TQ_ID),
            "ge": guild.get_role(GE_ID),
            "grhco": guild.get_role(GRHCO_ID),
            "cr": guild.get_role(CR_ID),
            "eletro": guild.get_role(ELETRO_ID),
            "tgpc": guild.get_role(TGPC_ID),
            "contabilidade": guild.get_role(CONTABILIDADE_ID),
            "ec": guild.get_role(EC_ID),
            "ig": guild.get_role(IG_ID),
            "md": guild.get_role(MD_ID),
        }

        escolha = self.values[0]
        role = roles_map.get(escolha)

        if role is None:
            await interaction.response.send_message("Erro ao encontrar o cargo.", ephemeral=True)
            return

        if visitante in member.roles:
            await member.remove_roles(visitante)

        for r in roles_map.values():
            if r in member.roles and r != role:
                await member.remove_roles(r)

        await member.add_roles(role)

        await interaction.response.send_message(
            f"Curso definido para **{role.name}**. Bem-vindo!", ephemeral=True
        )

class CursoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CursoSelect())

@bot.tree.command(name="cursos", description="Envia o menu de escolha de curso", guild=discord.Object(id=GUILD_ID))
async def cursos(interaction: discord.Interaction):
    view = CursoView()
    await interaction.response.send_message(
        "Escolhe o teu curso para entrares no servidor:",
        view=view
    )

# --------------------------
# MENU DE ANOS
# --------------------------

class AnoSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1º Ano", value="ano1"),
            discord.SelectOption(label="2º Ano", value="ano2"),
            discord.SelectOption(label="3º Ano", value="ano3"),
            discord.SelectOption(label="4º Ano", value="ano4"),
            discord.SelectOption(label="5º Ano", value="ano5"),
            discord.SelectOption(label="6º Ano", value="ano6"),
            discord.SelectOption(label="Não te interessa o meu ano", value="nao"),
        ]

        super().__init__(
            placeholder="Escolhe o teu ano",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ano_select"
        )

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user

        roles_map = {
            "ano1": guild.get_role(ANO1_ID),
            "ano2": guild.get_role(ANO2_ID),
            "ano3": guild.get_role(ANO3_ID),
            "ano4": guild.get_role(ANO4_ID),
            "ano5": guild.get_role(ANO5_ID),
            "ano6": guild.get_role(ANO6_ID),
            "nao": guild.get_role(ANONAO_ID),
        }

        escolha = self.values[0]
        role = roles_map.get(escolha)

        if role is None:
            await interaction.response.send_message("Erro ao encontrar o cargo.", ephemeral=True)
            return

        for r in roles_map.values():
            if r in member.roles and r != role:
                await member.remove_roles(r)

        await member.add_roles(role)

        await interaction.response.send_message(
            f"Ano definido para **{role.name}**.", ephemeral=True
        )

class AnoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(AnoSelect())

@bot.tree.command(name="anos", description="Escolhe o teu ano", guild=discord.Object(id=GUILD_ID))
async def anos(interaction: discord.Interaction):
    view = AnoView()
    await interaction.response.send_message(
        "Escolhe o teu ano:",
        view=view
    )

# --------------------------
# SISTEMA DE XP: ON_MESSAGE
# --------------------------

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)
    now = time.time()

    # Cooldown anti-spam
    if user_id in xp_cooldown and now - xp_cooldown[user_id] < COOLDOWN_SECONDS:
        return

    xp_cooldown[user_id] = now

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}

    xp_gain = random.randint(5, 15)
    user_data[user_id]["xp"] += xp_gain

    xp_total = user_data[user_id]["xp"]
    level = user_data[user_id]["level"]

    if level < MAX_LEVEL and xp_total >= xp_needed(level):
        user_data[user_id]["level"] += 1
        user_data[user_id]["xp"] = 0

        await message.channel.send(
            f"🎉 **{message.author.display_name} subiu para o nível {level + 1}!**"
        )

    save_data()
    await bot.process_commands(message)

# --------------------------
# /rank — CARTÃO VISUAL
# --------------------------

@bot.tree.command(name="rank", description="Mostra o teu cartão de nível", guild=discord.Object(id=GUILD_ID))
async def rank(interaction: discord.Interaction):
    user_id = str(interaction.user.id)

    if user_id not in user_data:
        user_data[user_id] = {"xp": 0, "level": 1}

    xp = user_data[user_id]["xp"]
    level = user_data[user_id]["level"]
    xp_next = xp_needed(level)

    # Criar imagem base
    card = Image.new("RGB", (600, 200), (30, 30, 30))
    draw = ImageDraw.Draw(card)

    # Avatar
    avatar_url = interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url
    async with aiohttp.ClientSession() as session:
        async with session.get(avatar_url) as resp:
            avatar_bytes = await resp.read()
    avatar = Image.open(io.BytesIO(avatar_bytes)).resize((150, 150))
    card.paste(avatar, (25, 25))

    # Texto
    font = ImageFont.truetype("arial.ttf", 24)
    draw.text((200, 40), f"{interaction.user.display_name}", fill="white", font=font)
    draw.text((200, 80), f"Nível: {level}/{MAX_LEVEL}", fill="white", font=font)
    draw.text((200, 120), f"XP: {xp}/{xp_next}", fill="white", font=font)

    # Barra de progresso
    progress = int((xp / xp_next) * 300) if xp_next > 0 else 0
    draw.rectangle((200, 160, 200 + progress, 180), fill=(0, 200, 255))

    buffer = io.BytesIO()
    card.save(buffer, format="PNG")
    buffer.seek(0)

    await interaction.response.send_message(file=discord.File(buffer, "rank.png"))

# --------------------------
# /ranktop10 — TOP 10
# --------------------------

@bot.tree.command(name="ranktop10", description="Mostra o top 10 global", guild=discord.Object(id=GUILD_ID))
async def ranktop10(interaction: discord.Interaction):

    if not user_data:
        await interaction.response.send_message("Ainda não há dados de XP.", ephemeral=True)
        return

    top = sorted(
        user_data.items(),
        key=lambda x: (x[1]["level"], x[1]["xp"]),
        reverse=True
    )[:10]

    embed = discord.Embed(
        title="🏆 Top 10 — Ranking Global",
        color=0xffd700
    )

    pos = 1
    for uid, data in top:
        user = interaction.guild.get_member(int(uid))
        nome = user.display_name if user else f"User {uid}"
        embed.add_field(
            name=f"#{pos} — {nome}",
            value=f"Nível {data['level']} • {data['xp']} XP",
            inline=False
        )
        pos += 1

    await interaction.response.send_message(embed=embed)

# --------------------------
# INICIAR O BOT
# --------------------------

bot.run(os.getenv("TOKEN"))