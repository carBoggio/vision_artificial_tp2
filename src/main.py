import os
import sys
import time
import cv2
from PDFViewer import PDFViewer
from hand_detector import HandGestureDetector

def main():
    """
    Función principal que ejecuta el visor de PDF con detección de gestos.
    Pasa a la siguiente diapositiva cuando se detecta el gesto de paz.
    """
    # Inicializar la cámara
    cap = cv2.VideoCapture(0)  # 0 para la cámara predeterminada
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return
    
    # Crear el detector de gestos
    detector = HandGestureDetector()
    
    # Crear el visor de PDF
    viewer = PDFViewer()
    
    # Obtener la ruta del archivo de la línea de comandos si se proporciona
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        # Verificar si el archivo existe
        if not os.path.exists(pdf_path):
            print(f"Error: No se encontró el archivo '{pdf_path}'")
        elif not pdf_path.lower().endswith('.pdf'):
            print(f"Error: El archivo '{pdf_path}' no es un PDF")
        else:
            # Cargar el PDF
            viewer.load_pdf(pdf_path)
    
    # Variables para controlar el cambio de diapositivas
    last_page_change_time = time.time()
    cooldown_period = 2.0  # Tiempo de espera entre cambios de página por gesto (segundos)
    peace_gesture_detected = False
    
    # Bucle principal que combina la detección de gestos y la presentación
    try:
        while True:
            # Actualizar la interfaz gráfica
            if not viewer.update():
                break  # Salir si la ventana fue cerrada
            
            # Capturar frame de la cámara
            ret, frame = cap.read()
            if not ret:
                print("Error: No se pudo leer el frame de la cámara.")
                break
            
            # Voltear horizontalmente para una visualización más intuitiva
            frame = cv2.flip(frame, 1)
            
            # Detectar manos y dibujar landmarks
            frame = detector.find_hands(frame)
            
            # Tiempo actual
            current_time = time.time()
            
            # Verificar si se está haciendo el gesto de paz
            if detector.is_doing_the_symbol(frame):
                if not peace_gesture_detected and (current_time - last_page_change_time > cooldown_period):
                    # Cambiar de página
                    viewer.next()
                    last_page_change_time = current_time
                    peace_gesture_detected = True
            else:
                peace_gesture_detected = False
            
            # Mostrar FPS
            frame = detector.show_fps(frame)
            
            # Mostrar el frame con la detección
            cv2.imshow("Detección de Gestos", frame)
            
            # Salir si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            
            # Si la presentación está en modo automático, cambiar de página cada segundo
            if viewer.is_running() and (current_time - last_page_change_time > 1.0):
                viewer.next()
                last_page_change_time = current_time
                time.sleep(2)
            # Pequeña pausa para no saturar la CPU
            time.sleep(0.01)
                
    except KeyboardInterrupt:
        print("Programa interrumpido por el usuario")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        # Liberar recursos
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()