# Slack Gemini AI Bot

This Python bot connects your Slack workspace to Google's Gemini AI models, allowing you to interact with Gemini directly from Slack. You can ask text-based questions, get insights from images, and even generate images, all within your Slack channels.

## Features

*   **Text-Based Queries:**  Mention the bot in Slack and ask any text-based question. The bot will use Gemini AI to generate a response and reply directly in the channel, stylized as a Slack message.
*   **Image Analysis:**  Upload an image to Slack and mention the bot. The bot can analyze the image and provide insights or answer questions related to it. You can also include text with the image for more context.
*   **Image Generation:** Use a specific command (you can define this or just use text prompts) to instruct the bot to generate images using Gemini's image generation capabilities and receive the generated image (implementation for sending image back to Slack would need to be added, currently returns image bytes).
*   **Slack Integration:** Seamlessly integrates with Slack using the Slack Socket Mode, allowing real-time interaction without needing a public web server.
*   **Environment Variable Configuration:** Securely manages API keys using environment variables.
*   **Error Handling and Logging:** Includes basic error handling and logging to help with debugging and monitoring.

## Prerequisites

Before you begin, ensure you have the following:

1.  **Python 3.7+:** Python must be installed on your system.
2.  **Pip:**  Python package installer (usually included with Python installations).
3.  **Google Gemini API Key:** You need a Google Cloud project with access to the Gemini API and an API key. You can obtain one by following the Google AI Studio or Google Cloud documentation for setting up Gemini API access.
4.  **Slack App:** You need to create a Slack App. Follow these steps:
    *   Go to [Slack API: Create an app](https://api.slack.com/apps?new_app=1).
    *   Choose "From scratch".
    *   Give your app a name (e.g., "Gemini Slack Bot") and select your workspace.
    *   **Enable Socket Mode:** In your app settings, navigate to "Socket Mode" and activate it. You'll find your **Slack App Token** (starts with `xapp-`) here. Keep this token safe.
    *   **Bot Token Scopes:** Navigate to "OAuth & Permissions" and then "Bot Token Scopes". Add the following scopes:
        *   `app_mentions:read`
        *   `chat:write`
        *   `files:read`
        *   `files:write`
        *   `im:history`
        *   `im:read`
        *   `im:write`
        *   `users:read`
    *   **Install App to Workspace:**  In "OAuth & Permissions", click "Install to Workspace". Allow the permissions. After installation, you'll get a **Slack Bot Token** (starts with `xoxb-`). Keep this token safe as well.

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/pie101man/Gemini-slack-integration
    cd Gemini-slack-integration
    ```

2.  **Install Python Packages:**
    It's recommended to create a virtual environment to keep your project dependencies isolated.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    pip install -r requirements.txt
    ```

3.  **Set Environment Variables:**
    You need to set the following environment variables.  The best way to do this depends on your operating system and hosting environment. Here are a few common methods:

    *   **Using `.env` file (Recommended for local development):**
        *   Install `python-dotenv`: `pip install python-dotenv`
        *   Create a file named `.env` in the root directory of your repository.
        *   Add the following lines to `.env`, replacing the placeholders with your actual tokens and API key:
            ```
            GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
            SLACK_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE (starts with xoxb-)
            SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE (starts with xapp-)
            ```
        *   *(No changes to the Python scripts are needed as they already use `os.environ.get()`)*

    *   **Directly in your shell (For testing or simple setups):**
        *   **Linux/macOS:**
            ```bash
            export GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
            export SLACK_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE
            export SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE
            ```
        *   **Windows (Command Prompt):**
            ```cmd
            set GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
            set SLACK_TOKEN=YOUR_SLACK_BOT_TOKEN_HERE
            set SLACK_APP_TOKEN=YOUR_SLACK_APP_TOKEN_HERE
            ```
        *   **Windows (PowerShell):**
            ```powershell
            $env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"
            $env:SLACK_TOKEN="YOUR_SLACK_BOT_TOKEN_HERE"
            $env:SLACK_APP_TOKEN="YOUR_SLACK_APP_TOKEN_HERE"
            ```
## Usage

1.  **Run the Bot:**
    Navigate to your repository directory in the terminal and run:
    ```bash
    python Main.py
    ```
    You should see output in your console indicating that the bot is connected and listening for messages.

2.  **Interact with the Bot in Slack:**
    *   **In any Slack channel where the bot is installed**, mention the bot using `@your-bot-name` (replace `your-bot-name` with the actual name of your Slack app).

    *   **Text Query:**
        ```slack
        @your-bot-name What is the capital of France?
        ```
        The bot will respond with Gemini's answer in the channel.

    *   **Image Analysis:**
        Upload an image to Slack and add a mention:
        ```slack
        @your-bot-name What is in this picture?
        ```
        Or, upload an image without text:
        ```slack
        @your-bot-name
        ```

    *   **Text and Image Query:**
        Upload an image and include a text question:
        ```slack
        @your-bot-name  Analyze this image and tell me if this is a healthy plant.
        (Image attached)
        ```

    *   **Image Generation (Currently Text Response Only):**
        ```slack
        @your-bot-name generate an image of a futuristic city
        ```

## Contributing

Contributions are welcome! If you want to contribute to this project, please follow these steps:

1.  Fork the repository.
2.  Create a new branch for your feature or bug fix.
3.  Make your changes and commit them.
4.  Submit a pull request to the main repository.
