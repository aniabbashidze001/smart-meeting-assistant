# backend/visuals/generate_visual.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_visual_image(prompt_text: str):
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"❌ Failed to generate visual summary: {e}")
        return None
