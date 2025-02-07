import os
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# 📌 Configura tus credenciales de Telegram
api_id = 25427468
api_hash = '911ddfed8a08e11d43940c7aa1675931'

# 📌 Configura los canales con un diccionario {origen: destino}
canales_mapeados = {
    -1001819222843: -1002403945427,  # Canal 1 → Canal A (flujo mayorista a flujo oficial)
    -1001702806294: -1001809755552,  # Canal 2 → Canal B (entretenimientolat a play latino oficial)
    -1002484204066: -1002403945427,  # Admins a flujo oficial
    -1001809755552: -1001647498192,  # Play latino oficial a Play latino
    -1002262623789: -1002290744520   # Marcellvip a VIP Trading
}

# 🔹 Elimina la sesión anterior si está presente
session_file = "mi_sesion.session"
if os.path.exists(session_file):
    os.remove(session_file)

# 🔹 Crea la sesión con tu cuenta de Telegram
client = TelegramClient('mi_sesion', api_id, api_hash)

# Diccionario de palabras/frases prohibidas y sus reemplazos específicos
reemplazos = {
    '@Marcellfx': '',
    'https://wa.me/message/5QK7PX2NDTWQH1': 'https://wa.me/+5545999151749',
    '@entretenimientolat': '@playslatino'
}

# Función para reemplazar las palabras/frases prohibidas con su reemplazo específico
def reemplazar_palabras(texto):
    if texto:  # Evita errores si el texto es None
        for palabra, reemplazo in reemplazos.items():
            texto = texto.replace(palabra, reemplazo)
    return texto

# 🔹 Escucha nuevos mensajes en los canales de origen
@client.on(events.NewMessage(chats=list(canales_mapeados.keys())))
async def reenviar_mensaje(event):
    canal_origen = event.chat_id
    canal_destino = canales_mapeados.get(canal_origen)  # Obtiene el canal destino correspondiente

    if canal_destino:
        mensaje = event.message
        mensaje_texto = reemplazar_palabras(mensaje.text)

        # 🔹 Verifica si el mensaje es una respuesta a otro
        if mensaje.reply_to_msg_id:
            mensaje_original = await client.get_messages(canal_origen, ids=mensaje.reply_to_msg_id)
            texto_original = reemplazar_palabras(mensaje_original.text)

            if texto_original:
                mensaje_texto = f"📩 *Respondiendo a:* {texto_original}\n\n{mensaje_texto or ''}"

        # 🔹 Si el mensaje tiene una imagen, video o documento, lo reenvía con la descripción corregida
        if mensaje.media:
            await client.send_file(
                canal_destino,
                mensaje.media,
                caption=mensaje_texto if mensaje_texto else ""  # Adjunta la descripción modificada
            )
        elif mensaje_texto:  # Si es solo texto, lo reenvía directamente
            await client.send_message(canal_destino, mensaje_texto)
        else:
            print("⚠️ Mensaje vacío o no soportado.")

# 🔹 Inicia el bot
with client:
    print("🤖 Bot en ejecución...")
    client.run_until_disconnected()
