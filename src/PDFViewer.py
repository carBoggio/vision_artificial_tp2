import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFViewer:
    def __init__(self):
        # Crear la ventana principal
        self.root = tk.Tk()
        self.root.title("Visor de PDF")
        self.root.geometry("800x600")
        
        # Variables de estado
        self.pdf_document = None
        self.pages = []
        self.current_page = 0
        self.running = False
        self.zoom_factor = 1.0
        
        # Variables para el puntero láser
        self.laser_points = []  # Lista para almacenar puntos del láser
        self.max_laser_points = 10  # Número máximo de puntos para la cola del láser
        
        # Interfaz gráfica
        self._setup_ui()
        
        # Configurar eventos
        self._setup_events()
    
    def _setup_ui(self):
        """Configura los elementos de la interfaz de usuario"""
        # Canvas principal para mostrar el PDF
        self.canvas = tk.Canvas(self.root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Botones (simplificados)
        self.btn_frame = tk.Frame(self.root)
        self.btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_open = tk.Button(self.btn_frame, text="Abrir PDF", command=self.open_pdf)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(self.btn_frame, text="Detener", command=self.stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Control de zoom
        self.zoom_frame = tk.Frame(self.btn_frame)
        self.zoom_frame.pack(side=tk.LEFT, padx=10)
        
        self.btn_zoom_out = tk.Button(self.zoom_frame, text="-", command=self.zoom_out, width=2)
        self.btn_zoom_out.pack(side=tk.LEFT)
        
        self.zoom_label = tk.Label(self.zoom_frame, text="100%", width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        
        self.btn_zoom_in = tk.Button(self.zoom_frame, text="+", command=self.zoom_in, width=2)
        self.btn_zoom_in.pack(side=tk.LEFT)
        
        # Etiqueta de estado
        self.status = tk.Label(self.btn_frame, text="No hay documento cargado")
        self.status.pack(side=tk.RIGHT, padx=10)
    
    def _setup_events(self):
        """Configura los eventos del teclado y de la ventana"""
        # Eventos de teclado
        self.root.bind("<Left>", lambda e: self.prev())
        self.root.bind("<Right>", lambda e: self.next())
        self.root.bind("<space>", lambda e: self.toggle_running())
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("<plus>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())
        
        # Evento de redimensionar
        self.root.bind("<Configure>", self._on_resize)
    
    def _on_resize(self, event):
        """Maneja el evento de redimensionado de la ventana"""
        if self.pdf_document:
            # Esperar un momento para que la ventana se estabilice
            self.root.after(100, self.show_current_page)
    
    def open_pdf(self):
        """Abre un archivo PDF a través del diálogo de archivos"""
        self.stop()
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """Carga un documento PDF desde la ruta especificada"""
        try:
            # Cerrar documento anterior si existe
            if self.pdf_document:
                self.pdf_document.close()
            
            # Abrir nuevo documento
            self.pdf_document = fitz.open(file_path)
            num_pages = len(self.pdf_document)
            
            if num_pages == 0:
                messagebox.showinfo("Información", "El PDF no contiene páginas.")
                self.status.config(text="PDF sin páginas")
                return
                
            # Precargar todas las páginas como imágenes
            self.pages = []
            for i in range(num_pages):
                # Inicialmente solo cargar las referencias, no las imágenes completas
                self.pages.append(i)
            
            # Configurar interfaz
            self.current_page = 0
            self.zoom_factor = 1.0
            self.zoom_label.config(text="100%")
            
            # Actualizar título de la ventana
            filename = os.path.basename(file_path)
            self.root.title(f"Visor de PDF - {filename}")
            
            # Mostrar primera página
            self.show_current_page()
            
            # Inicialmente no está en modo automático
            self.running = False
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el PDF: {str(e)}")
            self.status.config(text="Error al cargar el PDF")
    
    def render_page(self, page_index, zoom_factor=1.0):
        """Renderiza una página del PDF como imagen"""
        if not self.pdf_document or page_index >= len(self.pdf_document):
            return None
            
        try:
            # Obtener la página
            page = self.pdf_document[page_index]
            
            # Configurar factor de zoom
            zoom_matrix = fitz.Matrix(zoom_factor, zoom_factor)
            
            # Renderizar página como una imagen pixmap
            pixmap = page.get_pixmap(matrix=zoom_matrix, alpha=False)
            
            # Convertir pixmap a imagen PIL
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            
            return img
            
        except Exception as e:
            print(f"Error al renderizar página {page_index}: {str(e)}")
            return None
    
    def show_current_page(self):
        """Muestra la página actual en el canvas"""
        if not self.pdf_document:
            return
            
        # Renderizar la página actual
        img = self.render_page(self.current_page, self.zoom_factor)
        if img is None:
            return
            
        # Obtener dimensiones del canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width < 50:  # Si el canvas aún no tiene un tamaño definido
            canvas_width = self.root.winfo_width() - 20
            canvas_height = self.root.winfo_height() - 80
        
        # Ajustar imagen al tamaño del canvas si es necesario
        img_width, img_height = img.size
        if img_width > canvas_width or img_height > canvas_height:
            ratio = min(canvas_width/img_width, canvas_height/img_height)
            new_size = (int(img_width * ratio), int(img_height * ratio))
            img = img.resize(new_size, Image.LANCZOS)
        
        # Convertir a formato Tkinter
        self.photo = ImageTk.PhotoImage(img)
        
        # Mostrar en el canvas
        self.canvas.delete("all")
        self.canvas.create_image(
            canvas_width//2, 
            canvas_height//2, 
            image=self.photo
        )
        
        # Dibujar el puntero láser si hay puntos
        self.draw_laser_pointer()
        
        # Actualizar estado
        total_pages = len(self.pdf_document)
        self.status.config(text=f"Página {self.current_page + 1} de {total_pages}")
        
        # Actualizar la ventana
        self.root.update_idletasks()
    
    def update_laser_pointer(self, x, y):
        """Actualiza la posición del puntero láser"""
        if x is None or y is None:
            # Si no hay posición del dedo índice, limpiar los puntos del láser
            self.laser_points = []
            return
            
        # Mantener solo el último punto
        self.laser_points = [(x, y)]
        
        # Redibujar la página con el puntero
        self.show_current_page()
    
    def draw_laser_pointer(self):
        """Dibuja el puntero láser en el canvas"""
        if not self.laser_points:
            return
            
        # Solo dibujar el punto principal del láser
        x, y = self.laser_points[-1]
        self.canvas.create_oval(
            x-5, y-5, x+5, y+5,
            fill='red',
            outline='red'
        )
    
    def next(self):
        """Avanza a la siguiente página"""
        if not self.pdf_document:
            return
            
        if self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
        else:
            # Volver al principio cuando se llega al final
            self.current_page = 0
            
        self.show_current_page()
    
    def prev(self):
        """Retrocede a la página anterior"""
        if not self.pdf_document:
            return
            
        if self.current_page > 0:
            self.current_page -= 1
        else:
            # Ir a la última página cuando se está en la primera
            self.current_page = len(self.pdf_document) - 1
            
        self.show_current_page()
    
    def toggle_running(self):
        """Alterna entre iniciar y detener la presentación"""
        if self.running:
            self.stop()
        else:
            self.running = True
            self.btn_stop.config(state=tk.NORMAL)
    
    def stop(self):
        """Detiene la presentación automática"""
        self.running = False
        if hasattr(self, 'btn_stop') and self.btn_stop:
            self.btn_stop.config(state=tk.DISABLED)
    
    def is_running(self):
        """Devuelve True si la presentación está en marcha"""
        return self.running
    
    def update(self):
        """Actualiza la interfaz gráfica"""
        try:
            self.root.update_idletasks()
            self.root.update()
            return True
        except tk.TclError:
            # Ventana cerrada
            return False
    
    def zoom_in(self):
        """Aumenta el nivel de zoom"""
        if not self.pdf_document:
            return
            
        self.zoom_factor *= 1.2
        self.update_zoom_label()
        self.show_current_page()
    
    def zoom_out(self):
        """Reduce el nivel de zoom"""
        if not self.pdf_document:
            return
            
        self.zoom_factor /= 1.2
        # Limitar zoom mínimo
        if self.zoom_factor < 0.1:
            self.zoom_factor = 0.1
        self.update_zoom_label()
        self.show_current_page()
    
    def update_zoom_label(self):
        """Actualiza la etiqueta con el porcentaje de zoom"""
        zoom_percent = int(self.zoom_factor * 100)
        self.zoom_label.config(text=f"{zoom_percent}%")
    
    def run_from_path(self, pdf_path=None):
        """Inicia la aplicación con un PDF opcional"""
        # Si se proporciona un path, cargar el PDF
        if pdf_path and os.path.exists(pdf_path):
            self.load_pdf(pdf_path)
        
        # Iniciar el bucle principal de Tkinter
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            # Manejar cierre por interrupción
            self.stop()
    
    def __del__(self):
        """Destructor para cerrar el documento PDF"""
        if hasattr(self, 'pdf_document') and self.pdf_document:
            self.pdf_document.close()