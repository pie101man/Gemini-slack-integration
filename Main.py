from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse
from Slack_calls import load_slack_tokens, process_slack_message
import time


# Initialize Slack clients and tokens
web_client, socket_mode_client, slack_token = load_slack_tokens()
bot_user_id = web_client.auth_test()["user_id"]  # Get the bot's user ID *once*

tracked_chats = {}

# --- Main Process Function ---
def process(client: SocketModeClient, req: SocketModeRequest):
    client.send_socket_mode_response(SocketModeResponse(envelope_id=req.envelope_id))
    if req.type == "events_api":
        event = req.payload["event"]
        channel_id, session_key, updated_chat_session, event_type = process_slack_message(web_client, event, tracked_chats, bot_user_id)
        if updated_chat_session:
            tracked_chats[channel_id][session_key] = updated_chat_session
            print(f"Stored/updated chat session for thread ts: {session_key}")
        else:
            print(f"Event type '{event_type}' not being processed by current logic.")

    else: print(f"Received and acknowledged a non-events_api request of type: {req.type}")

socket_mode_client.socket_mode_request_listeners.append(process)

if __name__ == "__main__":
    socket_mode_client.connect()
    print("Socket Mode client connected and listening...")
    while True:
        time.sleep(1)
