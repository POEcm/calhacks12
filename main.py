from fish_audio_sdk import Session, TTSRequest
import os
from dotenv import load_dotenv

import pyaudio

load_dotenv()

FISH_API = os.getenv("FISH_API")

session = Session(FISH_API)

text = """
(happy) I'm excited to share this!
(sad) Unfortunately, it didn't work out.
(whispering) This is a secret.
"""

# Generate speech
with open("welcome.mp3", "wb") as f:
    for chunk in session.tts(
      TTSRequest(text=text,
      reference_id="54e3a85ac9594ffa83264b8a494b901b"),
      backend='s1'
    ):
        f.write(chunk)

print("✓ Audio saved to welcome.mp3")


### ---- STREAM

p = pyaudio.PyAudio()
stream = p.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=44100,
    output=True
)

# Stream audio
for chunk in session.tts(TTSRequest(
    text="Streaming audio 1 2 3, test streaming",
    format="pcm",
    sample_rate=44100
)):
    stream.write(chunk)

stream.close()
p.terminate()