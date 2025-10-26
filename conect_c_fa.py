import os
from dotenv import load_dotenv
from anthropic import Anthropic
from fish_audio_sdk import WebSocketSession, TTSRequest
import pyaudio

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API")
FISH_AUDIO_API_KEY = os.getenv("FISH_API")

claude_client = Anthropic(api_key=CLAUDE_API_KEY)
ws_session = WebSocketSession(FISH_AUDIO_API_KEY)


AUDIO_FORMAT = pyaudio.paInt16  # 16-bit PCM
CHANNELS = 1
RATE = 44100
REQUEST_FORMAT = "pcm_s16le_24000"
OUTPUT_FILENAME = "claude_historia.wav" # El formato ahora es WAV

print("Inicializando reproductor de audio (Pyaudio)...")
p = pyaudio.PyAudio()
try:
    audio_play_stream = p.open(format=AUDIO_FORMAT,
                               channels=CHANNELS,
                               rate=RATE,
                               output=True) # ¡Stream de salida!
except Exception as e:
    print(f"Error al abrir Pyaudio stream: {e}")
    p.terminate()
    exit()


def claude_text_stream_generator():
    """
    Este generador llama a la API de Claude y produce (yields)
    los fragmentos de texto a medida que llegan.
    Fish Audio consumirá este generador.
    """
    print("-> [GENERADOR]: Solicitando stream a Claude...")
    try:
        # Llama a la API de Claude para obtener el stream
        stream = claude_client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": "Very easy steps on how to do a cooking recipe."
            }],
            stream=True  # ¡Modo streaming!
        )

        # Itera sobre los fragmentos de Claude
        for chunk in stream:
            if chunk.type == "content_block_delta":
                text_chunk = chunk.delta.text
                print(f"   [Claude ->] {text_chunk}", end="", flush=True)

                # En lugar de imprimir, produce el fragmento
                # para que Fish Audio lo consuma.
                yield text_chunk

        print("\n-> [GENERADOR]: Stream de Claude finalizado.")

    except Exception as e:
        print(f"\nError durante el stream de Claude: {e}")
        yield "" # Produce un string vacío para terminar limpiamente


# --- 3. Proceso Principal: Fish Audio ---

print("\nIniciando sesión de Fish Audio TTS...")
try:
    # Abre la conexión del WebSocket
    with ws_session:
        print(f"Abriendo archivo de salida: {OUTPUT_FILENAME}")

        # Abre el archivo donde se guardará el audio
        with open(OUTPUT_FILENAME, "wb") as f:

            print("Llamando a ws_session.tts() con el generador de Claude...")

            # Llama a TTS.
            # 1. Pasa una solicitud vacía (porque usamos streaming)
            # 2. Pasa la *función generadora* que creamos
            audio_stream = ws_session.tts(
                TTSRequest(text="",
                    reference_id="8ab06957eca840ee88b6a5f8b2972c0c", # GRANDMA VOICE
                    format="wav"),  # Texto base vacío
                claude_text_stream_generator()  # ¡El generador conectado!
            )

            # Itera sobre los *fragmentos de audio* que Fish Audio devuelve
            for audio_chunk in audio_stream:
                if audio_chunk:
                    print(f"\n   [<- Audio Fish] Recibido chunk de {len(audio_chunk)} bytes.")
                    f.write(audio_chunk)


                    audio_play_stream.write(audio_chunk)

        print(f"\n¡Éxito! Audio guardado en {OUTPUT_FILENAME}")

except Exception as e:
    print(f"\nOcurrió un error con la sesión de Fish Audio: {e}")
