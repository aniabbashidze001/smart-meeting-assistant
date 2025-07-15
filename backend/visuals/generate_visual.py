import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_visual_image(prompt_text: str):
    """
        Generate a single image using OpenAI's DALL·E 3 API based on provided prompt.

        Args:
            prompt_text (str): Descriptive text prompt to guide image generation.

        Returns:
            str or None: URL of the generated image if successful; None otherwise.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt_text,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        print(f"❌ Failed to generate visual summary: {e}")
        return None
