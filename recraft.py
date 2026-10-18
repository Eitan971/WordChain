import base64
import os
import re
import httpx
from dotenv import load_dotenv

import game_state as gs

load_dotenv()

RECRAFT_URL = "https://external.api.recraft.ai/v1/images/generations"
RECRAFT_MODEL = "recraftv4_1_flash"
RECRAFT_SIZE = "1:1"
IMAGES_FOLDER = "recraftimages"

def getImage(word, style=None, fileName=None):
    
    prompt = word
    if style:
        prompt += f" ({style}) style"
    gs.log(f"Generating image for word: {prompt}")

    try:
        response = httpx.post(
            RECRAFT_URL,
            headers={"Authorization": f"Bearer {os.environ['RECRAFT_API']}"},
            json={
                "prompt": prompt,
                "model": RECRAFT_MODEL,
                "size": RECRAFT_SIZE,
                "n": 1,
                "response_format": "b64_json",
                "image_format": "png",
            },
            timeout=60,
        )
        response.raise_for_status()
        image = base64.b64decode(response.json()["data"][0]["b64_json"])

        fileName = fileName or word.strip().lower() +".png"
        path = os.path.join(IMAGES_FOLDER, fileName)
        f = open(path, "wb")
        f.write(image)
        f.close()
        gs.log(f"->Image saved.")
        return True
    except Exception as e:
        gs.log(f"    Error generating image for '{word}': {e}")
        return False
