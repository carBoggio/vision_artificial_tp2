import cv2
import mediapipe as mp
import time
import numpy as np

class HandGestureDetector:
    def __init__(self):
        """Inicializa el detector de gestos de manos"""
        # Inicializar módulos de MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        
        # Variable para FPS
        self.p_time = 0
        
        # Variables para el puntero láser
        self.laser_points = []  # Lista para almacenar puntos del láser
        self.max_laser_points = 10  # Número máximo de puntos para la cola del láser
    
    def find_hands(self, img):
        """Detecta manos en la imagen y dibuja los landmarks"""
        if img is None:
            return None, None
            
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        index_pos = None
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
                # Obtener la posición del dedo índice
                h, w, _ = img.shape
                index_finger = hand_lms.landmark[8]  # Landmark 8 es la punta del dedo índice
                x, y = int(index_finger.x * w), int(index_finger.y * h)
                index_pos = (x, y)
        
        return img, index_pos
    
    def draw_laser_pointer(self, img, hand_landmarks):
        """Dibuja el puntero láser en la punta del dedo índice"""
        try:
            if img is None or hand_landmarks is None:
                return
                
            h, w, _ = img.shape
            
            # Verificar que el landmark 8 existe
            if len(hand_landmarks.landmark) <= 8:
                return
                
            # Obtener la posición del dedo índice (landmark 8)
            index_finger = hand_landmarks.landmark[8]
            x, y = int(index_finger.x * w), int(index_finger.y * h)
            
            # Verificar que las coordenadas están dentro de los límites de la imagen
            x = max(0, min(x, w-1))
            y = max(0, min(y, h-1))
            
            # Agregar el punto actual a la lista
            self.laser_points.append((x, y))
            
            # Mantener solo los últimos N puntos
            if len(self.laser_points) > self.max_laser_points:
                self.laser_points.pop(0)
            
            # Dibujar la cola del láser solo si hay más de un punto
            if len(self.laser_points) > 1:
                for i in range(len(self.laser_points) - 1):
                    # Verificar que los puntos existen
                    if i >= len(self.laser_points) or i+1 >= len(self.laser_points):
                        continue
                        
                    # Calcular el grosor basado en la posición en la cola
                    thickness = max(1, int((i + 1) * 2 / len(self.laser_points)))
                    # Calcular el color (rojo con transparencia)
                    alpha = (i + 1) / len(self.laser_points)
                    color = (0, 0, int(255 * alpha))
                    
                    # Obtener los puntos actuales
                    pt1 = self.laser_points[i]
                    pt2 = self.laser_points[i + 1]
                    
                    # Verificar que los puntos son válidos
                    if pt1 is not None and pt2 is not None:
                        # Dibujar la línea
                        cv2.line(img, pt1, pt2, color, thickness)
            
            # Dibujar el punto principal del láser
            cv2.circle(img, (x, y), 5, (0, 0, 255), -1)
            
        except Exception as e:
            print(f"Error en draw_laser_pointer: {str(e)}")
            # Limpiar los puntos del láser en caso de error
            self.laser_points = []
    
    def check_open_hand(self, hand_landmarks):
        """
        Verifica si la mano está abierta usando múltiples criterios:
        1. Los dedos están extendidos (las puntas están por encima de las articulaciones)
        2. La palma está plana (los puntos de la palma forman un plano)
        3. Los dedos están separados (hay espacio entre ellos)
        """
        """Verifica si la mano está haciendo el signo de paz (índice y medio arriba, anular y meñique abajo)"""
        # Puntos de referencia para las puntas de los dedos
        # 8, 12, 16, 20 = puntas del índice, medio, anular, meñique
        
        # Verificar posición de cada dedo (excepto pulgar)
        index_up = hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y
        middle_up = hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y
        ring_closed = hand_landmarks.landmark[16].y > hand_landmarks.landmark[14].y
        pinky_closed = hand_landmarks.landmark[20].y > hand_landmarks.landmark[18].y
        
        # Índice y medio arriba, anular y meñique abajo
        return index_up and middle_up and ring_closed and pinky_closed
    
    def is_doing_the_symbol(self, img):
        """Detecta el gesto de paz en la imagen"""
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if self.check_open_hand(hand_lms):
                    cv2.putText(img, "SIGNO DE PAZ DETECTADO!", 
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    return True  # Gesto de paz detectado
        return False
        
    def show_fps(self, img):
        """Muestra los FPS en la imagen"""
        current_time = time.time()
        fps = 1 / (current_time - self.p_time)
        self.p_time = current_time
        
        cv2.putText(img, f"{int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        
        return img