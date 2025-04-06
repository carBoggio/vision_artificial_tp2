import cv2
import time
import os

# variables 
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)      # Ancho
cap.set(4, hCam)      # Alto
listaOpciones = ["1", "2", "3", "4", "5"]

previus_time = 0



# Ir capturando las imagenes de la camara
while True: 

    print(listaOpciones[0])

    success, img = cap.read()  # Captura la imagen de la camara


    # Calcular el timpo actual y los FPS
    current_time = time.time()  # Obtiene el tiempo actual
    frames_per_second = 1 / (current_time - previus_time)  # Calcula los FPS
    previus_time = current_time  # Actualiza el tiempo previo
    # Escribir los FPS en la imagen
    cv2.putText(img, str(int(frames_per_second)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)  # Escribe los FPS en la imagen




    cv2.imshow("Imagen", img)  # Muestra la imagen capturada
    cv2.waitKey(1)  # Espera 1 milisegundo para mostrar la imagen

