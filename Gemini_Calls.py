from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig
import os

if 'GEMINI_API_KEY' in os.environ:
    print("Gemini API Key found!")
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
else:
    print("Unable to find Gemini API key, please add it to your environment variables!")
    GEMINI_API_KEY = None
safety = GenerateContentConfig(response_modalities=['Text', 'Image'],
                               safety_settings=[types.SafetySetting(category="HARM_CATEGORY_CIVIC_INTEGRITY",threshold="OFF")])
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
model_name = "gemini-2.0-flash-exp"

def create_chat_session(use_kb_context):
    print("Creating new chat session")
    try:
        if use_kb_context == True:
            chat_session = client.chats.create(model="gemini-2.0-pro-exp-02-05", config=GenerateContentConfig(
                safety_settings=[types.SafetySetting(category="HARM_CATEGORY_CIVIC_INTEGRITY",threshold="OFF")]))
            return chat_session
        else:
            chat_session = client.chats.create(model=model_name, config=safety)
        return chat_session
    except Exception as e:
        print(f"Error creating chat session: {e}")
        return None, None

def kb(prompt, chat_session):
    try:
        print('kb func used')
        with open("knowledgebase_report.md", "rb") as f:
            md_bytes = f.read()
        md_part = types.Part.from_bytes(data=md_bytes, mime_type='text/markdown')
        print('md_part read')
        response = chat_session.send_message([f"Using only the knowledge base: {prompt}", md_part])
        print('response generated')
        return response.candidates[0].content.parts, chat_session
    except FileNotFoundError:
        print("Error: knowledgebase_report.md not found.")
        return None
    except Exception as e:
        print(f"Error using knowledge base: {e}")
        return None

def messagefunc(prompt, chat_session):
    try:
        response = chat_session.send_message(prompt)
        return response.candidates[0].content.parts, chat_session
    except Exception as e:
        print(f"Error sending message to chat session: {e}")
        return None

def imagefunc(prompt, chat_session, image_bytes):
    response = chat_session.send_message([prompt, image_bytes])
    return response.candidates[0].content.parts, chat_session

def interact_with_gemini(prompt, chat_session=None, use_kb_context=False, image_bytes=None):
    if not client:
        print("Gemini client not initialized (API key missing).")
        return None
    prompt = f"{prompt}"
    if chat_session is None:

        chat_session = create_chat_session(use_kb_context)
        if use_kb_context:
            print('using kb context')
            return kb(prompt, chat_session)
        if image_bytes is not None:
            return imagefunc(prompt, chat_session, image_bytes)
        return messagefunc(prompt, chat_session)

    elif chat_session is not None:
        print("Using existing chat session")
        if use_kb_context:
            return kb(prompt, chat_session)
        if image_bytes is not None:
            return imagefunc(prompt, chat_session, image_bytes)
        return messagefunc(prompt, chat_session)
