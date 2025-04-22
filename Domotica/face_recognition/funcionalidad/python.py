import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QTimer, QUrl

class HTMLRenderer:
    def __init__(self, url="http://127.0.0.1:5500/Domotica/face_recognition/estructura/estado_casa.html"):
        # Aseguramos que QApplication existe antes de crear QWebEngineView
        if not QApplication.instance():
            self.app = QApplication(sys.argv)
        else:
            self.app = QApplication.instance()

        self.web = QWebEngineView()
        self.web.load(QUrl(url))
        self.web.resize(500, 500)
        self.web.show()

        # Conectar la señal correctamente
        self.web.loadFinished.connect(self.on_load_finished)

        self.timer = QTimer()
        self.timer.timeout.connect(self.capture_html)
        self.image = None

    def on_load_finished(self, success):
        """Inicia la captura solo si la página se cargó correctamente."""
        if success:
            self.timer.start(500)  # Retraso antes de la primera captura

    def capture_html(self):
        """Captura el contenido del navegador como imagen."""
        self.web.grab().save("output.png")
        self.image = cv2.imread("output.png")

    def get_image(self):
        """Devuelve la última imagen capturada."""
        return self.image

def main():
    renderer = HTMLRenderer("http://127.0.0.1:5500/Domotica/face_recognition/estructura/estado_casa.html")

    cap = cv2.VideoCapture(0)
    cap.set(3, 1920)
    cap.set(4, 1080)

    diccionario = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
    parametros = cv2.aruco.DetectorParameters()

    # Para OpenCV 4.7+ usa ArucoDetector
    detector = cv2.aruco.ArucoDetector(diccionario, parametros)

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        esquinas, ids, _ = detector.detectMarkers(gray)

        if ids is not None and len(esquinas) > 0:
            cv2.aruco.drawDetectedMarkers(frame, esquinas)

            imagen_html = renderer.get_image()
            if imagen_html is not None:
                puntos_aruco = np.array(esquinas[0][0], dtype=np.float32)
                puntos_imagen = np.array([
                    [0, 0], [imagen_html.shape[1] - 1, 0],
                    [imagen_html.shape[1] - 1, imagen_html.shape[0] - 1], 
                    [0, imagen_html.shape[0] - 1]
                ], dtype=np.float32)

                h, _ = cv2.findHomography(puntos_imagen, puntos_aruco)
                perspectiva = cv2.warpPerspective(imagen_html, h, (frame.shape[1], frame.shape[0]))

                cv2.fillConvexPoly(frame, puntos_aruco.astype(int), 0)
                frame = cv2.addWeighted(frame, 1, perspectiva, 1, 0)

        cv2.imshow("Realidad Aumentada con WebSockets", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
