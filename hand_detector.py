import cv2
import mediapipe as mp
import time


cap = cv2.VideoCapture(0)  # Captura de video desde la cámara

mpHans = mp.solutions.hands  # Inicializa el módulo de manos de MediaPipe
hands = mpHans.Hands()  # Configura el detector de manos

# Moudlo para dibujar las manos
mpDraw = mp.solutions.drawing_utils  # Inicializa el módulo de dibujo de MediaPipe


while True:
    success, img = cap.read()  # Captura la imagen de la cámara
    if not success:
        break  # Sale del bucle si no se captura la imagen correctamente

    # Trabajar en la deteccion de manos
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convierte la imagen a RGB
    results = hands.process(imgRGB)  # Procesa la imagen para detectar manos
    print(results)  # Imprime los resultados de la detección
   
    if results.multi_hand_landmarks:  # Si se detectan manos
        for handLms in results.multi_hand_landmarks:  # Recorre las manos detectadas
            # Dibuja los puntos de referencia de la mano en la imagen
            mpDraw.draw_landmarks(img, handLms, mpHans.HAND_CONNECTIONS)
            
    # Calcular el tiempo actual y los FPS
    cv2.imshow("Imagen", img)  # Muestra la imagen capturada
    cv2.waitKey(1)  # Espera 1 milisegundo para mostrar la imagen
