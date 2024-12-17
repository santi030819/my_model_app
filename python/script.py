import time
import os
from PIL import Image
import win32print
import win32api
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

class ImageHandler(FileSystemEventHandler):
    def __init__(self, output_folder, new_width, new_height, position_x, position_y):
        self.output_folder = output_folder
        self.new_width = new_width
        self.new_height = new_height
        self.position_x = position_x
        self.position_y = position_y

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith(('.jpg', '.jpeg', '.png', '.tmp')):
            self.handle_temp_file(event.src_path)

    def handle_temp_file(self, file_path):
        # Si es un archivo .tmp, esperar a que termine de transferirse
        if file_path.endswith('.tmp'):
            print(f"Detectado archivo temporal: {file_path}")
            while file_path.endswith('.tmp'):
                time.sleep(0.1)  # Esperar un momento y luego verificar si sigue siendo un archivo temporal
                new_file_path = file_path.replace('.tmp', '')
                if os.path.exists(new_file_path):
                    print(f"Archivo completado: {new_file_path}")
                    file_path = new_file_path  # Cambiar a la versión completa del archivo
                    break
            else:
                return  # Si no se encuentra el archivo final, no hacer nada

        self.process_image(file_path)

    def process_image(self, image_path):
        time.sleep(0.3)# Esperar un poco para asegurarse de que el archivo esté completamente escrito
        try:
            # Redimensionar la imagen y crear el PDF
            image = Image.open(image_path)
            image = image.resize((self.new_width, self.new_height), Image.LANCZOS)
            page_width, page_height = letter

            pdf_path = os.path.join(self.output_folder, os.path.splitext(os.path.basename(image_path))[0] + '.pdf')

            c = canvas.Canvas(pdf_path, pagesize=letter)
            x = self.position_x
            y = page_height - self.new_height - self.position_y

            c.drawImage(image_path, x, y, width=self.new_width, height=self.new_height)
            c.showPage()
            c.save()

            print(f"Imagen convertida a PDF: {pdf_path}")
            self.print_pdf(pdf_path)

        except Exception as e:
            print(f"Error al procesar la imagen {image_path}: {e}")

    def print_pdf(self, pdf_path):
        try:
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(0, "print", pdf_path, None, ".", 0)
            print(f"Archivo enviado a la impresora: {printer_name}")
        except Exception as e:
            print(f"Error al imprimir el archivo {pdf_path}: {e}")

if __name__ == "__main__":
    folder_to_watch = r"C:/Users/es-irium.socampo/Desktop/inbox"  # Carpeta a monitorear
    output_folder = r"C:/Users/es-irium.socampo/Desktop/impresion"  # Carpeta donde se guardarán los PDFs
    new_width = 370
    new_height = 250
    position_x = 31
    position_y = 90

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    event_handler = ImageHandler(output_folder, new_width, new_height, position_x, position_y)
    observer = Observer()
    observer.schedule(event_handler, path=folder_to_watch, recursive=False)
    observer.start()

    print(f"Monitoreando la carpeta: {folder_to_watch}")

    try:
        while True:
            time.sleep(0.3)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
