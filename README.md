# Personal Email & Calendar Assistant

A Python-based personal assistant that reads your Gmail, extracts relevant information (meetings, deadlines, tasks), and updates your Google Calendar accordingly.

## Features
- Fetch recent unread or recent emails
- Parse emails for dates, times, events using simple heuristics or AI (optional OpenAI)
- Create or update Google Calendar events
- OAuth2 authentication with Google

## Prerequisites
- Python 3.9+
- Google Cloud Project with Gmail API and Google Calendar API enabled
- OAuth 2.0 credentials (Desktop app)

## Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/rsharminai/personal-email-calendar-assistant.git
   cd personal-email-calendar-assistant
   ```

2. **Install dependencies:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Google Cloud Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable **Gmail API** and **Google Calendar API**
   - Create OAuth 2.0 Client ID (Application type: Desktop app)
   - Download the JSON and save as `credentials.json` in the project root
   - Add your email as a test user on the OAuth consent screen

4. **Run the assistant:**
   ```bash
   python assistant.py
   ```
   On first run, it will open a browser for authentication and save `token.json`.

## Usage
- The script scans recent emails and proposes/creates calendar events.
- Customize the logic in `assistant.py` for better AI integration (add OpenAI key for smarter parsing).

## Security
- Never commit `credentials.json` or `token.json`
- Use environment variables for any API keys

## Extending
- Integrate with OpenAI/Anthropic for better email understanding
- Add email sending/replying
- Support Outlook via Microsoft Graph
- Deploy as a scheduled job (cron, GitHub Actions, etc.)

MIT License
