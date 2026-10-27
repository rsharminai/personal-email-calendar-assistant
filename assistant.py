#!/usr/bin/env python3
"""
Personal Assistant: Extract info from Gmail and update Google Calendar.
Requires credentials.json from Google Cloud Console.
"""

import os.path
import base64
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import dateparser

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def get_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def get_gmail_service(creds):
    return build('gmail', 'v1', credentials=creds)

def get_calendar_service(creds):
    return build('calendar', 'v3', credentials=creds)

def fetch_recent_emails(gmail_service, max_results=10):
    """Fetch recent emails."""
    try:
        results = gmail_service.users().messages().list(
            userId='me', maxResults=max_results, q='is:unread OR newer_than:1d'
        ).execute()
        messages = results.get('messages', [])
        emails = []
        for msg in messages:
            msg_data = gmail_service.users().messages().get(
                userId='me', id=msg['id'], format='full'
            ).execute()
            payload = msg_data.get('payload', {})
            headers = payload.get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            from_ = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            # Extract body
            body = ''
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        break
            else:
                data = payload.get('body', {}).get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            emails.append({
                'id': msg['id'],
                'subject': subject,
                'from': from_,
                'body': body[:2000]  # Limit length
            })
        return emails
    except HttpError as error:
        print(f'An error occurred: {error}')
        return []

def extract_event_info(email):
    """Simple heuristic extraction of event info from email.
    For production, replace with LLM call (OpenAI, etc.).
    """
    text = f"{email['subject']} {email['body']}".lower()
    # Look for date/time patterns
    dt = dateparser.parse(text, settings={'PREFER_DATES_FROM': 'future'})
    if not dt:
        return None
    
    # Assume 1 hour duration if not specified
    end_dt = dt + timedelta(hours=1)
    
    # Simple title from subject
    title = email['subject'][:100]
    
    return {
        'summary': title,
        'description': f"Extracted from email by {email['from']}\n\n{email['body'][:500]}",
        'start': dt.isoformat(),
        'end': end_dt.isoformat(),
        'source_email': email['id']
    }

def create_calendar_event(calendar_service, event_info):
    """Create an event in Google Calendar."""
    event = {
        'summary': event_info['summary'],
        'description': event_info['description'],
        'start': {
            'dateTime': event_info['start'],
            'timeZone': 'UTC',  # Adjust as needed
        },
        'end': {
            'dateTime': event_info['end'],
            'timeZone': 'UTC',
        },
    }
    try:
        created = calendar_service.events().insert(calendarId='primary', body=event).execute()
        print(f"Event created: {created.get('htmlLink')}")
        return created
    except HttpError as error:
        print(f'Calendar error: {error}')
        return None

def main():
    print("Starting Personal Email-Calendar Assistant...")
    creds = get_credentials()
    gmail = get_gmail_service(creds)
    calendar = get_calendar_service(creds)
    
    emails = fetch_recent_emails(gmail)
    print(f"Found {len(emails)} recent emails.")
    
    for email in emails:
        print(f"\nProcessing: {email['subject']}")
        event = extract_event_info(email)
        if event:
            print(f"  -> Detected event: {event['summary']} at {event['start']}")
            # Uncomment to actually create:
            # create_calendar_event(calendar, event)
            print("  (Creation commented out for safety - uncomment in code)")
        else:
            print("  -> No clear event detected.")
    
    print("\nDone. Review events and uncomment creation if satisfied.")

if __name__ == '__main__':
    main()
