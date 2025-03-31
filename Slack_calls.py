from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
import requests
from Gemini_Calls import interact_with_gemini # Updated import
import os
import tempfile
import re
import io
from PIL import Image
slack_token = os.environ.get('SLACK_TOKEN')
def load_slack_tokens():
    slack_token = os.environ.get('SLACK_TOKEN')
    app_token = os.environ.get('SLACK_APP_TOKEN')

    if not slack_token:
        print("Unable to find Slack Auth Bearer Token. Please set SLACK_TOKEN environment variable. Starts with xoxb, this is your Oauth Token")
        exit(1)
    else:
        print("Slack Auth Bearer Token found!")

    if not app_token:
        print("Unable to find Slack App Token. Please set SLACK_APP_TOKEN environment variable. Starts with xapp")
        exit(1)
    else:
        print("Slack App Token found!")

    web_client = WebClient(token=slack_token)
    socket_mode_client = SocketModeClient(app_token=app_token, web_client=web_client)
    return web_client, socket_mode_client, slack_token

def add_reaction(web_client,channel_id, ts, reaction_name="thinking_face"):
    try:
        web_client.reactions_add(channel=channel_id, name=reaction_name, timestamp=ts)
    except Exception as e:
        print(f"Error adding reaction: {e}")

def extract_file(event, slack_token):
    file = event.get("files", "")
    private_download_url = file[0]['url_private_download']
    headers = {'Authorization': f'Bearer {slack_token}'}
    response = requests.get(private_download_url, headers=headers)
    file_bytes = response.content
    image_stream = io.BytesIO(file_bytes)
    image = Image.open(image_stream)
    return image


def get_or_create_chat_session(channel_id, thread_ts, tracked_chats):
    if channel_id not in tracked_chats:
        tracked_chats[channel_id] = {}

    if thread_ts not in tracked_chats[channel_id]:
        tracked_chats[channel_id][thread_ts] = None
    return tracked_chats[channel_id].get(thread_ts)


def send_slack_message(client: WebClient, channel_id: str, text: str, thread_ts: str=None):
    """Sends a message to a Slack channel."""
    try:
        client.chat_postMessage(channel=channel_id, text=text, thread_ts=thread_ts)
    except Exception as e:
        print(f"Error sending Slack message: {e}")

def upload_slack_image(client, channel_id: str, image_path: str, message: str=None, thread_ts: str=None):
    """Uploads an image file to a Slack channel."""
    try:
        print(image_path)
        print(f"message: {message}")
        print(f"thrad_ts: {thread_ts}")
        print(f"client: {client}")
        print(f"channel_id: {channel_id}")
        response = client.files_upload_v2(
            channel=channel_id,
            initial_comment=message,
            file=image_path,
            thread_ts=thread_ts
        )
        print(response)
        if response["ok"]:
            print(f"Image uploaded successfully to channel {channel_id}")
        else:
            print(f"Error uploading image: {response['error']}")
    except Exception as e:
        print(f"Error uploading image to Slack: {e}")

def process_slack_message(web_client: WebClient, event, tracked_chats, bot_user_id):
    event_type = event.get("type")
    channel_id = event.get("channel")
    thread_ts = event.get("thread_ts")
    user_id = event.get("user")
    ts = event.get("ts")
    file = event.get("files", "")
    text = event.get("text", "")
    cleaned_text = re.sub(r"<@[\w]+>\s*", "", text).strip()
    if event_type == "app_mention":
        image = None
        print("Processing app_mention or thread message...")

        if user_id == bot_user_id:
            print("Message sent by bot, ignoring.")
            return

        session_key = thread_ts or ts
        chat_session = get_or_create_chat_session(channel_id, thread_ts, tracked_chats)

        try:
            print("Adding reaction...")
            add_reaction(web_client,channel_id, ts, reaction_name="thinking_face")
            print("Reaction added.")
        except Exception as e:
            print(f"Error adding reaction: {e}")

        gemini_kwargs = {"chat_session": chat_session}
        print("Calling interact_with_gemini...")

        if """!kb""" in cleaned_text: gemini_kwargs["use_kb_context"] = True

        if file != '':
            image = extract_file(event, slack_token)
            gemini_kwargs["image_bytes"] = image

        gemini_response_parts, updated_chat_session = interact_with_gemini (cleaned_text,**gemini_kwargs)

        try:
            print("Calling handle_gemini_response_for_slack...")
            handle_gemini_response_for_slack(web_client, channel_id, ts, gemini_response_parts, user_id)
        except Exception as e:
            print(f"Error in handle_gemini_response_for_slack: {e}")

        return channel_id, session_key, updated_chat_session, event_type

def handle_gemini_response_for_slack(web_client, channel_id, ts, gemini_response, user_id):
    for part in gemini_response:
        text_content = None
        is_image = False

        if isinstance(part, str):
            text_content = part

        elif hasattr(part, 'text') and part.text is not None:
            text_content = part.text

        elif hasattr(part, 'inline_data') and hasattr(part.inline_data, 'data') and part.inline_data.data is not None:
            is_image = True

        if text_content is not None:
            send_slack_message(web_client, channel_id, text_content, ts)

        elif is_image:

            try:
                tmp_file_path = None
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                    tmp_file.write(part.inline_data.data)
                    tmp_file.flush()
                    tmp_file_path = tmp_file.name
                upload_slack_image(web_client, channel_id, tmp_file_path, thread_ts=ts)
            except Exception as e:
                print(f"Error processing and uploading image: {e}")
                send_slack_message(web_client, channel_id, "Error processing image. Sorry!", ts)

        else:
            send_slack_message(web_client, channel_id, f"Sorry, I might be broken, <@{user_id}>.", ts)
