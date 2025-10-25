from fish_audio_sdk import WebSocketSession, TTSRequest

# Create WebSocket session
ws_session = WebSocketSession("your_api_key")

# Define text generator
def text_stream():
    yield "Hello, "
    yield "this is "
    yield "streaming text!"

# Stream and save audio
with ws_session:
    with open("output.mp3", "wb") as f:
        for audio_chunk in ws_session.tts(
            TTSRequest(text=""),  # Empty text for streaming
            text_stream()
        ):
            f.write(audio_chunk)