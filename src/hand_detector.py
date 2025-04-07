import cv2
import mediapipe as mp
import time

class HandGestureDetector:
    def __init__(self):
        """Inicializa el detector de gestos de manos"""
        # Inicializar módulos de MediaPipe
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils
        
        # Variable para FPS
        self.p_time = 0
    
    def find_hands(self, img):
        """Detecta manos en la imagen y dibuja los landmarks"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        
        return img
    
    def check_peace_sign(self, hand_landmarks):
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
                if self.check_peace_sign(hand_lms):
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