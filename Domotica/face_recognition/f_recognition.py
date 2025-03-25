import cv2
import os
import face_recognition
import asyncio
import websockets
import base64
import numpy as np
import openai

# Configuracion de la ApiKey de OpenAI
openai.api_key = "ApiKey"

# Configuración del servidor WebSocket
HOST = "0.0.0.0"  # Dirección en la que el servidor escuchará conexiones
PORT = 3000  # Puerto del servidor WebSocket

# Ruta donde se almacenan las imágenes de las caras registradas
imageFacesPath = "C:/Users/HOME/Desktop/Semestre 7/Domotica2/Domotica/faces"

# Listas para almacenar codificaciones faciales y nombres de las personas registradas
facesEncodings = []
facesNames = []

# Cargar imágenes y generar codificaciones faciales
for file_name in os.listdir(imageFacesPath):
    image = cv2.imread(os.path.join(imageFacesPath, file_name))  # Cargar imagen
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
    encodings = face_recognition.face_encodings(image)  # Obtener codificación facial
    if encodings:
        facesEncodings.append(encodings[0])  # Guardar la codificación
        facesNames.append(file_name.split(".")[0])  # Guardar el nombre de la persona

# Estado del servo (cerrado por defecto)
servo_abierto = True 

# Estado de los sensores
sensor1_estado = 0
sensor2_estado = 0

# Conjunto para almacenar clientes WebSocket conectados
websocket_clients = set()

# Función para enviar mensajes a todos los clientes conectados
async def send_message_to_clients(message):
    if websocket_clients:
        await asyncio.gather(*(client.send(message) for client in websocket_clients))

# Función para obtener respuesta de GPT-4 con información del servo y sensores
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
        return f"Error al conectar con GPT: {e}"

# Manejo de la conexión con los clientes WebSocket
async def handle_connection(websocket, path):
    global servo_abierto, sensor1_estado, sensor2_estado
    websocket_clients.add(websocket)  # Agregar cliente a la lista de conexiones activas
    
    try:
        async for message in websocket:
            # Procesar mensajes de sensores
            if message.startswith("sensors:"):
                sensor_values = message.split(":")[1]
                sensor1_estado, sensor2_estado = map(int, sensor_values.split(","))

                if sensor1_estado == 1:
                    await send_message_to_clients("Sensor D5 detectó un objeto")
                elif sensor2_estado == 1:
                    await send_message_to_clients("Sensor D6 detectó un objeto")
                else:
                    await send_message_to_clients("Sin detección")

            # Procesar imagen para reconocimiento facial
            elif message.startswith("data:image/png;base64,"):
                image_data = message.split(",")[1]  # Obtener los datos de la imagen en base64
                image_bytes = base64.b64decode(image_data)  # Decodificar base64
                nparr = np.frombuffer(image_bytes, np.uint8)  # Convertir a numpy array
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)  # Decodificar imagen
                
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
                face_encodings = face_recognition.face_encodings(image)  # Obtener codificación facial

                if face_encodings:
                    match = face_recognition.compare_faces(facesEncodings, face_encodings[0])  # Comparar con caras registradas
                    if True in match:
                        if not servo_abierto:
                            print("Persona reconocida, abriendo servo...")
                            await send_message_to_clients("1")  # Enviar señal para abrir el servo
                            servo_abierto = True
                    else:
                        print("Persona no reconocida, no se abre el servo.")
                else:
                    print("No se detectó rostro, cerrando servo.")
                    if servo_abierto:
                        await send_message_to_clients("0")  # Enviar señal para cerrar el servo
                        servo_abierto = False

            # Procesar mensajes para GPT
            elif message.startswith("gpt:"):
                pregunta = message[4:]  # Extraer la pregunta del usuario
                respuesta = await obtener_respuesta_gpt(pregunta)  # Obtener respuesta de GPT
                await send_message_to_clients(f"gpt_response:{respuesta}")  # Enviar respuesta al cliente

            # Comando manual para cerrar el servo
            if message == "cerrar":
                print("Cerrando servo manualmente...")
                await send_message_to_clients("0")  # Enviar señal de cierre
                servo_abierto = False

    finally:
        websocket_clients.remove(websocket)  # Remover cliente al desconectarse

# Iniciar el servidor WebSocket
loop = asyncio.new_event_loop()  # Crear un nuevo bucle de eventos
asyncio.set_event_loop(loop)  # Establecer el bucle de eventos como el actual
start_server = websockets.serve(handle_connection, HOST, PORT)  # Configurar el servidor WebSocket

print(f"Servidor WebSocket iniciado en {HOST}:{PORT}")
loop.run_until_complete(start_server)  # Iniciar el servidor
loop.run_forever()  # Mantener el servidor en ejecución
