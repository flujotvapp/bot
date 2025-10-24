import os
import time
import json
from telethon import TelegramClient, events

# 📌 Configura tus credenciales de Telegram
api_id = 25427468
api_hash = '911ddfed8a08e11d43940c7aa1675931'

# 📌 Configura los canales con un diccionario {origen: destino}
canales_mapeados = {
    -1001819222843: -1002403945427,  # flujo mayorista a flujo oficial
    -1001702806294: -1001809755552,  # entretenimientolat a play latino oficial
    -1002484204066: -1002403945427,  # Admins a flujo oficial
    -1001809755552: -1001647498192,  # Play latino oficial a Play latino
    -1002231971466: -1001848625541   #REGALOS DIGITALES a Emprendimientos VIP
}

# 🔹 Elimina la sesión anterior si está presente
session_file = "mi_sesion.session"
if os.path.exists(session_file):
    os.remove(session_file)

# Archivo para persistir el último mensaje procesado por cada canal
PERSISTENCE_FILE = "last_message_ids.json"

# Función para cargar el último mensaje procesado de cada canal desde el archivo
def load_last_message_ids():
    if os.path.exists(PERSISTENCE_FILE):
        with open(PERSISTENCE_FILE, "r") as f:
            try:
                data = json.load(f)
                # Convertir claves a enteros (ya que JSON las guarda como strings)
                return {int(k): v for k, v in data.items()}
            except Exception as e:
                print("Error al cargar el archivo de persistencia:", e)
                return {}
    else:
        return {}

# Función para guardar el estado en el archivo de persistencia
def save_last_message_ids():
    with open(PERSISTENCE_FILE, "w") as f:
        json.dump(last_message_ids, f)

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

# Diccionario para almacenar el último mensaje procesado en cada canal (se persistirá en un archivo)
last_message_ids = {}

# Función para inicializar last_message_ids, cargando el estado persistido y completando los canales faltantes
async def initialize_last_message_ids():
    global last_message_ids
    last_message_ids = load_last_message_ids()
    for origen in canales_mapeados.keys():
        if origen not in last_message_ids:
            try:
                mensajes = await client.get_messages(origen, limit=1)
                if mensajes:
                    last_message_ids[origen] = mensajes[0].id
                else:
                    last_message_ids[origen] = 0
            except Exception as e:
                print(f"Error al obtener mensajes iniciales del canal {origen}: {e}")
                last_message_ids[origen] = 0
    save_last_message_ids()

# Función para recuperar y reenviar mensajes perdidos tras reconexión
async def fetch_missed_messages():
    global last_message_ids
    for origen, destino in canales_mapeados.items():
        last_id = last_message_ids.get(origen, 0)
        print(f"Buscando mensajes perdidos en el canal {origen} con id mayor a {last_id}")
        # Se recorren los mensajes con id mayor a last_id en orden cronológico
        async for mensaje in client.iter_messages(origen, min_id=last_id, reverse=True):
            if mensaje.id > last_id:
                mensaje_texto = reemplazar_palabras(mensaje.text)
                if mensaje.media:
                    await client.send_file(destino, mensaje.media, caption=mensaje_texto if mensaje_texto else "")
                elif mensaje_texto:
                    await client.send_message(destino, mensaje_texto)
                else:
                    print("⚠️ Mensaje vacío o no soportado en la recuperación.")
                last_message_ids[origen] = mensaje.id
                print(f"Mensaje reenviado del canal {origen} con id {mensaje.id}")
                save_last_message_ids()

# Escucha nuevos mensajes y actualiza el último mensaje procesado, persistiendo el estado
@client.on(events.NewMessage(chats=list(canales_mapeados.keys())))
async def reenviar_mensaje(event):
    origen = event.chat_id
    mensaje = event.message
    mensaje_texto = reemplazar_palabras(mensaje.text)
    destino = canales_mapeados.get(origen)

    if origen not in last_message_ids or mensaje.id > last_message_ids[origen]:
        last_message_ids[origen] = mensaje.id
        save_last_message_ids()

    if destino:
        if mensaje.media:
            await client.send_file(destino, mensaje.media, caption=mensaje_texto if mensaje_texto else "")
        elif mensaje_texto:
            await client.send_message(destino, mensaje_texto)
        else:
            print("⚠️ Mensaje vacío o no soportado.")

# Bucle para reiniciar el bot en caso de error o desconexión (incluyendo apagones o detenciones)
while True:
    try:
        with client:
            print("🤖 Bot en ejecución...")
            # Inicializa el registro de último mensaje procesado (cargando el estado persistido)
            client.loop.run_until_complete(initialize_last_message_ids())
            # Tras reconectar, se buscan y reenvían los mensajes perdidos
            client.loop.run_until_complete(fetch_missed_messages())
            client.run_until_disconnected()
    except Exception as e:
        print("❌ Error detectado:", e)
        print("⏳ Reintentando en 5 segundos...")
        time.sleep(5)

