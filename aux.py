import streamlit as st
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from dotenv import load_dotenv
load_dotenv()


def open_info(filename):
    """Function to open and read saved user info."""
    try:
        with open(filename, "r") as f:
            info = f.read()
        return info
    except FileNotFoundError:
        return "No saved info found."
    except Exception as e:
        st.error(f"An error occurred while reading info: {e}")
        return ""

def save_info(filename, info):
    """Function to save user info."""
    try:
        with open(filename, "w") as f:
            f.write(info + "\n")
        return True
    except Exception as e:
        st.error(f"An error occurred while saving info: {e}")
        return False
    

client = genai.Client()

def ai_text_generate(system="", prompt=""):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system),
    )

    return response.text

def ai_text_stream_generate(system="", prompt=""):
    response = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system),
    )
    for chunk in response:
        if chunk.text:
            yield chunk.text



def image_generate(prompt=""):
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )

        image = None
        description = ""

        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                description += part.text.strip()

            if hasattr(part, "inline_data") and part.inline_data:
                if hasattr(part.inline_data, "data") and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    image = Image.open(BytesIO(image_bytes))

        if image is None:
            st.warning("No image was returned by Gemini.")

        return image, description

    except Exception as e:
        st.error(f"Error generating image: {e}")
        return None, None
