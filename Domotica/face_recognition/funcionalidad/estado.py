import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl

# Clase que renderiza HTML usando PyQt5 y lo convierte en imagen
class HTMLRenderer:
    def __init__(self, url="http://127.0.0.1:5500/Domotica/face_recognition/estructura/estado_casa.html"):
        # Asegura que solo exista una instancia de QApplication
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        # Crea un navegador web embebido con PyQt5
        self.web = QWebEngineView()
        self.web.load(QUrl(url))  # Carga la URL del contenido HTML
        self.web.resize(500, 500)  # Ajusta el tamaño de la ventana web
        self.web.show()  # Muestra el navegador 

        # Conecta la señal de carga completada a la función correspondiente
        self.web.loadFinished.connect(self.on_load_finished)

        # Temporizador para capturar la vista web en intervalos
        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_html)
        self.image = None  # Variable para almacenar la imagen capturada

    def on_load_finished(self, success):
        """Inicia la captura si la página se cargó correctamente."""
        if success:
            self.timer.start(500)  # Espera 500ms antes de capturar

    def capture_html(self):
        """Captura el contenido actual del navegador como imagen PNG."""
        self.web.grab().save("output.png")  # Guarda captura como archivo
        self.image = cv2.imread("output.png")  # Carga la imagen con OpenCV

    def get_image(self):
        """Devuelve la última imagen capturada desde el HTML."""
        return self.image

# Función principal del programa
def main():
    # Instancia la clase HTMLRenderer con la URL del HTML local
    renderer = HTMLRenderer("http://127.0.0.1:5500/Domotica/face_recognition/estructura/estado_casa.html")

    # Inicia la cámara
    cap = cv2.VideoCapture(0)
    cap.set(3, 1920)  # Ancho de la captura
    cap.set(4, 1080)  # Alto de la captura

    # Carga un diccionario ArUco (para detectar marcadores)
    diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
    parametros = cv2.aruco.DetectorParameters()

    # Usa el nuevo detector (OpenCV 4.7+)
    detector = cv2.aruco.ArucoDetector(diccionario, parametros)

    # Bucle principal
    while True:
        ret, frame = cap.read()  # Captura un frame de la cámara
        if not ret:
            continue  # Si no hay frame, se salta esta iteración

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Convierte a escala de grises
        esquinas, ids, _ = detector.detectMarkers(gray)  # Detecta marcadores ArUco

        if ids is not None and len(esquinas) > 0:
            # Dibuja los marcadores detectados sobre el frame
            cv2.aruco.drawDetectedMarkers(frame, esquinas)

            # Obtiene la imagen del contenido HTML
            imagen_html = renderer.get_image()
            if imagen_html is not None:
                # Coordenadas del marcador detectado (primer marcador)
                puntos_aruco = np.array(esquinas[0][0], dtype=np.float32)
                
                # Coordenadas de las esquinas de la imagen HTML
                puntos_imagen = np.array([
                    [0, 0],
                    [imagen_html.shape[1] - 1, 0],
                    [imagen_html.shape[1] - 1, imagen_html.shape[0] - 1], 
                    [0, imagen_html.shape[0] - 1]
                ], dtype=np.float32)

                # Calcula la homografía (transformación de perspectiva)
                h, _ = cv2.findHomography(puntos_imagen, puntos_aruco)
                # Aplica la transformación para ajustar la imagen HTML al marcador
                perspectiva = cv2.warpPerspective(imagen_html, h, (frame.shape[1], frame.shape[0]))

                # Rellena el área del marcador con negro antes de superponer la imagen
                cv2.fillConvexPoly(frame, puntos_aruco.astype(int), 0)
                # Superpone la imagen transformada sobre el frame original
                frame = cv2.addWeighted(frame, 1, perspectiva, 1, 0)

        # Muestra el resultado en una ventana
        cv2.imshow("Realidad Aumentada con WebSockets", frame)
        # Sale del bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera la cámara y destruye las ventanas
    cap.release()
    cv2.destroyAllWindows()

# Ejecuta el programa si es el script principal
if __name__ == "__main__":
    main()
