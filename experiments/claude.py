from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()
CLAUDE_API = os.getenv("CLAUDE_API")

client = Anthropic(api_key=CLAUDE_API)

stream = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Tell me a short story"}],
    stream=True  # <-- STREAMING MODE
)

for chunk in stream:
    if chunk.type == "content_block_delta":
        print(chunk.delta.text, end="", flush=True)