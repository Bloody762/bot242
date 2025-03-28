import discord
from discord import app_commands
from discord.ext import commands
import psutil
from datetime import datetime
from discord import app_commands, Embed
import random
import string
import json
import os
from discord.ui import Select, View
import asyncio
import re
from collections import defaultdict
import random
import sys
import time
import platform
import requests
from discord.ui import Button, View

command_usage = defaultdict(int)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Lista negra (almacena los IDs de los usuarios)
blacklist = []
# Lista blanca (almacena los IDs de los usuarios)
whitelist = []

# Verifica si el usuario está en la whitelist
def is_whitelisted(user_id):
    return str(user_id) in whitelist

# Evento cuando el bot se conecta
@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f'Se han sincronizado {len(synced)} comandos de barra.')
    except Exception as e:
        print(f'Error al sincronizar comandos: {e}')



    


# Comando Nuke 💥

import discord
from discord import app_commands
from discord.ext import commands

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

# Comando Status 📊
@bot.tree.command(name="status", description="Muestra el estado del bot")
async def status(interaction: discord.Interaction):
    server_count = len(bot.guilds)
    member_count = sum(guild.member_count for guild in bot.guilds)

    embed = discord.Embed(
        title="📊 Estado del Bot",
        description="Información actual del bot",
        color=discord.Color.red()  # Rojo
    )
    embed.add_field(name="🌍 Servidores", value=f"{server_count}", inline=True)
    embed.add_field(name="👥 Miembros Totales", value=f"{member_count}", inline=True)
    embed.set_footer(text=f"Solicitado por {interaction.user.name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    await interaction.response.send_message(embed=embed)

# Archivo donde se guardará la blacklist
BLACKLIST_FILE = "blacklist.json"

# Cargar la blacklist desde el archivo
try:
    with open(BLACKLIST_FILE, "r") as f:
        blacklist = list(json.load(f))
except (FileNotFoundError, json.JSONDecodeError):
    blacklist = []

# Crear instancia del bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Guardar la blacklist en un archivo
def save_blacklist():
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(blacklist, f, indent=4)

# Función para banear al usuario en todos los servidores
async def ban_global(user_id: int, reason: str):
    for guild in bot.guilds:
        try:
            user = guild.get_member(user_id)
            if user:
                await guild.ban(user, reason=reason, delete_message_days=0)
                print(f"✅ Usuario {user} ({user_id}) baneado en {guild.name}")
            else:
                print(f"⚠️ El usuario con ID {user_id} no está en {guild.name}, pero será baneado si se une.")
        except discord.Forbidden:
            print(f"❌ No tengo permisos para banear en {guild.name}.")
        except Exception as e:
            print(f"⚠️ Error al intentar banear en {guild.name}: {e}")

# Comando para añadir un usuario a la blacklist y banearlo globalmente
@bot.tree.command(name="blacklist_add", description="Añadir a un usuario a la lista negra y banearlo globalmente")
async def blacklist_add(interaction: discord.Interaction, user_id: str, reason: str):
    try:
        user_id = int(user_id)
        if user_id not in blacklist:
            blacklist.append(user_id)
            save_blacklist()
            await ban_global(user_id, reason)
            
            embed = discord.Embed(title="🚫 Usuario Baneado Globalmente", color=discord.Color.gold())
            embed.add_field(name="ID de Usuario:", value=str(user_id))
            embed.add_field(name="Razón:", value=reason)
            embed.set_footer(text="Este ban es global, no puede eludirlo.")
            
            await interaction.response.send_message(embed=embed)
            
            for guild in bot.guilds:
                general_channel = discord.utils.get(guild.text_channels, name="general")
                if general_channel:
                    try:
                        await general_channel.send(embed=embed)
                    except discord.Forbidden:
                        print(f"⚠️ No puedo enviar mensajes en {guild.name}.")
        else:
            await interaction.response.send_message("⚠️ El usuario ya está en la lista negra.")
    except ValueError:
        await interaction.response.send_message("❌ ID de usuario inválido.")
    except Exception as e:
        print(f"⚠️ Error en blacklist_add: {e}")
        await interaction.response.send_message("❌ Ocurrió un error inesperado.")

# Comando para quitar de la blacklist
@bot.tree.command(name="blacklist_remove", description="Remueve un usuario de la lista negra")
async def blacklist_remove(interaction: discord.Interaction, user_id: str):
    try:
        user_id = int(user_id)
        if user_id in blacklist:
            blacklist.remove(user_id)
            save_blacklist()
            await interaction.response.send_message(f"✅ El usuario con ID {user_id} ha sido removido de la lista negra.")
        else:
            await interaction.response.send_message(f"⚠️ El usuario con ID {user_id} no está en la lista negra.")
    except ValueError:
        await interaction.response.send_message("❌ ID de usuario inválido.")
    except Exception as e:
        print(f"⚠️ Error en blacklist_remove: {e}")
        await interaction.response.send_message("❌ Ocurrió un error inesperado.")

# Comando para ver la blacklist
@bot.tree.command(name="blacklist_list", description="Muestra la lista de usuarios baneados globalmente")
async def blacklist_list(interaction: discord.Interaction):
    if blacklist:
        blacklist_str = "\n".join(str(user_id) for user_id in blacklist)
        embed = discord.Embed(title="📜 Lista de usuarios baneados globalmente", color=discord.Color.red())
        embed.add_field(name="Usuarios:", value=blacklist_str, inline=False)
    else:
        embed = discord.Embed(title="✅ No hay usuarios en la lista negra", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)


# Evento que banea a los usuarios en la blacklist cuando se unen
@bot.event
async def on_member_join(member):
    if member.id in blacklist:
        try:
            await member.ban(reason="Usuario en la lista negra global.")
            print(f"🔴 Usuario {member.name} ({member.id}) baneado al intentar unirse.")
        except discord.Forbidden:
            print(f"❌ No tengo permisos para banear a {member.name} ({member.id}) en {member.guild.name}.")
        except Exception as e:
            print(f"⚠️ Error en on_member_join: {e}")

# Nuke

@bot.tree.command(name="nuke", description="💥 Elimina todos los mensajes del canal actual")
@app_commands.checks.has_permissions(manage_messages=True)
async def nuke(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Verificar permisos del bot
        bot_perms = interaction.channel.permissions_for(interaction.guild.me)
        if not bot_perms.manage_messages or not bot_perms.add_reactions:
            return await interaction.followup.send("❌ No tengo permisos suficientes (Manage Messages & Add Reactions) para ejecutar esta acción.", ephemeral=True)
        
        # Enviar mensaje de confirmación
        confirm_embed = discord.Embed(
            title="⚠️ Confirmación requerida",
            description="¿Estás seguro de que quieres eliminar todos los mensajes de este canal?",
            color=discord.Color.orange()
        )
        confirm_embed.set_footer(text="Presiona ✅ para confirmar o ❌ para cancelar.")

        confirm_msg = await interaction.channel.send(embed=confirm_embed)
        await confirm_msg.add_reaction("✅")
        await confirm_msg.add_reaction("❌")

        def check(reaction, user):
            return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]

        try:
            reaction, _ = await bot.wait_for("reaction_add", timeout=15.0, check=check)
            if str(reaction.emoji) == "❌":
                await confirm_msg.delete()
                return await interaction.followup.send("❌ Acción cancelada.", ephemeral=True)
        except:
            await confirm_msg.delete()
            return await interaction.followup.send("⏳ No respondiste a tiempo, operación cancelada.", ephemeral=True)

        # Borrar mensajes
        await interaction.channel.purge()
        
        embed = discord.Embed(
            title="💥 Canal Nukeado 💥",
            description="Todos los mensajes han sido eliminados.",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Comando ejecutado por {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.channel.send(embed=embed)
        await interaction.followup.send("✅ Canal limpiado con éxito.", ephemeral=True)
    
    except discord.Forbidden:
        await interaction.followup.send("❌ No tengo permisos suficientes para ejecutar esta acción.", ephemeral=True)
    except discord.HTTPException:
        await interaction.followup.send("❌ Hubo un error al intentar limpiar el canal.", ephemeral=True)

@nuke.error
async def nuke_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)

# userinfo 

@bot.tree.command(name="userinfo", description="Muestra la información del usuario.")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user  # Si no se especifica un miembro, se toma el usuario que ejecutó el comando

    # Obtener información básica del usuario
    username = member.name
    discriminator = member.discriminator
    id = member.id
    avatar_url = member.display_avatar.url
    join_date = member.joined_at.strftime('%Y-%m-%d %H:%M:%S')
    creation_date = member.created_at.strftime('%Y-%m-%d %H:%M:%S')
    status = str(member.status).capitalize()

    # Crear un embed con la información del usuario
    embed = discord.Embed(
        title=f"Información de {username}",
        description=f"Detalles sobre {username} (ID: {id})",
        color=discord.Color.blue()
    )
    embed.set_thumbnail(url=avatar_url)
    embed.add_field(name="🔑 Nombre de usuario", value=f"{username}#{discriminator}", inline=False)
    embed.add_field(name="🆔 ID del usuario", value=str(id), inline=False)
    embed.add_field(name="📅 Fecha de creación de la cuenta", value=creation_date, inline=False)
    embed.add_field(name="📅 Fecha de unión al servidor", value=join_date, inline=False)
    embed.add_field(name="🟢 Estado", value=status, inline=True)

    # Emojis animados (asegúrate de tener los emojis cargados en tu servidor de Discord)
    animated_emoji = "<a:Fuego1:1353231885953794109>"  # Reemplaza con tu emoji animado real

    # Enviar el mensaje de respuesta con un emoji animado
    await interaction.response.send_message(embed=embed)


# Clasificar 

# Comando Slash
@bot.tree.command(name="clasificar", description="Clasifica a un miembro del staff.")
async def clasificar(interaction: discord.Interaction, miembro: discord.Member, razon: str, estrellas: int):
    # Verificar que el número de estrellas esté en el rango adecuado
    if estrellas < 1 or estrellas > 5:
        await interaction.response.send_message("Por favor, proporciona un número de estrellas entre 1 y 5.", ephemeral=True)
        return

    # Crear el embed con el color rojo
    embed = Embed(
        title="Clasificación de Staff",
        description=f"{miembro.mention} ha sido clasificado por la siguiente razón:",
        color=discord.Color.red()
    )
    
    # Añadir la razón y las estrellas
    embed.add_field(name="Razón", value=razon, inline=False)
    embed.add_field(name="Estrellas", value="⭐" * estrellas, inline=False)  # Muestra las estrellas
    embed.set_footer(text="⭐ Clasificación realizada con éxito.")
    
    # Enviar el embed al canal
    await interaction.response.send_message(embed=embed)





    # Comando /tempban
@bot.tree.command(name="tempban")
@app_commands.describe(usuario="Usuario a banear", tiempo="Tiempo de baneo en minutos")
async def tempban(interaction: discord.Interaction, usuario: discord.User, tiempo: int):
    await interaction.response.send_message(f"El usuario {usuario} ha sido baneado temporalmente por {tiempo} minutos.")
    await interaction.guild.ban(usuario, reason=f"Baneo temporal por {tiempo} minutos")
    await asyncio.sleep(tiempo * 60)
    await interaction.guild.unban(usuario)
    await interaction.followup.send(f"El baneo temporal de {usuario} ha finalizado.")

# Comando /undeafen
@bot.tree.command(name="undeafen")
@app_commands.describe(usuario="Usuario a desmutear")
async def undeafen(interaction: discord.Interaction, usuario: discord.Member):
    await usuario.edit(mute=False)
    await interaction.response.send_message(f"Se ha desactivado el deafened de {usuario}.")




# Comando /botinfo
@bot.tree.command(name="botinfo")
async def botinfo(interaction: discord.Interaction):
    await interaction.response.send_message(f"Este es un bot de seguridad desarrollado para moderar servidores.")

# restar
# ID del jefe del bot (¡Reemplázalo con tu ID real!)
OWNER_ID = 1108560647236636774  # <---- Cambia esto por tu ID

# ID del canal donde quieres que el bot avise cuando se reinicie
CHANNEL_ID = 1342296140036575355  # <---- Cambia esto por el ID del canal

@bot.tree.command(name="restart")
async def restart(interaction: discord.Interaction):
    # Verificar si el usuario es el dueño del bot
    if interaction.user.id != OWNER_ID:
        embed = discord.Embed(
            title="❌ Permiso denegado",
            description="Solo el **jefe del bot** puede reiniciarlo.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title="🔄 Reinicio en proceso...",
        description="El bot se está reiniciando...",
        color=discord.Color.orange()
    )

    await interaction.response.send_message(embed=embed)

    await asyncio.sleep(3)  # Esperar 3 segundos antes de cerrar

    await bot.close()  # Apagar el bot

    # Reiniciar el bot
    os.execv(sys.executable, ['python'] + sys.argv)

@bot.event
async def on_ready():
    """Este evento se ejecuta cuando el bot vuelve a estar en línea después del reinicio"""
    canal = bot.get_channel(CHANNEL_ID)
    if canal:
        embed = discord.Embed(
            title="✅ Reinicio completado",
            description="El bot ya está en línea y listo para usar.",
            color=discord.Color.green()
        )
        await canal.send(embed=embed)



# Comando /hug
@bot.tree.command(name="hug")
@app_commands.describe(usuario="Usuario a abrazar")
async def hug(interaction: discord.Interaction, usuario: discord.User):
    hug_gifs = [
        "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
        "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
        "https://media.giphy.com/media/3bqtLDeiDtwhq/giphy.gif",
        "https://media.giphy.com/media/xT39D7ubkIUIrgX2lK/giphy.gif",
        "https://media.giphy.com/media/13YrHUvPzUUmkM/giphy.gif"
    ]

    selected_gif = random.choice(hug_gifs)  # Selecciona un GIF aleatorio

    embed = discord.Embed(
        description=f"{interaction.user.mention} le ha dado un abrazo a {usuario.mention} 🤗",
        color=discord.Color.random()
    )
    embed.set_image(url=selected_gif)  # Agrega el GIF al embed

    # Responder solo una vez correctamente
    await interaction.response.send_message(embed=embed)

    #8ball
@bot.tree.command(name="8ball")
@app_commands.describe(pregunta="Haz una pregunta a la Bola 8")
async def eight_ball(interaction: discord.Interaction, pregunta: str):
    respuestas = [
        "Sí, definitivamente.",
        "No cuentes con ello.",
        "Es muy probable.",
        "Mis fuentes dicen que no.",
        "Pregunta de nuevo más tarde.",
        "No estoy seguro, intenta otra vez.",
        "Parece prometedor.",
        "No lo creo.",
        "Sin duda.",
        "Muy dudoso."
    ]

    respuesta = random.choice(respuestas)  # Selecciona una respuesta aleatoria

    embed = discord.Embed(
        title="🎱 Bola 8 Mágica",
        description=f"**Pregunta:** {pregunta}\n**Respuesta:** {respuesta}",
        color=discord.Color.blue()
    )

    await interaction.response.send_message(embed=embed)



#Avatar

@bot.tree.command(name="avatar")
@app_commands.describe(usuario="Usuario del que quieres ver el avatar")
async def avatar(interaction: discord.Interaction, usuario: discord.User = None):
    usuario = usuario or interaction.user  # Si no mencionan a nadie, muestra el avatar del que usa el comando

    embed = discord.Embed(
        title=f"Avatar de {usuario.name}",
        color=discord.Color.blue()
    )
    embed.set_image(url=usuario.display_avatar.url)  # Obtiene la URL del avatar

    await interaction.response.send_message(embed=embed)


    #amor
@bot.tree.command(name="amor")
@app_commands.describe(usuario1="Primer usuario", usuario2="Segundo usuario")
async def amor(interaction: discord.Interaction, usuario1: discord.User, usuario2: discord.User):
    amor = random.randint(0, 100)  # Genera un porcentaje aleatorio de amor
    mensaje = ""
    
    # Genera un mensaje según el porcentaje
    if amor >= 90:
        mensaje = "¡Es un amor verdadero! ❤️"
    elif amor >= 70:
        mensaje = "¡Hay mucha química entre ustedes! 💕"
    elif amor >= 50:
        mensaje = "¡Hay algo de amor! 😍"
    elif amor >= 30:
        mensaje = "Parece que no es mucho amor... 😅"
    else:
        mensaje = "No hay nada de amor aquí... 😬"

    embed = discord.Embed(
        title="Compatibilidad de Amor",
        description=f"**{usuario1.mention} ❤️ {usuario2.mention}**\n\n**Compatibilidad de amor:** {amor}%\n{mensaje}",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)



#meme 

@bot.tree.command(name="meme")
async def meme(interaction: discord.Interaction):
    # Solicitar un meme aleatorio desde la API de memes
    url = "https://meme-api.com/gimme"
    response = requests.get(url)
    
    if response.status_code == 200:
        meme_data = response.json()
        meme_url = meme_data['url']
        meme_title = meme_data['title']

        # Crear el embed con el meme y el color amarillo
        embed = discord.Embed(
            title=meme_title,
            description="¡Aquí tienes un meme aleatorio para ti!",
            color=discord.Color.from_rgb(255, 255, 0)  # Color amarillo
        )
        embed.set_image(url=meme_url)  # Establecer la imagen del meme

        # Enviar el embed al canal
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("No pude obtener un meme en este momento. Intenta de nuevo más tarde.")


#confulip 

@bot.tree.command(name="coinflip")
@app_commands.describe(usuario1="Primer usuario", usuario2="Segundo usuario")
async def coinflip(interaction: discord.Interaction, usuario1: discord.User, usuario2: discord.User):
    # Crear un embed inicial con el mensaje de "Lanzando..." y los usuarios que están compitiendo
    embed = discord.Embed(
        title="Lanzamiento de la moneda",
        description=f"**Compitiendo:**\n{usuario1.mention} vs {usuario2.mention}\n\nElige 'Cara' o 'Cruz' para hacer tu predicción.",
        color=discord.Color.gold()
    )

    # Crear el select para elegir cara o cruz
    class CoinChoiceSelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label="Cara", description="Elige Cara", value="cara"),
                discord.SelectOption(label="Cruz", description="Elige Cruz", value="cruz")
            ]
            super().__init__(placeholder="¡Haz tu predicción!", min_values=1, max_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            # Obtener la elección del usuario
            eleccion_usuario = self.values[0]
            result = random.choice(["Cara", "Cruz"])

            # Determinar el ganador según el resultado
            if result == "Cara":
                ganador = usuario1
            else:
                ganador = usuario2

            # Crear el embed con el resultado final
            result_embed = discord.Embed(
                title="Resultado del Lanzamiento",
                description=f"**Compitiendo:**\n{usuario1.mention} vs {usuario2.mention}\n\n**El resultado del lanzamiento de la moneda es:** {result}\n**Ganador:** {ganador.mention}",
                color=discord.Color.green()
            )

            # Verificar si el usuario ha acertado
            if eleccion_usuario == result.lower():
                result_embed.add_field(name="🎉 **¡Acertaste!**", value=f"¡Tu predicción fue correcta, {interaction.user.mention}!", inline=False)
            else:
                result_embed.add_field(name="❌ **¡Fallaste!**", value=f"Tu predicción fue incorrecta, {interaction.user.mention}.", inline=False)

            # Enviar el mensaje con el resultado
            await interaction.response.edit_message(embed=result_embed, view=view)

    # Crear la vista y añadir el select para elegir cara o cruz
    view = View()
    select = CoinChoiceSelect()
    view.add_item(select)

    # Enviar el mensaje inicial con el select
    await interaction.response.send_message(embed=embed, view=view)


















































# Comando /banlist
@bot.tree.command(name="banlist")
async def banlist(interaction: discord.Interaction):
    bans = await interaction.guild.bans()
    banlist = "\n".join([str(ban.user) for ban in bans])
    await interaction.response.send_message(f"Usuarios baneados:\n{banlist}")

# Comando /setstatus
@bot.tree.command(name="setstatus")
@app_commands.describe(estado="Estado del bot (Online, Idle, Do not disturb)")
async def setstatus(interaction: discord.Interaction, estado: str):
    # IDs permitidos, incluyendo el del dueño del bot
    allowed_ids = [bot.owner_id, 1108560647236636774]  # Reemplaza con los IDs permitidos

    # Verificar si el usuario tiene permiso
    if interaction.user.id not in allowed_ids:
        embed = discord.Embed(
            title="❌ Permiso denegado",
            description="Solo el **dueño del bot** o usuarios con permisos especiales pueden usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    estados = {
        "online": {"status": discord.Status.online, "color": discord.Color.green(), "emoji": "🟢"},
        "idle": {"status": discord.Status.idle, "color": discord.Color.orange(), "emoji": "🟠"},
        "dnd": {"status": discord.Status.dnd, "color": discord.Color.red(), "emoji": "🔴"}
    }

    estado_lower = estado.lower()

    if estado_lower not in estados:
        embed = discord.Embed(
            title="❌ Error",
            description="Estado no reconocido. Usa `Online`, `Idle` o `DND`.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await bot.change_presence(status=estados[estado_lower]["status"])

    embed = discord.Embed(
        title="✅ Estado actualizado",
        description=f"El estado del bot ha sido cambiado a {estados[estado_lower]['emoji']} **{estado.capitalize()}**.",
        color=estados[estado_lower]["color"]
    )

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="setbotstatus")
@app_commands.describe(estado="Estado de actividad del bot")
async def setbotstatus(interaction: discord.Interaction, estado: str):
    # IDs permitidos, incluyendo el del dueño del bot
    allowed_ids = [bot.owner_id, 1108560647236636774]  # Reemplaza con los IDs permitidos

    # Verificar si el usuario tiene permiso
    if interaction.user.id not in allowed_ids:
        embed = discord.Embed(
            title="❌ Permiso denegado",
            description="Solo el **dueño del bot** o usuarios con permisos especiales pueden usar este comando.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    await bot.change_presence(activity=discord.Game(name=estado))
    await interaction.response.send_message(f"Estado de actividad del bot cambiado a {estado}.")

# Comando /mutelist
@bot.tree.command(name="mutelist")
async def mutelist(interaction: discord.Interaction):
    muted_members = [member for member in interaction.guild.members if member.mute]
    mute_list = "\n".join([str(member) for member in muted_members])
    await interaction.response.send_message(f"Usuarios silenciados:\n{mute_list}")

# Comando /setantiflood
@bot.tree.command(name="setantiflood")
@app_commands.describe(
    tiempo="Tiempo máximo entre mensajes (en segundos)",
    mensaje="Mensaje que se enviará cuando alguien haga flood"
)
async def setantiflood(interaction: discord.Interaction, tiempo: int, mensaje: str):
    embed = discord.Embed(
        title="🛡️ Sistema Antiflood Activado",
        description=f"El sistema antiflood ha sido configurado con los siguientes parámetros:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="⏳ Tiempo límite", value=f"{tiempo} segundos", inline=False)
    embed.add_field(name="💬 Mensaje de advertencia", value=f"'{mensaje}'", inline=False)
    
    embed.set_footer(text="Recuerda que el antiflood ayuda a mantener el orden en el chat.")

    await interaction.response.send_message(embed=embed)







   




    # kick 
@bot.tree.command(name="kick", description="Expulsa a un usuario del servidor.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = None):
    # Verificar si el usuario tiene permisos para ejecutar el comando
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("No tienes permisos suficientes para expulsar a miembros.", ephemeral=True)

    # Verificar si el miembro a expulsar tiene un rol superior al del ejecutante del comando
    if member.top_role >= interaction.user.top_role:
        return await interaction.response.send_message("No puedes expulsar a este miembro porque tiene un rol igual o superior al tuyo.", ephemeral=True)

    # Crear un embed con la notificación del kick
    embed = discord.Embed(
        title="✅ Miembro expulsado",
        description=f"{member.mention} ha sido expulsado del servidor.\nRazón: {reason if reason else 'No se proporcionó ninguna razón.'}",
        color=discord.Color.blue()
    )

    embed.add_field(name="📝 Razón", value=reason if reason else "No se proporcionó ninguna razón.", inline=False)
    embed.add_field(name="🔨 Acción", value="Expulsado correctamente", inline=False)
    embed.set_footer(text=f"Expulsado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

    # Expulsar al miembro
    try:
        await member.kick(reason=reason)

        # Enviar notificación al canal de logs si existe
        log_channel = discord.utils.get(interaction.guild.text_channels, name="moderation-logs")
        if log_channel:
            await log_channel.send(f"🚨 **{interaction.user}** ha expulsado a {member.mention} del servidor. Razón: {reason if reason else 'No especificada.'}", embed=embed)

        # Confirmación al canal donde se ejecutó el comando
        await interaction.response.send_message(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("No tengo permisos para expulsar a este miembro.", ephemeral=True)
    except discord.HTTPException:
        await interaction.response.send_message("Ocurrió un error al intentar expulsar al miembro.", ephemeral=True)



# Comando para recuperar los mensajes recientes de un usuario
@bot.tree.command(name="messagegrab", description="Recupera los mensajes de un usuario en los últimos X minutos.")
@app_commands.describe(usuario="El usuario del que recuperar mensajes", minutos="Tiempo en minutos")
async def messagegrab(interaction: discord.Interaction, usuario: discord.Member, minutos: int):
    await interaction.response.defer()
    since_time = discord.utils.utcnow() - discord.utils.timedelta(minutes=minutos)
    messages = []
    
    for channel in interaction.guild.text_channels:
        try:
            async for message in channel.history(limit=100, after=since_time):
                if message.author == usuario:
                    messages.append(f"[{channel.name}] {message.content}")
        except discord.Forbidden:
            continue  # Saltar canales donde el bot no tiene permiso

    if messages:
        response = "\n".join(messages[:10])  # Limita a 10 mensajes para evitar spam
    else:
        response = "No se encontraron mensajes recientes."
    
    await interaction.followup.send(f"Mensajes de {usuario.mention}:\n{response}")

# Comando para buscar palabras en los registros
@bot.tree.command(name="logsearch", description="Busca en los registros del bot cualquier mensaje con cierta palabra.")
@app_commands.describe(palabra="Palabra clave a buscar")
async def logsearch(interaction: discord.Interaction, palabra: str):
    await interaction.response.defer()
    logs = []
    
    for channel in interaction.guild.text_channels:
        try:
            async for message in channel.history(limit=100):
                if palabra.lower() in message.content.lower():
                    logs.append(f"[{channel.name}] {message.author}: {message.content}")
        except discord.Forbidden:
            continue  # Saltar canales sin permiso
    
    if logs:
        response = "\n".join(logs[:10])  # Limita la cantidad de mensajes mostrados
    else:
        response = "No se encontraron coincidencias."
    
    await interaction.followup.send(response)

# Comando para clonar el servidor
@bot.tree.command(name="serverclone", description="Crea un backup del servidor.")
async def serverclone(interaction: discord.Interaction):
    await interaction.response.send_message("Este comando requiere permisos avanzados y debe implementarse con una base de datos.")





@bot.tree.command(name="whisper", description="Envía un mensaje privado anónimo a un usuario.")
@app_commands.describe(usuario="El usuario destinatario", mensaje="El mensaje a enviar")
async def whisper(interaction: discord.Interaction, usuario: discord.Member, mensaje: str):
    try:
        # Enviar mensaje anónimo al usuario
        await usuario.send(f"**Mensaje anónimo recibido**\n\n{mensaje}")
        
        # Crear un embed para la respuesta al usuario que envía el mensaje
        embed = discord.Embed(
            title="✉️ Mensaje Enviado Anónimamente",
            description=f"Tu mensaje ha sido enviado de forma anónima a {usuario.mention}.",
            color=discord.Color.green()
        )
        embed.set_footer(text="¡Mantén la magia del anonimato! 🔒")
        
        # Enviar mensaje de confirmación al que ejecuta el comando
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    except discord.Forbidden:
        # Si el bot no tiene permisos para enviar mensaje
        await interaction.response.send_message("No puedo enviar mensajes a este usuario. Verifica sus configuraciones de privacidad.", ephemeral=True)
    
    except discord.HTTPException:
        # Si ocurre un error general de HTTP
        await interaction.response.send_message("Hubo un error al intentar enviar el mensaje. Intenta de nuevo más tarde.", ephemeral=True)
    
    except Exception as e:
        # Cualquier otro error no previsto
        await interaction.response.send_message(f"Ocurrió un error inesperado: {e}", ephemeral=True)

# Sincronizar comandos en el servidor
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot conectado como {bot.user}")





        # soporte 


# Configuración
CANAL_REPORTES_ID = 1335724519251513521  # Reemplaza con el ID real
PALABRAS_PROHIBIDAS = ["pato", "lmb", "cbrn" , "mmg" , "wlb"]  # Lista de palabras a filtrar



@bot.event
async def on_ready():
    print(f'{bot.user} ha iniciado sesión')

# Comando para reportar
@bot.tree.command(name="reportar", description="Envía un reporte al canal de reportes")
@app_commands.describe(reporte="Describe el problema o usuario a reportar")
async def reportar(interaction: discord.Interaction, reporte: str):
    # Filtrar palabras prohibidas
    for palabra in PALABRAS_PROHIBIDAS:
        if palabra.lower() in reporte.lower():
            await interaction.response.send_message("⚠️ Tu reporte contiene lenguaje inapropiado. Por favor, reformúlalo utilizando un tono más profesional y respetuoso.", ephemeral=True)
            return

    # Obtener el canal de reportes
    try:
        canal_reportes = await bot.fetch_channel(CANAL_REPORTES_ID)
    except discord.NotFound:
        await interaction.response.send_message("⚠️ No se encontró el canal de reportes. Contacta con un administrador.", ephemeral=True)
        return
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ No tengo permisos para acceder al canal de reportes.", ephemeral=True)
        return

    # Generar un enlace de invitación al servidor
    try:
        invitacion = await interaction.guild.text_channels[0].create_invite(max_uses=1, unique=True)
        link_servidor = invitacion.url
    except Exception:
        link_servidor = "No se pudo generar un enlace."

    # Crear Embed del reporte
    embed = Embed(
        title="📢 Nuevo Reporte",
        description=f"**Usuario:** {interaction.user.mention} (`{interaction.user.id}`)\n"
                    f"**Servidor:** {interaction.guild.name}\n"
                    f"**Reporte:** {reporte}",
        color=discord.Color.red(),
        timestamp=interaction.created_at
    )
    embed.add_field(name="🔗 Enlace al servidor", value=f"[Unirse al servidor]({link_servidor})", inline=False)
    embed.set_footer(text=f"Reporte enviado desde {interaction.guild.name}", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
    embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

    # Enviar el reporte al canal de reportes
    try:
        await canal_reportes.send(embed=embed)
        await interaction.response.send_message("✅ ¡Tu reporte ha sido enviado correctamente!", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("⚠️ No tengo permisos para enviar mensajes en el canal de reportes.", ephemeral=True)









    # Copia de seguridad 

@bot.tree.command(name="copia_de_seguridad", description="Crea una copia de seguridad del servidor")
@app_commands.checks.has_permissions(administrator=True)
async def copia_de_seguridad(interaction: discord.Interaction):
    codigo_respaldo = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    backup_data = {}

    server = interaction.guild
    try:
        backup_data['server_name'] = server.name
        backup_data['server_icon'] = str(server.icon.url) if server.icon else None
    except:
        pass

    backup_data['roles'] = []
    for role in server.roles:
        if role.name != "@everyone":
            role_data = {
                'name': role.name,
                'permissions': role.permissions.value,
                'color': role.color.value,
                'hoist': role.hoist,
                'position': role.position,
                'mentionable': role.mentionable
            }
            backup_data['roles'].append(role_data)

    backup_data['categories'] = []
    backup_data['text_channels'] = []
    backup_data['voice_channels'] = []

    for category in server.categories:
        cat_data = {
            'name': category.name,
            'position': category.position,
            'overwrites': [{
                'id': k.id,
                'allow': v.allow.value,
                'deny': v.deny.value
            } for k, v in category.overwrites.items()]
        }
        backup_data['categories'].append(cat_data)

    for channel in server.text_channels:
        chan_data = {
            'name': channel.name,
            'category': channel.category.name if channel.category else None,
            'topic': channel.topic,
            'position': channel.position,
            'slowmode_delay': channel.slowmode_delay,
            'nsfw': channel.is_nsfw(),
            'overwrites': [{
                'id': k.id,
                'allow': v.allow.value,
                'deny': v.deny.value
            } for k, v in channel.overwrites.items()]
        }
        backup_data['text_channels'].append(chan_data)

    for vc in server.voice_channels:
        vc_data = {
            'name': vc.name,
            'category': vc.category.name if vc.category else None,
            'position': vc.position,
            'user_limit': vc.user_limit,
            'bitrate': vc.bitrate,
            'overwrites': [{
                'id': k.id,
                'allow': v.allow.value,
                'deny': v.deny.value
            } for k, v in vc.overwrites.items()]
        }
        backup_data['voice_channels'].append(vc_data)

    with open(f'backup_{codigo_respaldo}.json', 'w') as f:
        json.dump(backup_data, f)

    embed = discord.Embed(
        title="📂 Copia de Seguridad del Servidor",
        description=f"Tu copia de seguridad ha sido creada con éxito.\n\n**Código:** `{codigo_respaldo}`",
        color=discord.Color.blue()
    )

    await interaction.user.send(embed=embed)
    await interaction.response.send_message("✅ Se ha generado una copia de seguridad. Te envié un DM con los detalles.", ephemeral=True)

@bot.tree.command(name="cargar_copia_seguridad", description="Restaura una copia de seguridad con un código")
@app_commands.checks.has_permissions(administrator=True)
async def cargar_copia_seguridad(interaction: discord.Interaction, codigo_respaldo: str):
    backup_file = f'backup_{codigo_respaldo}.json'
    
    if not os.path.exists(backup_file):
        await interaction.response.send_message("❌ No se encontró una copia de seguridad con ese código.", ephemeral=True)
        return

    with open(backup_file, 'r') as f:
        backup_data = json.load(f)

    guild = interaction.guild

    # Borrar roles y canales actuales
    for channel in guild.channels:
        try:
            await channel.delete()
        except:
            continue

    for role in guild.roles:
        if role.name != "@everyone":
            try:
                await role.delete()
            except:
                continue

    # Restaurar roles
    for role_data in reversed(backup_data['roles']):
        try:
            await guild.create_role(
                name=role_data['name'],
                permissions=discord.Permissions(role_data['permissions']),
                color=discord.Color(role_data['color']),
                hoist=role_data['hoist'],
                mentionable=role_data['mentionable']
            )
        except:
            continue

    # Restaurar categorías
    for cat_data in backup_data['categories']:
        try:
            await guild.create_category(name=cat_data['name'])
        except:
            continue

    # Restaurar canales de texto
    for chan_data in backup_data['text_channels']:
        try:
            category = discord.utils.get(guild.categories, name=chan_data['category'])
            await guild.create_text_channel(
                name=chan_data['name'],
                category=category,
                topic=chan_data['topic'],
                nsfw=chan_data['nsfw'],
                slowmode_delay=chan_data['slowmode_delay']
            )
        except:
            continue

    # Restaurar canales de voz
    for vc_data in backup_data['voice_channels']:
        try:
            category = discord.utils.get(guild.categories, name=vc_data['category'])
            await guild.create_voice_channel(
                name=vc_data['name'],
                category=category,
                bitrate=vc_data['bitrate'],
                user_limit=vc_data['user_limit']
            )
        except:
            continue

    embed = discord.Embed(
        title="✅ Restauración Exitosa",
        description=f"**Copia de seguridad restaurada correctamente**\n\n**Código:** `{codigo_respaldo}`",
        color=discord.Color.green()
    )

    await interaction.response.send_message(embed=embed)

# Sincronizar comandos de barra
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"🔗 {len(synced)} comandos de barra sincronizados.")
    except Exception as e:
        print(f"❌ Error al sincronizar comandos: {e}")


        # server info 

@bot.tree.command(name="serverinfo", description="Muestra información del servidor")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    owner = guild.owner
    member_count = guild.member_count
    created_at = guild.created_at.strftime("%d/%m/%Y a las %H:%M")
    icon_url = guild.icon.url if guild.icon else "No tiene icono"
    
    # Crea el embed para mostrar la información del servidor
    embed = discord.Embed(
        title=f"Información de {guild.name}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="🔑 Propietario", value=f"{owner}", inline=False)
    embed.add_field(name="👥 Miembros", value=f"{member_count}", inline=False)
    embed.add_field(name="📅 Fecha de creación", value=f"{created_at}", inline=False)
    
    # Si el servidor tiene un icono, mostrarlo
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    embed.set_footer(text=f"Comando ejecutado por {interaction.user.name}", icon_url=interaction.user.avatar.url)

    # Envía el embed como respuesta
    await interaction.response.send_message(embed=embed)


    # regitro 


# Diccionario para almacenar los usuarios registrados
usuarios_registrados = {}

# Registrar los comandos slash
@bot.event
async def on_ready():
    print(f'Bot {bot.user} conectado')
    # Sincronizar los comandos slash
    await bot.tree.sync()

# Comando slash para registrar al usuario
@bot.tree.command(name="registro", description="Registra tu nombre de usuario de Roblox.")
async def registro(interaction: discord.Interaction, nombre_usuario: str):
    """Comando para registrar a un usuario con su nombre de usuario de Roblox."""
    user_id = interaction.user.id  # Obtener el ID del usuario de Discord
    
    # Verificar si el usuario ya está registrado
    if user_id in usuarios_registrados:
        await interaction.response.send_message(f"{interaction.user.mention}, ya estás registrado con el nombre de usuario de Roblox {usuarios_registrados[user_id]}.")
    else:
        # Registrar al usuario
        usuarios_registrados[user_id] = nombre_usuario

        # Crear un embed para la respuesta
        embed = Embed(
            title="Registro Exitoso",
            description=f"¡Te has registrado con éxito con el nombre de usuario de Roblox: **{nombre_usuario}**!",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Registrado por {interaction.user.name}", icon_url=interaction.user.avatar.url)
        
        # Enviar el embed
        await interaction.response.send_message(embed=embed)



    # logs


# Configuración del bot con Intents
intents = discord.Intents.all()
tree = bot.tree  # Para manejar slash commands

# Diccionario para almacenar los canales de logs de cada servidor
log_channels = {}  # {server_id: channel_id}

@bot.event
async def on_ready():
    await tree.sync()  # Sincronizar comandos de barra
    print(f"✅ {bot.user} está en línea y listo!")

# Comando /setlogs para establecer el canal de logs
@tree.command(name="setlogs", description="Establece el canal donde se enviarán los logs.")
async def setlogs(interaction: discord.Interaction, channel: discord.TextChannel):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("🚫 No tienes permisos para usar este comando.", ephemeral=True)
        return
    
    log_channels[interaction.guild.id] = channel.id
    await interaction.response.send_message(f"✅ Canal de logs configurado: {channel.mention}")

# Función auxiliar para enviar logs
async def send_log(guild, embed):
    log_channel_id = log_channels.get(guild.id)
    if log_channel_id:
        log_channel = bot.get_channel(log_channel_id)
        if log_channel:
            await log_channel.send(embed=embed)

# Registrar mensajes eliminados
@bot.event
async def on_message_delete(message):
    if message.guild and not message.author.bot:
        embed = discord.Embed(title="🗑️ Mensaje eliminado", color=discord.Color.red())
        embed.add_field(name="Autor", value=message.author.mention, inline=False)
        embed.add_field(name="Canal", value=message.channel.mention, inline=False)
        embed.add_field(name="Contenido", value=message.content or "Embed/Archivo eliminado", inline=False)
        embed.set_footer(text=f"ID: {message.id} | {message.created_at}")
        await send_log(message.guild, embed)

# Registrar mensajes editados
@bot.event
async def on_message_edit(before, after):
    if before.guild and not before.author.bot and before.content != after.content:
        embed = discord.Embed(title="✏️ Mensaje editado", color=discord.Color.orange())
        embed.add_field(name="Autor", value=before.author.mention, inline=False)
        embed.add_field(name="Canal", value=before.channel.mention, inline=False)
        embed.add_field(name="Antes", value=before.content, inline=False)
        embed.add_field(name="Después", value=after.content, inline=False)
        embed.set_footer(text=f"ID: {before.id} | {before.created_at}")
        await send_log(before.guild, embed)

# Registrar baneos
@bot.event
async def on_member_ban(guild, user):
    embed = discord.Embed(title="🚨 Usuario baneado", color=discord.Color.red())
    embed.add_field(name="Usuario", value=user.mention, inline=False)
    embed.set_footer(text=f"ID: {user.id}")
    await send_log(guild, embed)

# Registrar expulsiones
@bot.event
async def on_member_remove(member):
    embed = discord.Embed(title="⚠️ Usuario expulsado/salió", color=discord.Color.orange())
    embed.add_field(name="Usuario", value=member.mention, inline=False)
    embed.set_footer(text=f"ID: {member.id}")
    await send_log(member.guild, embed)

# Registrar cambios de roles
@bot.event
async def on_member_update(before, after):
    if before.roles != after.roles:
        embed = discord.Embed(title="🔄 Cambio de roles", color=discord.Color.blue())
        embed.add_field(name="Usuario", value=after.mention, inline=False)
        before_roles = ", ".join([r.mention for r in before.roles])
        after_roles = ", ".join([r.mention for r in after.roles])
        embed.add_field(name="Antes", value=before_roles or "Ninguno", inline=False)
        embed.add_field(name="Después", value=after_roles or "Ninguno", inline=False)
        embed.set_footer(text=f"ID: {after.id}")
        await send_log(after.guild, embed)





   # multas

# Diccionario para almacenar las multas de los jugadores
multas_jugadores = {}

# Registrar los comandos slash
@bot.event
async def on_ready():
    print(f'Bot {bot.user} conectado')
    # Sincronizar los comandos slash
    await bot.tree.sync()

# Comando slash para imponer una multa a un jugador
@bot.tree.command(name="multas", description="Imponer una multa a un jugador por violar reglas de rol.")
async def multas(interaction: discord.Interaction, jugador: discord.Member, motivo: str):
    """Comando para imponer una multa a un jugador por violar reglas de rol."""
    # Verificar si el usuario que ejecuta el comando es un administrador
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("¡No tienes permiso para imponer multas!", ephemeral=True)
        return
    
    # Agregar la multa al jugador
    if jugador.id not in multas_jugadores:
        multas_jugadores[jugador.id] = []
    
    # Registrar la multa
    multas_jugadores[jugador.id].append(motivo)
    
    # Crear un embed para la multa
    embed = Embed(
        title="Multa Impuesta",
        description=f"Has sido multado por el siguiente motivo:\n\n**{motivo}**",
        color=discord.Color.red()
    )
    embed.set_footer(text=f"Impuesta por {interaction.user.name}", icon_url=interaction.user.avatar.url)
    
    # Enviar el embed con la multa en el canal donde se ejecutó el comando
    await interaction.response.send_message(embed=embed)

    # Notificar al jugador de la multa en su DM con un embed
    try:
        embed_dm = Embed(
            title="¡Has recibido una multa!",
            description=f"**Motivo:** {motivo}\n\nPor favor, respétanos las reglas del servidor.",
            color=discord.Color.red()
        )
        embed_dm.set_footer(text=f"Multa impuesta por {interaction.user.name}", icon_url=interaction.user.avatar.url)
        
        await jugador.send(embed=embed_dm)
    except discord.errors.Forbidden:
        await interaction.response.send_message(f"No pude enviar la multa a {jugador.mention} porque tiene los DMs desactivados.")


        # Raid limit


@bot.event
async def on_command(ctx):
    print(f"🛠️ Comando ejecutado: {ctx.command} por {ctx.author} en {ctx.guild.name} (ID: {ctx.guild.id})")




@bot.event
async def on_command(ctx):
    user = ctx.author
    command_usage[user.id] += 1
    print(f"⚠️ {user} ha usado {command_usage[user.id]} comandos.")

    if command_usage[user.id] > 10:  # Ajusta este límite si es necesario
        await ctx.send(f"⚠️ {user.mention}, estás usando demasiados comandos en poco tiempo.")


@bot.event
async def on_command(ctx):
    user = ctx.author
    command_name = ctx.command
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("command_logs.txt", "a") as f:
        f.write(f"[{now}] {user} ejecutó {command_name}\n")

    print(f"📝 Registrado: {user} ejecutó {command_name}")







# Anti-Webhooks 

@bot.event
async def on_webhooks_update(channel):
    guild = channel.guild
    webhooks = await channel.webhooks()

    for webhook in webhooks:
        if webhook.user != bot.user:
            # Crear Embed de Alerta con emojis animados
            embed = discord.Embed(
                title="<a:red_siren1:1349869405571649567> ¡ALERTA DE SEGURIDAD! <a:red_siren1:1349869405571649567>",  # Emoji animado personalizado
                description=f"Se ha detectado un webhook en {channel.mention}. **Eliminándolo...**",
                color=discord.Color.red()  # Color rojo
            )
            embed.set_footer(text="Sistema de Seguridad | Anti-Webhooks")

            # Buscar el canal de logs
            log_channel = discord.utils.get(guild.text_channels, name="logs")
            if log_channel:
                await log_channel.send(embed=embed)

            # Enviar alerta en el mismo canal donde se creó el webhook
            await channel.send(embed=embed)

            # Eliminar el webhook
            await webhook.delete()
            print(f"🚨 Webhook eliminado en {channel.name}")



        


# Bienvenida 

@bot.event
async def on_guild_join(guild):
    # Buscar el primer canal donde el bot pueda enviar mensajes
    welcome_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            welcome_channel = channel
            break

    # Si se encontró un canal adecuado
    if welcome_channel:
        # Crear el Embed de Bienvenida con un GIF
        embed = discord.Embed(
            title="🤖 ¡Gracias por agregarme! <a:Fuego1:1353231885953794109>",  # Emoji animado personalizado
            description=f"¡Hola! Soy **{bot.user.name}**, tu nuevo bot de seguridad y moderación. 🚀\n\n"
                        "✅ Usa `/cmds` para ver todos mis comandos disponibles.\n"
                        "⚙️ Asegúrate de configurar mis permisos para que pueda ofrecerte la mejor ayuda.\n"
                        "📢 Si tienes dudas o necesitas soporte, no dudes en contactar a mi creador usando `/reportar`.",
            color=discord.Color.green()  # Color verde para un toque positivo
        )
        embed.set_image(url="https://media.discordapp.net/attachments/1222707673884131439/1340532294770757682/standard_4.gif?ex=67b8a23c&is=67b750bc&hm=da2b6f0d3a726d00c42d1308ea3562aca9224195f0953515531f1348e1079565&=")  # GIF de bienvenida
        embed.set_footer(text="¡Gracias por confiar en mí! 💙\n¡Vamos a hacer de tu servidor un lugar más seguro!")

        # Enviar el mensaje en el primer canal disponible
        await welcome_channel.send(embed=embed)

    # Si no se encuentra un canal adecuado
    else:
        print(f"⚠️ No se encontró un canal adecuado para enviar el mensaje de bienvenida en el servidor {guild.name}.")








@bot.tree.command(name="cmds", description="Muestra la lista de comandos disponibles")
async def cmds(interaction: discord.Interaction):
    # Lista de comandos por categorías
    comandos_generales = [
        "🏓 **/ping** - Muestra la latencia del bot.",
        "💥 **/nuke** - Elimina todos los mensajes del canal actual.",
        "📊 **/status** - Muestra el estado del bot.",
        "🚫 **/ban** - Banea a un miembro del servidor.",
        "✅ **/whitelist** - Agrega un usuario a la whitelist.",
        "⚠️ **/remove_whitelist** - Remueve un usuario de la whitelist.",
        "🚶‍♂️ **/kick** - Expulsa a un miembro del servidor."
    ]
    
    comandos_avanzados = [
        "🛑 **/serverinfo** - Muestra información del servidor.",
        "🚫 **/blacklist_add** - Agrega un usuario a la lista negra.",
        "🚫 **/blacklist_remove** - Remueve un usuario de la lista negra.",
        "🔇 **/mute** - Silencia a un miembro del servidor.",
        "🔊 **/unmute** - Quita el mute a un miembro del servidor.",
        "📊 **/userinfo** - Muestra la información de un usuario.",
        "📝 **/warn** - Advierte a un usuario."
    ]
    
    comandos_roles = [
        "🎭 **/pedirrol** - Solicita un rol específico.",
        "🔄 **/cambiarestado** - Cambia el estado del bot.",
        "📂 **/copia_de_seguridad** - Crea una copia de seguridad del servidor.",
        "🔄 **/cargar_copia_seguridad <código>** - Restaura una copia de seguridad.",
        "🟢 **/add_role_all** - Asigna un rol a todos los miembros del servidor.",
        "🔴 **/remove_role_all** - Elimina un rol de todos los miembros del servidor."
    ]
    
    comandos_meme_amor_avatar = [
        "❤️ **/meme** - Envía un meme aleatorio.",
        "💖 **/amor** - Muestra un mensaje romántico o amoroso.",
        "👑 **/avatar @usuario** - Muestra el avatar de un usuario específico.",
        "💥 **/confulip** - Muestra un mensaje con un toque divertido y al estilo 'confulip'."
    ]

    # Crear el embed inicial
    embed = discord.Embed(
        title="⚙️ **Comandos Disponibles**",
        description="Aquí tienes los comandos disponibles. Haz clic en el botón para ver más.",
        color=discord.Color.gold()  # Color dorado para el botón amarillo
    )
    embed.add_field(name="🔍 **Cómo funciona**", value="Haz clic en el botón para explorar las categorías de comandos.", inline=False)

    # Crear el botón amarillo
    button = Button(style=discord.ButtonStyle.primary, label="Ver Comandos", emoji="🔧")
    
    # Función que se ejecuta cuando el botón es presionado
    async def button_callback(interaction):
        # Crear un nuevo embed para mostrar las categorías
        embed_comandos = discord.Embed(
            title="🌐 **Comandos por Categorías**",
            description="Selecciona una categoría para ver los comandos correspondientes.",
            color=discord.Color.gold()  # Dorado para un toque más de amarillo
        )
        embed_comandos.add_field(name="🔧 **Generales**", value="\n".join(comandos_generales), inline=False)
        embed_comandos.add_field(name="⚡ **Avanzados**", value="\n".join(comandos_avanzados), inline=False)
        embed_comandos.add_field(name="🎭 **Roles**", value="\n".join(comandos_roles), inline=False)
        embed_comandos.add_field(name="🎉 **Meme, Amor y Avatar**", value="\n".join(comandos_meme_amor_avatar), inline=False)
        
        # Enviar el mensaje con los comandos
        await interaction.response.send_message(embed=embed_comandos)

    # Asignar el callback al botón
    button.callback = button_callback

    # Crear la vista para el botón
    view = View()
    view.add_item(button)

    # Enviar el mensaje con el botón
    await interaction.response.send_message(embed=embed, view=view)






    # robos 




intents = discord.Intents.default()
intents.message_content = True  # Necesario para leer mensajes (si es necesario)



# Ejemplo de datos de robos activos
robos = []

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')
    # Sincroniza los comandos slash
    await bot.tree.sync()
    print("Comandos slash sincronizados.")

@bot.tree.command(name="robos", description="Informa sobre los robos activos.")
async def robos(interaction: discord.Interaction):
    # Preguntar por la razón
    await interaction.response.send_message("¿Cuál es la razón del robo? (Ejemplo: Robo de dinero, objetos, etc.)")

    # Esperar la respuesta del usuario (razón)
    def check_message(msg):
        return msg.author == interaction.user and isinstance(msg.channel, discord.TextChannel)

    razon_msg = await bot.wait_for("message", check=check_message)
    razon = razon_msg.content

    # Preguntar por el número de personas
    await interaction.followup.send("¿Cuántas personas están involucradas en el robo?")

    # Esperar la respuesta del número de personas
    personas_msg = await bot.wait_for("message", check=check_message)
    try:
        personas = int(personas_msg.content)
    except ValueError:
        await interaction.followup.send("Por favor, ingresa un número válido para la cantidad de personas.")
        return

    # Crear el Embed con la razón y el número de personas
    embed = discord.Embed(
        title="🚨 **Nuevo Robo Reportado** 🚨",
        description="Detalles del robo:",
        color=discord.Color.red()
    )

    embed.add_field(name="Razón del robo", value=razon, inline=False)
    embed.add_field(name="Número de personas involucradas", value=str(personas), inline=False)

    # Enviar el embed al canal de Discord
    await interaction.followup.send(embed=embed)

















    # Warns

# Diccionario para almacenar advertencias (puedes cambiarlo por una base de datos si lo deseas)
warnings = {}
@bot.tree.command(name="warn", description="Advierte a un usuario.")
@app_commands.describe(user="El usuario a advertir", reason="Razón de la advertencia")
async def warn(interaction: discord.Interaction, user: discord.Member, reason: str = "No se proporcionó razón"):
    if interaction.user.guild_permissions.administrator:
        # Agregar advertencia al usuario
        if user.id not in warnings:
            warnings[user.id] = []
        warnings[user.id].append(reason)

        embed = discord.Embed(
            title="<a:rf_alert:1353235268232020012> Advertencia Emitida <a:rf_alert:1353235268232020012>",  # Emoji animado personalizado
            description=f"{user.mention} ha sido advertido.",
            color=discord.Color.orange()
        )
        embed.add_field(name="Razón", value=reason, inline=False)
        embed.add_field(name="Cantidad de advertencias", value=str(len(warnings[user.id])), inline=False)
        embed.set_footer(text=f"Advertido por {interaction.user.name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

        # Notificar al usuario advertido
        try:
            dm_embed = discord.Embed(
                title="⚠️ Has sido advertido <a:rf_alert:1353235268232020012>",  # Emoji animado personalizado
                description=f"Has recibido una advertencia en {interaction.guild.name}.",
                color=discord.Color.red()
            )
            dm_embed.add_field(name="Razón", value=reason, inline=False)
            dm_embed.add_field(name="Cantidad de advertencias", value=str(len(warnings[user.id])), inline=False)
            await user.send(embed=dm_embed)
        except:
            pass  # Si no se puede enviar DM, continuar sin errores
    else:
        await interaction.response.send_message("🚫 No tienes permisos para usar este comando.", ephemeral=True)

# add rol 

@bot.tree.command(name="add_role_all", description="Asigna un rol a todos los miembros del servidor.")
@app_commands.describe(role="El rol que se asignará a todos los miembros")
async def add_role_all(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("🚫 No tienes permisos para usar este comando.", ephemeral=True)

    members = interaction.guild.members
    success_count = 0
    failed_count = 0

    await interaction.response.send_message(f"⏳ Asignando el rol **{role.name}** a todos los miembros... Esto puede tardar. 🌟")

    for member in members:
        try:
            if role not in member.roles:
                await member.add_roles(role)
                success_count += 1
        except:
            failed_count += 1

    embed = discord.Embed(
        title="<a:red_siren1:1349869405571649567>Rol  Asignado a Todos <a:red_siren1:1349869405571649567>",  # Emoji animado personalizado
        description=f"Se ha asignado el rol **{role.name}** a los miembros.",
        color=discord.Color.green()
    )
    embed.add_field(name="✔️ Éxitos", value=str(success_count))
    embed.add_field(name="❌ Fallos", value=str(failed_count))
    embed.set_footer(text=f"Comando ejecutado por {interaction.user.name}", icon_url=interaction.user.avatar.url)

    await interaction.followup.send(embed=embed)





# ban 
@bot.tree.command(name="ban", description="Banea a un usuario del servidor.")
@app_commands.describe(member="El usuario que deseas banear", reason="Razón del baneo")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "No especificado"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("❌ No tienes permisos para banear usuarios.", ephemeral=True)
        return
    
    if interaction.user == member:
        await interaction.response.send_message("❌ No puedes banearte a ti mismo.", ephemeral=True)
        return

    try:
        await member.ban(reason=reason)
        
        # Embed para la confirmación del baneo
        embed = discord.Embed(
            title="🚫 Usuario Baneado",
            description=f"**{member.mention}** ha sido baneado.\n\n**Razón:** {reason}",
            color=discord.Color.red()
        )
        embed.set_footer(text=f"Moderador: {interaction.user.name}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        # Respuesta oculta al moderador
        await interaction.response.send_message(f"✅ Has baneado a {member.mention}.", ephemeral=True)
        
        # Mensaje público en el canal confirmando el baneo
        await interaction.channel.send(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("❌ No tengo permisos suficientes para banear a este usuario.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ocurrió un error: {e}", ephemeral=True)


   






# Whitekist

@bot.tree.command(name="add_whitelist", description="Agrega un usuario a la whitelist.")
async def add_whitelist(interaction: discord.Interaction, user_id: str):
    # Opcionalmente, puedes verificar por tu cuenta si user_id se puede convertir a int:
    # try:
    #     _ = int(user_id)
    # except ValueError:
    #     return await interaction.response.send_message("El ID proporcionado no es válido.", ephemeral=True)

    if user_id not in whitelist:
        whitelist.append(user_id)
        embed = discord.Embed(
            title="✅ Usuario Agregado a la Whitelist",
            description=f"El usuario con ID `{user_id}` ha sido agregado exitosamente a la whitelist.",
            color=discord.Color.green()
        )
        embed.set_footer(text="¡Ahora puede crear canales sin restricciones!")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Error",
            description=f"El usuario con ID `{user_id}` ya está en la whitelist.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)


# Comando para eliminar un usuario de la whitelist
@bot.tree.command(name="remove_whitelist", description="Elimina un usuario de la whitelist.")
async def remove_whitelist(interaction: discord.Interaction, user_id: int):
    if str(user_id) in whitelist:
        whitelist.remove(str(user_id))
        embed = discord.Embed(
            title="❌ Usuario Eliminado de la Whitelist",
            description=f"El usuario con ID `{user_id}` ha sido eliminado de la whitelist.",
            color=discord.Color.red()
        )
        embed.set_footer(text="Ya no podrá crear canales sin restricciones.")
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Error",
            description=f"El usuario con ID `{user_id}` no está en la whitelist.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)

# Comando para ver la lista de usuarios en la whitelist
@bot.tree.command(name="view_whitelist", description="Muestra la lista de usuarios en la whitelist.")
async def view_whitelist(interaction: discord.Interaction):
    if whitelist:
        embed = discord.Embed(
            title="📜 Lista de Usuarios en la Whitelist",
            description="Usuarios actuales en la whitelist:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Usuarios", value="\n".join(whitelist), inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="⚠️ Whitelist Vacía",
            description="No hay usuarios en la whitelist actualmente.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

# Evento cuando un canal es creado
@bot.event
async def on_guild_channel_create(channel):
    # Si el autor de la acción no está en la whitelist, lo banea
    if not is_whitelisted(channel.guild.owner.id):
        await channel.guild.owner.ban(reason="Creación de canal no permitida")
        embed = discord.Embed(
            title="❌ Canal Eliminado",
            description=f"El usuario con ID `{channel.guild.owner.id}` no estaba en la whitelist, por lo que su canal fue eliminado.",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)
    else:
        embed = discord.Embed(
            title="✅ Canal Creado Correctamente",
            description=f"El usuario con ID `{channel.guild.owner.id}` está en la whitelist y su canal ha sido creado.",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)



             #pedir rol

# Diccionario para almacenar los mensajes de solicitudes
solicitudes = {}

@bot.tree.command(name="pedirrol", description="Solicita un rol con un mensaje adicional.")
@app_commands.describe(contenido="Explica por qué solicitas el rol o deja tu mensaje.")
async def rol(interaction: discord.Interaction, contenido: str):
    try:
        # Crea el embed con color rojo y detalles llamativos
        embed = discord.Embed(
            title="🔥 **¡Solicitud de Rol Ingresada!** 🔥",
            description=f"¡Gracias por tu solicitud, {interaction.user.mention}! 🔥",
            color=discord.Color.red()  # Color rojo
        )

        # Imagen de cabecera llamativa
        embed.set_thumbnail(url="https://example.com/your-thumbnail-image.png")  # Cambia por tu imagen

        # Añadir más campos al embed con emojis y detalles llamativos
        embed.add_field(name="🧑‍💻 **Autor de la Solicitud**", value=interaction.user.mention, inline=False)
        embed.add_field(name="🔑 **ID del Usuario**", value=str(interaction.user.id), inline=True)
        embed.add_field(name="💬 **Mensaje de Solicitud**", value=contenido, inline=False)
        embed.add_field(name="📅 **Fecha de Solicitud**", value=interaction.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)
        embed.add_field(name="🔥 **Motivación del Usuario**", value="¡Vamos por ese rol, esperamos tu respuesta!", inline=False)
        embed.add_field(name="⏰ **Fecha Estimada de Revisión**", value="La revisión puede tomar entre 24-48 horas.", inline=True)

        # Cambiar las posiciones: mover "Progreso" y "Estado Actual"
        embed.add_field(name="📈 **Progreso**", value="🟩 **En proceso** 🟩", inline=False)
        embed.add_field(name="⏳ **Estado Actual**", value="🌀 **Pendiente** 🌀\n👀 *En espera de revisión por el staff*.", inline=False)

        # Añadir una imagen de fondo interactiva
        embed.set_image(url="https://example.com/your-background-image.png")  # Cambia por tu imagen de fondo

        # Añadir enlaces interactivos (si es necesario)
        embed.add_field(name="🔗 **Más Información**", value="[Haz clic aquí para más detalles](https://example.com)", inline=False)

        # Pie de página con un toque creativo
        embed.set_footer(text="🔮 Revisa tu solicitud mientras el staff lo evalúa. 🔮", icon_url="https://example.com/icon.png")

        # Envía el embed al canal
        message = await interaction.channel.send(embed=embed)

        # Guardar el mensaje de la solicitud para referencia
        solicitudes[interaction.user.id] = message.id

        # Añadir los emojis de "Sí" (✅) y "No" (❌) al mensaje
        await message.add_reaction("✅")
        await message.add_reaction("❌")

        # Responder al usuario confirmando que su solicitud fue enviada
        await interaction.response.send_message("✅ ¡Tu solicitud ha sido enviada y está en espera de revisión!", ephemeral=True)

    except Exception as e:
        # Manejo de errores si algo sale mal
        await interaction.response.send_message("❌ Hubo un error al procesar tu solicitud. Por favor, inténtalo nuevamente.", ephemeral=True)
        print(f"Error al procesar el comando 'pedirrol': {e}")


@bot.tree.command(name="cambiarestado", description="Cambiar el estado de una solicitud (Solo Admins).")
@app_commands.describe(usuario="El usuario cuya solicitud deseas cambiar", estado="El nuevo estado de la solicitud")
async def cambiar_estado(interaction: discord.Interaction, usuario: discord.User, estado: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ No tienes permisos para usar este comando.", ephemeral=True)
        return

    # Verificar si la solicitud existe
    if usuario.id not in solicitudes:
        await interaction.response.send_message(f"❌ No se ha encontrado ninguna solicitud para {usuario.mention}.", ephemeral=True)
        return

    # Obtener el mensaje de la solicitud
    message_id = solicitudes[usuario.id]
    message = await interaction.channel.fetch_message(message_id)

    # Obtener el embed del mensaje
    embed = message.embeds[0]

    # Determinar el nuevo estado y el emoji correspondiente
    if estado.lower() == "aceptado":
        nuevo_estado = "✅ **Aceptado** ✅\n🎉 *Felicidades, tu solicitud ha sido aceptada.*"
    elif estado.lower() == "negado":
        nuevo_estado = "❌ **Negado** ❌\n🚫 *Lo sentimos, tu solicitud ha sido rechazada.*"
    else:
        await interaction.response.send_message("❌ El estado no es válido. Usa 'aceptada' o 'negada'.", ephemeral=True)
        return

    # Cambiar el campo del estado al nuevo estado (ubicado ahora en "Estado Actual")
    embed.set_field_at(4, name="⏳ **Estado Actual**", value=nuevo_estado, inline=False)

    # Actualizar el mensaje con el nuevo embed
    await message.edit(embed=embed)

    # Enviar una respuesta confirmando la actualización
    await interaction.response.send_message(f"✅ El estado de la solicitud de {usuario.mention} ha sido actualizado a {nuevo_estado}.", ephemeral=True)

# Recuerda sincronizar los comandos de aplicación
# (por ejemplo, al iniciar tu bot en on_ready)
@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Comandos de barra sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Error al sincronizar comandos: {e}")






        #mute
@bot.tree.command(name="mute", description="Silencia a un usuario en el servidor.")
@app_commands.describe(member="El usuario que deseas silenciar", reason="Razón del mute")
async def mute(interaction: discord.Interaction, member: discord.Member, reason: str = "No especificado"):
    # Verificar que el moderador tenga permisos para gestionar roles
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ No tienes permisos para silenciar usuarios.", ephemeral=True)
        return
    
    # Verificar que el moderador no intente silenciarse a sí mismo
    if interaction.user == member:
        await interaction.response.send_message("❌ No puedes silenciarte a ti mismo.", ephemeral=True)
        return

    # Verificar que el bot tenga permisos para gestionar roles
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ El bot no tiene permisos para gestionar roles.", ephemeral=True)
        return

    try:
        # Modificar los permisos en los canales de texto para que no pueda enviar mensajes
        for channel in interaction.guild.text_channels:
            await channel.set_permissions(member, send_messages=False)

        # Modificar los permisos en los canales de voz para que no pueda hablar
        for channel in interaction.guild.voice_channels:
            await channel.set_permissions(member, speak=False)

        # Embed para confirmar el mute en el canal
        embed = discord.Embed(
            title="🔇 Usuario Silenciado",
            description=f"**{member.mention}** ha sido silenciado.\n\n**Razón:** {reason}",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Moderador: {interaction.user.name}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        # Respuesta oculta al moderador
        await interaction.response.send_message(f"✅ Has silenciado a {member.mention}.", ephemeral=True)

        # Mensaje público en el canal confirmando el mute
        await interaction.channel.send(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("❌ No tengo permisos suficientes para silenciar a este usuario.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ocurrió un error: {e}", ephemeral=True)

# para quitar el mute 

@bot.tree.command(name="unmute", description="Quita el mute a un usuario en el servidor.")
@app_commands.describe(member="El usuario al que deseas quitar el mute")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    # Verificar que el moderador tenga permisos para gestionar roles
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ No tienes permisos para quitar el mute de usuarios.", ephemeral=True)
        return
    
    # Verificar que el moderador no intente desmutearse a sí mismo
    if interaction.user == member:
        await interaction.response.send_message("❌ No puedes desmutearte a ti mismo.", ephemeral=True)
        return

    # Verificar que el bot tenga permisos para gestionar roles
    if not interaction.guild.me.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ El bot no tiene permisos para gestionar roles.", ephemeral=True)
        return

    try:
        # Restaurar los permisos en los canales de texto para que pueda enviar mensajes
        for channel in interaction.guild.text_channels:
            await channel.set_permissions(member, send_messages=None)

        # Restaurar los permisos en los canales de voz para que pueda hablar
        for channel in interaction.guild.voice_channels:
            await channel.set_permissions(member, speak=None)

        # Embed para confirmar el unmute en el canal
        embed = discord.Embed(
            title="🔊 Usuario Desmutado",
            description=f"**{member.mention}** ha sido desmutado.",
            color=discord.Color.green()
        )
        embed.set_footer(text=f"Moderador: {interaction.user.name}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

        # Respuesta oculta al moderador
        await interaction.response.send_message(f"✅ Has desmuteado a {member.mention}.", ephemeral=True)

        # Mensaje público en el canal confirmando el unmute
        await interaction.channel.send(embed=embed)

    except discord.Forbidden:
        await interaction.response.send_message("❌ No tengo permisos suficientes para desmutear a este usuario.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Ocurrió un error: {e}", ephemeral=True)

# Nota 
# Evento cuando el bot está listo
@bot.event
async def on_ready():
    # Mostrar mensaje en el perfil del bot (estado de presencia)
    print(f'¡Bot conectado como {bot.user}!')
    # Cambia el estado del bot, en este caso con un "Juego"
    await bot.change_presence(activity=discord.Game("¡Estoy en la nube!"))

# Comando para verificar si el bot está funcionando correctamente
@bot.command()
async def hola(ctx):
    await ctx.send("¡Hola! Estoy aquí para ayudarte.")





        # Comando Ping 🏓

# Supongamos que `bot.start_time` almacena el tiempo en el que se inició el bot
bot.start_time = time.time()

@bot.tree.command(name="ping", description="📡 Muestra la latencia y estado del bot.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)  # Latencia en ms
    api_latency = round(bot.ws.latency * 1000)  # Latencia del WebSocket
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Fecha y hora actual
    cpu_usage = psutil.cpu_percent()  # Uso de CPU
    memory_usage = psutil.virtual_memory().percent  # Uso de RAM
    disk_usage = psutil.disk_usage('/').percent  # Uso de Disco
    uptime_seconds = int(time.time() - bot.start_time)
    uptime = str(datetime.utcfromtimestamp(uptime_seconds).strftime('%H:%M:%S'))  # Tiempo activo

    server_count = len(bot.guilds)  # Servidores donde está el bot
    user_count = sum(guild.member_count for guild in bot.guilds)  # Usuarios totales

    # Emojis personalizados (REEMPLAZA LOS IDs)
    ping_emoji = "<a:rocket_animated:1349872075615244431>"  # Emoji animado de ping
    cpu_emoji = "<:CPU:1349874154005856321>"  # 💻 Reemplaza con ID real
    ram_emoji = "<a:HackerBongoCat:1349873018020691991>"  # 🧠 Reemplaza con ID real
    disk_emoji = "<a:Early_Verified_Bot_Developer_a:1349877585261363270>"  # 💾 Reemplaza con ID real
    uptime_emoji = "<a:MegaShout:1349874607594803210>"  # ⏳ Reemplaza con ID real
    clock_emoji = "<a:clock_running:1349871349526564868>"  # 🕒 Reemplaza con ID real
    globe_emoji = "<:fire:1349875398413910177>"  # 🌍 Reemplaza con ID real
    users_emoji = "<:members:1349875744683069490>"  # 👥 Reemplaza con ID real
    servers_emoji = "<:prohibition:1349875936807354378>"  # 🖥️ Reemplaza con ID real

    # Color dinámico según la latencia
    if latency < 100:
        color = discord.Color.green()
    elif 100 <= latency <= 200:
        color = discord.Color.yellow()
    else:
        color = discord.Color.red()

    # Embed con información completa
    embed = discord.Embed(
        title=f"{ping_emoji} Pong!",
        description="📊 **Estado actual del bot**",
        color=color
    )
    embed.set_thumbnail(url="")
    embed.set_footer(text=f"Solicitado por {interaction.user}", icon_url=interaction.user.display_avatar.url)

    embed.add_field(name=f"{ping_emoji} Latencia", value=f"`{latency}ms`", inline=True)
    embed.add_field(name=f"{globe_emoji} WebSocket", value=f"`{api_latency}ms`", inline=True)
    embed.add_field(name=f"{clock_emoji} Hora", value=f"`{current_time}`", inline=True)

    embed.add_field(name=f"{cpu_emoji} CPU", value=f"`{cpu_usage}%`", inline=True)
    embed.add_field(name=f"{ram_emoji} RAM", value=f"`{memory_usage}%`", inline=True)
    embed.add_field(name=f"{disk_emoji} Disco", value=f"`{disk_usage}%`", inline=True)

    embed.add_field(name=f"{uptime_emoji} Uptime", value=f"`{uptime}`", inline=True)
    embed.add_field(name=f"{servers_emoji} Servidores", value=f"`{server_count}`", inline=True)
    embed.add_field(name=f"{users_emoji} Usuarios", value=f"`{user_count}`", inline=True)

    await interaction.response.send_message(embed=embed)





bot.run('MTMzODM0MTQ3NjM2NjY4MDEyNQ.GpV1IR.vJmkz3nnIofClKucgJOcY_-nWelEbsT_kGi0oA')
