import cv2
import mediapipe as mp
import time

# Variables de configuración
cap = cv2.VideoCapture(0)
mpHands = mp.solutions.hands
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mpDraw = mp.solutions.drawing_utils
pTime = 0

def check_peace_sign(hand_landmarks):
    # Definir los puntos de referencia para las puntas de los dedos
    finger_tips = [4, 8, 12, 16, 20]  # Pulgar, índice, medio, anular, meñique
    
    # Verificar si el pulgar está cerrado (comparación con la base del pulgar)
    thumb_closed = hand_landmarks.landmark[finger_tips[0]].x < hand_landmarks.landmark[finger_tips[0]-1].x
    
    # Verificar si el índice está levantado
    index_up = hand_landmarks.landmark[finger_tips[1]].y < hand_landmarks.landmark[finger_tips[1]-2].y
    
    # Verificar si el medio está levantado
    middle_up = hand_landmarks.landmark[finger_tips[2]].y < hand_landmarks.landmark[finger_tips[2]-2].y
    
    # Verificar si el anular está cerrado
    ring_closed = hand_landmarks.landmark[finger_tips[3]].y > hand_landmarks.landmark[finger_tips[3]-2].y
    
    # Verificar si el meñique está cerrado
    pinky_closed = hand_landmarks.landmark[finger_tips[4]].y > hand_landmarks.landmark[finger_tips[4]-2].y
    
    # Devolver verdadero solo si índice y medio están levantados y el resto cerrados
    return index_up and middle_up and thumb_closed and ring_closed and pinky_closed

def main():
    global pTime
    
    while True:
        success, img = cap.read()
        if not success:
            break
        
        img = cv2.flip(img, 1)  # Espejo
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                # Dibujar puntos de la mano
                mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
                
                # Verificar si se está haciendo el signo de paz (índice y medio arriba, resto abajo)
                if check_peace_sign(handLms):
                    cv2.putText(img, "SIGNO DE PAZ DETECTADO!", 
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Mostrar FPS
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f"{int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        
        # Mostrar imagen
        cv2.imshow("Hand Tracking", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()