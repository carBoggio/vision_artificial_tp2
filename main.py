import cv2
from hand_detector import HandDetector
from swipe_detector import SwipeDetector
from utils import display_info_on_frame

def calibrate_skin_detector():
    """Función para calibrar manualmente los parámetros de detección de piel"""
    cap = cv2.VideoCapture(0)
    detector = HandDetector()
    
    # Crear trackbars para ajustar parámetros de detección de piel
    cv2.namedWindow('Calibration')
    cv2.createTrackbar('Lower H', 'Calibration', detector.lower_skin[0], 179, lambda x: None)
    cv2.createTrackbar('Lower S', 'Calibration', detector.lower_skin[1], 255, lambda x: None)
    cv2.createTrackbar('Lower V', 'Calibration', detector.lower_skin[2], 255, lambda x: None)
    cv2.createTrackbar('Upper H', 'Calibration', detector.upper_skin[0], 179, lambda x: None)
    cv2.createTrackbar('Upper S', 'Calibration', detector.upper_skin[1], 255, lambda x: None)
    cv2.createTrackbar('Upper V', 'Calibration', detector.upper_skin[2], 255, lambda x: None)
    
    print("Calibre los parámetros de detección de piel usando los trackbars.")
    print("Presione 'c' para confirmar la calibración y comenzar la detección.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Actualizar parámetros desde trackbars
        detector.lower_skin[0] = cv2.getTrackbarPos('Lower H', 'Calibration')
        detector.lower_skin[1] = cv2.getTrackbarPos('Lower S', 'Calibration')
        detector.lower_skin[2] = cv2.getTrackbarPos('Lower V', 'Calibration')
        detector.upper_skin[0] = cv2.getTrackbarPos('Upper H', 'Calibration')
        detector.upper_skin[1] = cv2.getTrackbarPos('Upper S', 'Calibration')
        detector.upper_skin[2] = cv2.getTrackbarPos('Upper V', 'Calibration')
        
        # Procesar frame
        skin_mask = detector.detect_skin(frame)
        
        # Mostrar resultados
        cv2.imshow('Original', frame)
        cv2.imshow('Skin Mask', skin_mask)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return None  # Salir sin calibrar
        elif key == ord('c'):
            return detector  # Confirmar calibración
    
    cap.release()
    cv2.destroyAllWindows()
    return None

def main():
    print("Programa de detección de gestos: deslizamiento rápido de izquierda a derecha")
    print("\n1. Iniciar con calibración manual")
    print("2. Usar valores predeterminados")
    
    choice = input("\nSeleccione una opción (1-2): ")
    
    if choice == '1':
        hand_detector = calibrate_skin_detector()
        if hand_detector is None:
            print("Calibración cancelada. Usando valores predeterminados.")
            hand_detector = HandDetector()
    else:
        hand_detector = HandDetector()
    
    # Crear detector de deslizamiento
    swipe_detector = SwipeDetector()
    
    # Iniciar captura de video
    cap = cv2.VideoCapture(0)
    
    # Verificar si se pudo abrir la cámara
    if not cap.isOpened():
        print("Error: No se pudo acceder a la cámara.")
        return
    
    # Configurar ventanas
    cv2.namedWindow('Detección de Gesto')
    
    print("\nPrograma iniciado. Realice el gesto de deslizamiento de izquierda a derecha.")
    print("Presione 'q' para salir, 'r' para reiniciar estadísticas, 'm' para marcar intento fallido.")
    
    # Contador de gestos detectados para estadísticas
    successful_detections = 0
    total_attempts = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Voltear horizontalmente para que sea más intuitivo
        frame = cv2.flip(frame, 1)
        
        # Detectar piel y encontrar contorno de la mano
        skin_mask = hand_detector.detect_skin(frame)
        hand_contour, area = hand_detector.find_largest_contour(skin_mask)
        
        # Crear copia del frame para dibujar
        output = frame.copy()
        
        # Si se encontró una mano
        hand_center = None
        if hand_contour is not None:
            # Dibujar contorno
            cv2.drawContours(output, [hand_contour], 0, (0, 255, 0), 2)
            
            # Obtener y dibujar centro
            hand_center = hand_detector.get_hand_center(hand_contour)
            if hand_center:
                cv2.circle(output, hand_center, 5, (0, 0, 255), -1)
        
        # Actualizar trayectoria y detectar deslizamiento
        swipe_detector.track_movement(hand_center)
        swipe_detector.draw_trajectory(output)
        swipe_detected, confidence = swipe_detector.detect_swipe()
        
        # Actualizar estadísticas si se detectó un gesto
        if swipe_detected and confidence > 90:
            successful_detections += 1
            total_attempts += 1
        
        # Mostrar información en el frame
        display_info_on_frame(output, swipe_detected, confidence, 
                             successful_detections, total_attempts)
        
        # Mostrar resultados
        cv2.imshow('Detección de Gesto', output)
        cv2.imshow('Máscara de Piel', skin_mask)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # Reiniciar estadísticas
            successful_detections = 0
            total_attempts = 0
        elif key == ord('m'):
            # Marcar manualmente un intento fallido
            total_attempts += 1
    
    # Mostrar estadísticas finales
    if total_attempts > 0:
        print(f"\nEstadísticas finales:")
        print(f"Gestos correctamente detectados: {successful_detections}/{total_attempts}")
        print(f"Precisión: {successful_detections/total_attempts*100:.2f}%")
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()