import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import fitz  # PyMuPDF

class PDFViewer:
    def __init__(self, root, pdf_path=None):
        self.root = root
        self.root.title("Visor de PDF")
        self.root.geometry("800x600")
        
        # Variables
        self.pdf_document = None
        self.pages = []
        self.current_page = 0
        self.running = False
        self.zoom_factor = 1.0
        
        # Interfaz
        self.canvas = tk.Canvas(root, bg="gray")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Botones (simplificados)
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(fill=tk.X, pady=5)
        
        self.btn_open = tk.Button(self.btn_frame, text="Abrir PDF", command=self.open_pdf)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = tk.Button(self.btn_frame, text="Detener", command=self.stop_slideshow, state=tk.DISABLED)
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
        
        # Cargar PDF si se proporciona una ruta
        if pdf_path and os.path.exists(pdf_path):
            self.load_pdf(pdf_path)
            
        # Configurar teclas de navegación
        self.root.bind("<Left>", lambda e: self.prev_page())
        self.root.bind("<Right>", lambda e: self.next_page())
        self.root.bind("<space>", lambda e: self.toggle_slideshow())
        self.root.bind("<Escape>", lambda e: self.stop_slideshow())
        self.root.bind("<plus>", lambda e: self.zoom_in())
        self.root.bind("<minus>", lambda e: self.zoom_out())
    
    def open_pdf(self):
        """Abre un archivo PDF a través del diálogo de selección de archivos"""
        self.stop_slideshow()
        
        file_path = filedialog.askopenfilename(
            title="Seleccionar PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if file_path:
            self.load_pdf(file_path)
    
    def load_pdf(self, file_path):
        """Carga un documento PDF desde la ruta especificada"""
        try:
            # Detener la presentación actual si existe
            self.stop_slideshow()
            
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
            
            # Habilitar botón de detener
            self.btn_stop.config(state=tk.NORMAL)
            
            # Actualizar título de la ventana
            filename = os.path.basename(file_path)
            self.root.title(f"Visor de PDF - {filename}")
            
            # Mostrar primera página
            self.show_current_page()
            
            # Iniciar la presentación automáticamente
            self.start_slideshow()
            
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
        
        # Actualizar estado
        total_pages = len(self.pdf_document)
        self.status.config(text=f"Página {self.current_page + 1} de {total_pages}")
    
    def next_page(self):
        """Avanza a la siguiente página"""
        if not self.pdf_document:
            return
            
        if self.current_page < len(self.pdf_document) - 1:
            self.current_page += 1
            self.show_current_page()
    
    def prev_page(self):
        """Retrocede a la página anterior"""
        if not self.pdf_document:
            return
            
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()
    
    def toggle_slideshow(self):
        """Alterna entre iniciar y detener la presentación"""
        if self.running:
            self.stop_slideshow()
        else:
            self.start_slideshow()
    
    def start_slideshow(self):
        """Inicia la presentación automática"""
        if not self.pdf_document or self.running:
            return
            
        self.running = True
        self.btn_stop.config(state=tk.NORMAL)
        
        # En esta versión, el bucle principal controla la presentación
        # No necesitamos usar after aquí
    
    def change_page(self):
        """Cambia a la siguiente página en la presentación automática"""
        if not self.running:
            return
            
        self.next_page()
        
        # Si llegamos al final, volver al principio
        if self.current_page >= len(self.pdf_document) - 1:
            self.current_page = -1  # La próxima vez será 0
        
        # Programar la próxima actualización
        self.root.after(1000, self.change_page)
    
    def stop_slideshow(self):
        """Detiene la presentación automática"""
        self.running = False
        
        if hasattr(self, 'btn_stop') and self.btn_stop:
            self.btn_stop.config(state=tk.DISABLED)
    
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
    
    def __del__(self):
        """Destructor para cerrar el documento PDF"""
        if hasattr(self, 'pdf_document') and self.pdf_document:
            self.pdf_document.close()