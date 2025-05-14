import cv2
import os
import face_recognition
import asyncio
import websockets
import base64
import numpy as np
import openai

# Configuración de la ApiKey de OpenAI 
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 


# Configuración del servidor WebSocket
HOST = "0.0.0.0"
PORT = 3000

# Ruta donde se almacenan las imágenes de las caras registradas
imageFacesPath = "C:/Users/HOME/Desktop/Semestre 7/Domotica2/Domotica/faces"

# Listas para codificaciones y nombres
facesEncodings = []
facesNames = []

# Cargar imágenes y codificar rostros
for file_name in os.listdir(imageFacesPath):
    image = cv2.imread(os.path.join(imageFacesPath, file_name))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    encodings = face_recognition.face_encodings(image)
    if encodings:
        facesEncodings.append(encodings[0])
        facesNames.append(file_name.split(".")[0])

# Estados iniciales
servo_abierto = True
sensor1_estado = 0
sensor2_estado = 0

# Clientes conectados
websocket_clients = set()

# Enviar mensaje a todos los clientes conectados
async def send_message_to_clients(message):
    if websocket_clients:
        await asyncio.gather(*(client.send(message) for client in websocket_clients))

# Generar respuesta de GPT con estado del sistema
async def obtener_respuesta_gpt(mensaje):
    try:
        estado_servo = "abierto" if servo_abierto else "cerrado"
        estado_sensor1 = "detectó un objeto" if sensor1_estado == 1 else "no detectó nada"
        estado_sensor2 = "detectó un objeto" if sensor2_estado == 1 else "no detectó nada"

        contexto = (
            f"El servo está actualmente {estado_servo}. "
            f"El sensor D5 {estado_sensor1}. "
            f"El sensor D6 {estado_sensor2}."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": contexto},
                {"role": "user", "content": mensaje}
            ]
        )
        return response["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"Error al procesar la solicitud de GPT: {str(e)}")
        return f"Error al conectar con GPT: {e}"

# Manejo de conexión WebSocket
async def handle_connection(websocket):
    global servo_abierto, sensor1_estado, sensor2_estado
    websocket_clients.add(websocket)

    try:
        async for message in websocket:

            # Procesar datos de sensores
            if message.startswith("sensors:"):
                sensor_values = message.split(":")[1]
                sensor1_estado, sensor2_estado = map(int, sensor_values.split(","))

                if sensor1_estado == 1:
                    await send_message_to_clients("Sensor D5 detecto un objeto")
                else:
                    await send_message_to_clients("Sensor D5 sin deteccion")

                if sensor2_estado == 1:
                    await send_message_to_clients("Sensor D6 detecto un objeto")
                else:
                    await send_message_to_clients("Sensor D6 sin deteccion")

            # Procesar imagen facial
            elif message.startswith("data:image/png;base64,"):
                image_data = message.split(",")[1]
                image_bytes = base64.b64decode(image_data)
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    match = face_recognition.compare_faces(facesEncodings, face_encodings[0])
                    if True in match:
                        if not servo_abierto:
                            print("Persona reconocida, abriendo servo...")
                            await send_message_to_clients("1")
                            servo_abierto = True
                    else:
                        print("Persona no reconocida, no se abre el servo.")
                else:
                    print("No se detectó rostro, cerrando servo.")
                    if servo_abierto:
                        await send_message_to_clients("0")
                        servo_abierto = False

            # Procesar preguntas para GPT
            elif message.startswith("gpt:"):
                pregunta = message[4:]
                respuesta = await obtener_respuesta_gpt(pregunta)
                await send_message_to_clients(f"gpt_response:{respuesta}")

            # Cierre manual del servo
            elif message == "cerrar":
                print("Cerrando servo manualmente...")
                await send_message_to_clients("0")
                servo_abierto = False

    finally:
        websocket_clients.remove(websocket)

# Iniciar servidor WebSocket
async def main():
    async with websockets.serve(handle_connection, HOST, PORT):
        print(f"Servidor WebSocket iniciado en {HOST}:{PORT}")
        await asyncio.Future()  # Mantiene el servidor corriendo indefinidamente

asyncio.run(main())
