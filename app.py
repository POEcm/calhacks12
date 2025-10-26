import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from fish_audio_sdk import Session, ASRRequest
import os
from dotenv import load_dotenv

load_dotenv()

FISH_API = os.getenv("FISH_API")

session = Session(FISH_API)

app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde tu frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Definir la carpeta donde se guardarán los audios
UPLOAD_FOLDER = 'python_uploads'
# Asegurarse de que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/api/upload-audio', methods=['POST'])
def upload_audio():
    try:
        # 1. Verificar que el archivo 'audio' venga en la petición
        if 'audio' not in request.files:
            return jsonify({"success": False, "message": "No se encontró el archivo de audio"}), 400

        file = request.files['audio']

        if file.filename == '':
            return jsonify({"success": False, "message": "Nombre de archivo vacío"}), 400

        if file:
            # 2. Definir la ruta completa para guardar el archivo
            # Usamos el nombre original, pero podrías generar uno único
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 3. Guardar el archivo en el servidor
            file.save(filepath)

            print(f"Archivo guardado en: {filepath}")

            # Read audio file
            with open(filepath, "rb") as f:
                audio_data = f.read()

            # Transcribe
            response = session.asr(ASRRequest(
                audio=audio_data,
                language="en"
            ))

            print(response.text)
            print(f"Duration: {response.duration}ms")

            # 4. Responder al frontend
            return jsonify({"success": True, "message": "Audio guardado en Python."})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error al guardar el audio."}), 500

if __name__ == '__main__':
    # Correr el servidor en el puerto 5000 (o el que prefieras)
    app.run(debug=True, port=5000)