# Vision Artificial - Trabajo Práctico 2

Este proyecto implementa técnicas de visión artificial utilizando Python y bibliotecas como OpenCV y MediaPipe.

---

## Configuración del Entorno Virtual

Este proyecto utiliza un entorno virtual para gestionar las dependencias. Sigue los pasos a continuación para configurarlo correctamente.

---

### Requisitos Previos

- **Python 3.10** instalado en tu sistema.
- **`pip` actualizado**. Puedes actualizarlo con:
  ```bash
  python -m pip install --upgrade pip
  ```

---

### Pasos para Configurar el Entorno Virtual

1. **Crear el Entorno Virtual**  
   En la raíz del proyecto, ejecuta:
   ```bash
   python -m venv venv
   ```

2. **Activar el Entorno Virtual**  
   - En **Windows** (Command Prompt o PowerShell):
     ```bash
     .\venv\Scripts\activate
     ```
   - En **bash** (Git Bash o WSL):
     ```bash
     source ./venv/Scripts/activate
     ```

3. **Instalar las Dependencias**  
   Una vez activado el entorno virtual, instala las dependencias necesarias:
   ```bash
   pip install -r requirements.txt
   ```

---

## Uso del Entorno Virtual

- **Activar el Entorno**:  
  Antes de ejecutar cualquier script, asegúrate de activar el entorno virtual como se indica en el paso 2.

- **Desactivar el Entorno**:  
  Cuando termines de trabajar, desactiva el entorno virtual con:
  ```bash
  deactivate
  ```

---

## Generar o Actualizar `requirements.txt`

Si instalas nuevas dependencias, actualiza el archivo `requirements.txt` con:
```bash
pip freeze > requirements.txt
```

---

## Notas

- La carpeta `venv/` está excluida del repositorio mediante el archivo `.gitignore`.
- Asegúrate de que todos los colaboradores sigan estos pasos para configurar su entorno local.

---

## Ejecución del Proyecto

1. Activa el entorno virtual.
2. Ejecuta los scripts necesarios, como `hand_detector.py` o `finger_counting.py`:
   ```bash
   python hand_detector.py
   ```

---

## Dependencias

Este proyecto utiliza las siguientes bibliotecas principales:
- `opencv-python`
- `mediapipe`
- `time` y `os` (incluidas en la biblioteca estándar de Python)

Para más detalles, consulta el archivo `requirements.txt`.