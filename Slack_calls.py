from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
import requests
from Gemini_Calls import only_image, only_text, text_and_image, generate_image # Import generate_image
import os
import tempfile # Import tempfile for cleanup

# --- Setup and Initialization ---
def load_slack_tokens():
    """Loads Slack tokens from environment variables and initializes Slack clients."""
    slack_token = os.environ.get('SLACK_TOKEN')
    app_token = os.environ.get('SLACK_APP_TOKEN')

    if not slack_token:
        print("Unable to find Slack Auth Bearer Token. Please set SLACK_TOKEN environment variable.")
        exit(1)
    else:
        print("Slack Auth Bearer Token found!")

    if not app_token:
        print("Unable to find Slack App Token. Please set SLACK_APP_TOKEN environment variable.")
        exit(1)
    else:
        print("Slack App Token found!")

    web_client = WebClient(token=slack_token)
    socket_mode_client = SocketModeClient(app_token=app_token, web_client=web_client)
    return web_client, socket_mode_client, slack_token # Return slack_token as well for later use


# --- Helper Functions for Slack Interaction ---
def send_slack_message(client: WebClient, channel_id: str, text: str, thread_ts: str=None):
    """Sends a message to a Slack channel."""
    try:
        client.chat_postMessage(channel=channel_id, text=text, thread_ts=thread_ts)
    except Exception as e:
        print(f"Error sending Slack message: {e}")

def upload_slack_image(client: WebClient, channel_id: str, image_path: str, message: str=None, thread_ts: str=None):
    """Uploads an image file to a Slack channel."""
    try:
        with open(image_path, 'rb') as image_file:
            client.files_upload_v2(
                channel=channel_id,
                content=image_file.read(),
                filename="generated_image.png", # You can customize the filename
                initial_comment=message,
                thread_ts=thread_ts
            )
        print(f"Image uploaded successfully to channel {channel_id}")
    except Exception as e:
        print(f"Error uploading image to Slack: {e}")
        send_slack_message(client, channel_id, f"Sorry, I ran into an issue uploading the generated image. Error details in logs.", thread_ts=thread_ts)


def download_slack_image(web_client: WebClient, file_id: str, slack_token: str):
    """Downloads an image file from Slack given its file ID and returns image data and mimetype."""
    try:
        file_info_response = web_client.files_info(file=file_id)
        if file_info_response["ok"]:
            download_url = file_info_response["file"]["url_private_download"]
            headers = {"Authorization": f"Bearer {slack_token}"}
            image_response = requests.get(download_url, headers=headers)
            if image_response.status_code == 200:
                mimetype = file_info_response["file"]["mimetype"] # Get mimetype
                return image_response.content, mimetype # Return both content and mimetype
            else:
                print(f"Error downloading image: HTTP status {image_response.status_code}")
                return None, None # Return None for both if error
        else:
            print(f"Error getting file info from Slack: {file_info_response['error']}")
            return None, None # Return None for both if error
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None, None # Return None for both if error


def process_slack_image_message(web_client: WebClient, event: dict, cleaned_text: str, user_id: str, channel_id: str, ts: str, slack_token: str):
    """Processes a Slack message that includes an image."""
    for file_info in event.get("files", []):
        if file_info["mimetype"].startswith("image/"):
            image_data, mimetype = download_slack_image(web_client, file_info["id"], slack_token)
            if image_data:
                try:
                    if cleaned_text:
                        ai_response = text_and_image(cleaned_text, image_data, mimetype)
                        response_text = f"Hey <@{user_id}>! I received your image and text, here's what the AI thinks:\n\n{ai_response}"
                    else:
                        ai_response = only_image(image_data)
                        response_text = f"Hey <@{user_id}>! I received your image and here's what the AI thinks:\n\n{ai_response}"
                    send_slack_message(web_client, channel_id, response_text, ts)
                except Exception as ai_error:
                    print(f"Error processing image with AI: {ai_error}")
                    send_slack_message(web_client, channel_id, f"Sorry, I ran into an issue processing the image with AI. Please try again later, <@{user_id}>. Error details in logs.", ts)

            else:
                send_slack_message(web_client, channel_id, f"Oops! There was an error downloading the image from Slack. Please try again, <@{user_id}>.", thread_ts=ts)
            return # Exit after processing the first image


def process_slack_text_message(web_client: WebClient, event: dict, cleaned_text: str, user_id: str, channel_id: str, ts: str):
    """Processes a Slack message that is text-only."""
    if cleaned_text.lower().startswith("generate image of"): # Check for image generation command
        prompt = cleaned_text[len("generate image of"):].strip() # Extract prompt
        try:
            image_path = generate_image(prompt) # Generate the image and get the file path
            if image_path:
                upload_slack_image(web_client, channel_id, image_path, message=f"Generated image for: '{prompt}'", thread_ts=ts) # Upload image to Slack
                os.remove(image_path) # Clean up temporary image file
            else:
                send_slack_message(web_client, channel_id, f"Sorry <@{user_id}>, I couldn't generate an image for that prompt.", thread_ts=ts)
        except Exception as generate_error:
            print(f"Error during image generation and upload: {generate_error}")
            send_slack_message(web_client, channel_id, f"Sorry <@{user_id}>, there was an error generating or sending the image. Please check the logs.", thread_ts=ts)
    else: # Original text processing logic
        try:
            ai_response = only_text(cleaned_text)
            response_text = f"Hey <@{user_id}>! Here is what Gemini says: {ai_response}"
            send_slack_message(web_client, channel_id, response_text, ts)
        except Exception as ai_error:
            print(f"Error processing text with AI: {ai_error}")
            send_slack_message(web_client, channel_id, f"Sorry, I ran into an issue processing your text with AI. Please try again later, <@{user_id}>. Error details in logs.", ts)
