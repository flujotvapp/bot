import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument  # Eliminar MessageMediaVideo

# Configura tus credenciales de Telegram
api_id = 25427468
api_hash = '911ddfed8a08e11d43940c7aa1675931'

# Configura los canales
canal_origen = -1001702806294  # ID del canal de origen
canal_destino = -1001809755552  # ID del canal de destino

# Elimina la sesión anterior si está presente
if os.path.exists("mi_sesion.session"):
    os.remove("mi_sesion.session")

# Crea la sesión con tu cuenta de Telegram
client = TelegramClient('mi_sesion', api_id, api_hash)

# Escucha nuevos mensajes en el canal de origen
@client.on(events.NewMessage(chats=canal_origen))
async def reenviar_mensaje(event):
    mensaje = event.message

    if mensaje.text:
        await client.send_message(canal_destino, mensaje.text)
    elif mensaje.media:
        if isinstance(mensaje.media, MessageMediaPhoto):
            await client.send_file(canal_destino, mensaje.media.photo)
        elif isinstance(mensaje.media, MessageMediaDocument):  # Videos también son documentos
            await client.send_file(canal_destino, mensaje.media.document)
        else:
            print(f"Tipo de medio no soportado: {type(mensaje.media)}")
    else:
        print("Mensaje vacío o no soportado.")

# Inicia el cliente
with client:
    print("Bot en ejecución...")
    client.run_until_disconnected()
