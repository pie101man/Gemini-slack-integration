from google import genai
from google.genai import types
import os
import requests
from PIL import Image
from io import BytesIO
import tempfile # Import tempfile

Stylization = "Your response should be stylized as if it were being viewed in a slack channel"
AI_Model = "gemini-2.0-flash-exp"
Image_model = "imagen-3.0-generate-002"
#Making sure the API key exists in the environment variables
if 'GEMINI_API_KEY' in os.environ:
    print("Gemini API Key found!")
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
else:
    print("Unable to find Gemini API key, please add it to your environment variables!")

def only_image(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        client = genai.Client(api_key=GEMINI_API_KEY)
        api_response = client.models.generate_content(
            model=AI_Model,
            contents=["What are your thoughts?", types.Part.from_bytes(data=response.content, mime_type=response.headers['Content-Type'])]) # Dynamically get mime type
        return api_response.text
    except requests.exceptions.RequestException as req_err:
        print(f"Error fetching image: {req_err}")
        return None
    except Exception as e:
        print(f"Error in only_image: {e}")
        return None

def only_text(text):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=AI_Model,
            contents=[text])
        return response.text
    except Exception as e:
        print(f"Error in only_text: {e}")
        return None

def text_and_image(text, image_bytes, mime_type): # Added mime_type argument
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
    model=AI_Model,
    contents=[text, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)]) # Use the passed mime_type
    return response.text

def generate_image(text):
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_images(
            model=Image_model,
            prompt=text,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                safety_filter_level="BLOCK_ONLY_HIGH",
                person_generation="ALLOW_ADULT"))

        if response.generated_images:
            generated_image = response.generated_images[0]
            image_bytes = generated_image.image.image_bytes

            # Save image to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file: # Save as png for broad compatibility
                tmp_file.write(image_bytes)
                tmp_file_path = tmp_file.name # Get the path to the temporary file

            return tmp_file_path # Return the path to the temporary file
        else:
            print("No images generated.")
            return None
    except Exception as e:
        print(f"Error in generate_image: {e}")
        return None
