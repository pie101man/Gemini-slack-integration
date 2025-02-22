from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
import re
from Slack_calls import load_slack_tokens, process_slack_image_message, process_slack_text_message


# Initialize Slack clients and tokens
web_client, socket_mode_client, slack_token = load_slack_tokens()

# --- Main Process Function ---
def process(client: SocketModeClient, req: SocketModeRequest):
    if req.type == "events_api" and "event" in req.payload and req.payload["event"].get("type") == "app_mention":
        # Acknowledge the event immediately
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        event = req.payload["event"]
        event_type = event.get("type")
        text = event.get("text", "")
        channel_id = event.get("channel")
        ts = event.get("ts")
        user_id = event.get("user")
        cleaned_text = re.sub(r"<@[\w]+>\s*", "", text).strip()  # Removes the mention and strips whitespaces

        if "files" in event:
            process_slack_image_message(web_client, event, cleaned_text, user_id, channel_id, ts,slack_token)
        else:
            process_slack_text_message(web_client, event, cleaned_text, user_id, channel_id,ts)

    else:
        client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
        print(f"Received and acknowledged a non-events_api request of type: {req.type}")


# Add a request handler to the SocketModeClient
socket_mode_client.socket_mode_request_listeners.append(process)

if __name__ == "__main__":
    socket_mode_client.connect()
    print("Socket Mode client connected and listening for image uploads...")
    import time
    while True:
        time.sleep(1)
