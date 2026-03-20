import discord
from discord.ext import commands
from discord import app_commands
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import aiohttp
import io
import os

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
intents.message_content = False

bot = commands.Bot(command_prefix="!", intents=intents)


# --------------------------
# EVENTO ON_READY
# --------------------------

@bot.event
async def on_ready():
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
# INICIAR O BOT
# --------------------------

bot.run(os.getenv("TOKEN"))
