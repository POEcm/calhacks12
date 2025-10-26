import anthropic
import base64
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

CLAUDE_API_KEY = os.getenv("CLAUDE_API")
# Your API key
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# --- 1. Read and Encode Your Image ---
image_path = "grape.jpeg"
media_type = "image/jpeg"  # Or "image/png", "image/gif", "image/webp"

# Read the image file in binary mode
with open(image_path, "rb") as image_file:
    image_data = image_file.read()

# Encode the binary data to Base64
base64_image = base64.b64encode(image_data).decode("utf-8")
# -------------------------------------

try:
    message = client.messages.create(
        model="claude-sonnet-4-5",  # Or any other vision-capable model
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": base64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": "What is in this image?"
                    }
                ],
            }
        ],
    )

    print(message.content[0].text)

except anthropic.APIError as e:
    print(f"An API error occurred: {e}")
except httpx.ConnectError as e:
    print(f"A connection error occurred: {e}")