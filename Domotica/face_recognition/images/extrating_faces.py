# Importamos las librerías necesarias
import cv2  # OpenCV para procesamiento de imágenes
import os  # Para interactuar con el sistema de archivos


# Definir la ruta donde están almacenadas las imágenes de entrada
imagesPath = "C:/Users/HOME/Desktop/Semestre 7/Domotica/face_recognition/images/input_images"

# Verificar si existe la carpeta "faces" donde se guardarán los rostros detectados
if not os.path.exists("faces"):
    os.makedirs("faces")  # Crear la carpeta si no existe
    print("Nueva carpeta: faces") 
    
# Cargar el clasificador de rostros de OpenCV (Haarcascade)
faceClassif = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# Contador para nombrar los archivos de las imágenes de rostros recortados
count = 0

# Recorrer todas las imágenes dentro del directorio de entrada
for imageName in os.listdir(imagesPath):

    print(imageName)  # Imprimir el nombre de la imagen que se está procesando

    # Cargar la imagen desde la ruta especificada
    image = cv2.imread(os.path.join(imagesPath, imageName))

    # Verificar si la imagen se cargó correctamente
    if image is None:
        print(f"No se pudo cargar la imagen {imageName}")  # Mensaje de error
        continue  # Pasar a la siguiente imagen

    # Detectar rostros en la imagen usando el clasificador Haarcascade
    faces = faceClassif.detectMultiScale(image, 1.1, 5)  # Escaneo con factor de escala 1.1 y mínimo 5 vecinos

    # Recorrer todas las detecciones de rostros encontradas en la imagen
    for (x, y, w, h) in faces:
        face = image[y:y + h, x:x + w]  # Recortar la región de la imagen donde se detectó el rostro
        face = cv2.resize(face, (150, 150))  # Redimensionar el rostro detectado a 150x150 píxeles
        cv2.imwrite(f"faces/{count}.jpg", face)  # Guardar la imagen recortada en la carpeta "faces"
        count += 1  # Incrementar el contador de imágenes guardadas

