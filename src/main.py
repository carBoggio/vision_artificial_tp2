import os
import sys
import time
import tkinter as tk
from tkinter import messagebox
from PDFViewer import PDFViewer

def main():
    """
    Función principal que inicializa la aplicación con un bucle while.
    
    Esta implementación usa un while True explícito para el control de la presentación,
    en lugar de usar el sistema de eventos de tkinter.
    """
    # Verificar si se pasó un archivo como argumento
    pdf_path = None
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        # Verificar si el archivo existe
        if not os.path.exists(pdf_path):
            print(f"Error: No se encontró el archivo '{pdf_path}'")
            pdf_path = None
        # Verificar si es un PDF
        elif not pdf_path.lower().endswith('.pdf'):
            print(f"Error: El archivo '{pdf_path}' no es un PDF")
            pdf_path = None
    
    # Crear la ventana principal
    root = tk.Tk()
    
    # Modificar PDFViewer para que no use after() para la presentación
    # Esto lo manejará nuestro bucle while
    original_start_slideshow = PDFViewer.start_slideshow
    original_change_page = PDFViewer.change_page
    
    def custom_start_slideshow(self):
        if not self.pdf_document or self.running:
            return
        self.running = True
        self.btn_stop.config(state=tk.NORMAL)
        # No programamos cambio de página aquí, lo hará el bucle while
    
    def custom_change_page(self):
        if not self.running:
            return
        self.next_page()
        if self.current_page >= len(self.pdf_document) - 1:
            self.current_page = -1  # La próxima vez será 0
        # No programamos el siguiente cambio aquí, lo hará el bucle while
    
    # Reemplazar los métodos para que no usen after()
    PDFViewer.start_slideshow = custom_start_slideshow
    PDFViewer.change_page = custom_change_page
    
    # Inicializar la aplicación con la ruta del archivo (si existe)
    app = PDFViewer(root, pdf_path)
    
    # Configurar el evento de redimensionado para ajustar las páginas al tamaño de la ventana
    def on_resize(event):
        if hasattr(app, 'pdf_document') and app.pdf_document:
            app.show_current_page()
    
    root.bind("<Configure>", on_resize)
    
    # Bucle while simplificado, sin necesidad de variables de control de tiempo
    
    try:
        # Bucle principal personalizado con while True
        while True:
            # Actualizar la interfaz de tkinter (equivalente a mainloop pero controlado por nosotros)
            root.update_idletasks()
            root.update()
            
            # Si estamos en modo presentación, cambiar página después del sleep de 1 segundo
            if app.running:
                app.change_page()  # Nuestro método personalizado
                
            # Dormir simplemente 1 segundo entre cambios cuando estamos en modo presentación
            if app.running:
                time.sleep(1)  # Dormir exactamente 1 segundo
            else:
                # Si no estamos en presentación, solo una pausa pequeña para no saturar la CPU
                time.sleep(0.01)
            
    except tk.TclError as e:
        # Capturar el error cuando se cierra la ventana
        if 'application has been destroyed' not in str(e):
            messagebox.showerror("Error", f"Se produjo un error: {str(e)}")
    except Exception as e:
        messagebox.showerror("Error", f"Se produjo un error: {str(e)}")
    finally:
        # Restaurar los métodos originales por si se necesita
        PDFViewer.start_slideshow = original_start_slideshow
        PDFViewer.change_page = original_change_page

if __name__ == "__main__":
    main()