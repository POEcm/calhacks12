from fish_audio_sdk import Session, TTSRequest
import os
from dotenv import load_dotenv

load_dotenv()

FISH_API = os.getenv("FISH_API")

session = Session(FISH_API)

# Generate speech
with open("welcome.mp3", "wb") as f:
    for chunk in session.tts(
      TTSRequest(text="Hello! Welcome to Fish Audio."),
      backend='s1'
    ):
        f.write(chunk)

print("✓ Audio saved to welcome.mp3")