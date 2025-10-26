import os
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from fish_audio_sdk import Session, ASRRequest
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from fish_audio_sdk import WebSocketSession, TTSRequest

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API")
FISH_API = os.getenv("FISH_API")

claude_client = Anthropic(api_key=CLAUDE_API_KEY)
session = Session(FISH_API)
ws_session = WebSocketSession(FISH_API)

OUTPUT_FILENAME = "claude_historia.wav" # El formato ahora es WAV

app = Flask(__name__)
# Habilitar CORS para permitir peticiones desde tu frontend
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3000"}})

# Definir la carpeta donde se guardarán los audios
UPLOAD_FOLDER = 'python_uploads'
# Asegurarse de que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- 1. Generador de Texto de Claude (Tu código) ---
def claude_text_stream_generator(prompt):
    """
    Llama a Claude y produce (yields) los fragmentos de texto.
    """
    print("-> [GENERADOR]: Solicitando stream a Claude...")
    try:
        stream = claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": prompt
            }],
            stream=True
        )

        for chunk in stream:
            if chunk.type == "content_block_delta":
                text_chunk = chunk.delta.text
                print(f"   [Claude ->] {text_chunk}", end="", flush=True)
                yield text_chunk

        print("\n-> [GENERADOR]: Stream de Claude finalizado.")
    except Exception as e:
        print(f"\nError durante el stream de Claude: {e}")
        yield ""


# --- 2. Generador de Stream de Audio (NUEVO) ---
def audio_stream_generator(prompt):
    """
    Este generador llama a Fish Audio con el generador de Claude
    y produce (yields) los 'chunks' de audio en lugar de guardarlos.
    """
    print("Iniciando stream de audio para el frontend...")
    try:
        # Abre la conexión del WebSocket
        with ws_session:
            print("Llamando a ws_session.tts() con el generador de Claude...")

            audio_stream = ws_session.tts(
                TTSRequest(text="",
                           reference_id="8ab06957eca840ee88b6a5f8b2972c0c", # GRANDMA VOICE
                           format="wav"),
                claude_text_stream_generator(prompt) # ¡El generador conectado!
            )

            # Itera sobre los *fragmentos de audio* que Fish Audio devuelve
            for audio_chunk in audio_stream:
                if audio_chunk:
                    print(f"\n   [-> FE] Enviando chunk de {len(audio_chunk)} bytes.")
                    # En lugar de escribir a un archivo, envía el chunk al frontend
                    yield audio_chunk

            print("\n¡Éxito! Stream de audio al frontend finalizado.")

    except Exception as e:
        print(f"\nOcurrió un error con la sesión de Fish Audio: {e}")


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


            return Response(audio_stream_generator(response.text), mimetype="audio/wav")

            ## 4. Responder al frontend
            #return jsonify({"success": True, "message": "Audio guardado en Python."})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error al guardar el audio."}), 500

######## IMAGE

@app.route('/api/upload-image', methods=['POST'])
def upload_image():
    try:
        # 1. Verificar que el archivo 'image' venga en la petición
        if 'image' not in request.files:
            return jsonify({"success": False, "message": "No 'image' file part found"}), 400

        file = request.files['image']

        # 2. Si el usuario no selecciona archivo, el navegador envía
        #    un archivo vacío sin nombre.
        if file.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        # 3. Verificar si el archivo es válido y tiene una extensión permitida

        # 5. Guardar el archivo en la carpeta de imágenes
        filepath = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        print(f"Imagen guardada en: {filepath}")

        # 6. Responder al frontend con éxito
        return jsonify({
            "success": True,
            "message": f"Imagen '{file.filename}' guardada exitosamente.",
            "filepath": filepath
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "message": "Error al guardar la imagen."}), 500



##### APP

if __name__ == '__main__':
    # Correr el servidor en el puerto 5000 (o el que prefieras)
    app.run(debug=True, port=5000)