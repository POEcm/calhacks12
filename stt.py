from fish_audio_sdk import Session, ASRRequest
import os
from dotenv import load_dotenv

load_dotenv()

FISH_API = os.getenv("FISH_API")

session = Session(FISH_API)

# Read audio file
with open("audio.m4a", "rb") as f:
    audio_data = f.read()

# Transcribe
response = session.asr(ASRRequest(
    audio=audio_data,
    language="en"
))

print(response.text)
print(f"Duration: {response.duration}ms")