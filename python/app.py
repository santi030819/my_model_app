from flask import Flask, render_template
import subprocess
import webbrowser
import threading

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
def open_browser():
    """Abre el navegador por defecto con la dirección de la app."""
    webbrowser.open_new("http://127.0.0.1:5000")


@app.route('/comenzar', methods=['POST'])
def comenzar():
    try:
        # Ejecutar el script y capturar la salida
        result = subprocess.run(['python', 'script.py'], capture_output=True, text=True)
        
        # Obtener la salida estándar del script
        output = result.stdout
        
        # Si hay errores en el script, los mostramos también
        if result.stderr:
            output += '\nError:\n' + result.stderr
        
        # Pasar la salida al template
        return render_template('index.html', output=output)
    
    except Exception as e:
        return render_template('index.html', output=f"Hubo un error al ejecutar el script: {str(e)}")

if __name__ == "__main__":
    # Inicia el navegador en un hilo separado
    threading.Timer(1, open_browser).start()
    app.run(debug=False, use_reloader=False)