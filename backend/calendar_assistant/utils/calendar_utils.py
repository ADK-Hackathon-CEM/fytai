"""
Utility functions for Google Calendar integration.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define scopes needed for Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Path for token storage


def get_calendar_service(access_token: str):
    """
    Creates a Google Calendar service object from a user's access token.

    Args:
        access_token: The user's OAuth 2.0 access token obtained from the frontend.

    Returns:
        A Google Calendar service object or None if the token is invalid or expired.
    """
    if not access_token:
        print("Error: Access token is required.")
        return None

    try:
        # Crea las credenciales directamente desde el access token.
        # Nota: estas credenciales no se pueden refrescar y son de corta duración.
        creds = Credentials(token=access_token)
        
        # Construye el servicio de Google Calendar.
        service = build("calendar", "v3", credentials=creds)
        return service
        
    except HttpError as error:
        # El error más común aquí es que el token sea inválido o haya expirado.
        print(f"An error occurred: {error}")
        return None


def format_event_time(event_time):
    """
    Format an event time into a human-readable string.

    Args:
        event_time (dict): The event time dictionary from Google Calendar API

    Returns:
        str: A human-readable time string
    """
    if "dateTime" in event_time:
        # This is a datetime event
        dt = datetime.fromisoformat(event_time["dateTime"].replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %I:%M %p")
    elif "date" in event_time:
        # This is an all-day event
        return f"{event_time['date']} (All day)"
    return "Unknown time format"


def parse_datetime(datetime_str):
    """
    Parse a datetime string into a datetime object.

    Args:
        datetime_str (str): A string representing a date and time

    Returns:
        datetime: A datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %I:%M %p",
        "%m/%d/%Y",
        "%B %d, %Y %H:%M",
        "%B %d, %Y %I:%M %p",
        "%B %d, %Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(datetime_str, fmt)
        except ValueError:
            continue

    return None


def normalize_date_string(date_str: str) -> str:
    """
    Try to parse a date string in various formats and return it formatted as %m-%d-%Y.

    Args:
        date_str (str): Input date string.

    Returns:
        str: Date formatted as %m-%d-%Y.

    Raises:
        ValueError: If none of the formats match the input.
    """
    possible_formats = [
        "%m-%d-%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%Y/%m/%d",
        "%m/%d/%Y",
        "%d/%m/%Y"
    ]

    for fmt in possible_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            return date_obj.strftime("%m-%d-%Y")
        except ValueError:
            continue

    return date_str

def get_current_time() -> dict:
    """
    Get the current time and date
    """
    now = datetime.now()

    # Format date as MM-DD-YYYY
    formatted_date = now.strftime("%m-%d-%Y")

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": formatted_date,
    }


def get_upcoming_events(access_token, days=30, max_results=10):
    """
    Get upcoming events from Google Calendar for the specified number of days.
    
    Args:
        days (int): Number of days to look ahead (default: 30)
        max_results (int): Maximum number of events to return (default: 10)
    
    Returns:
        list: A list of events in JSON format, or None if there's an error
    """
    try:
        # Get the authenticated calendar service
        service = get_calendar_service(access_token)
        if not service:
            return None

        # Calculate time range
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        future = (datetime.utcnow() + timedelta(days=days)).isoformat() + 'Z'

        # Call the Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=future,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Format the events with human-readable time
        formatted_events = []
        for event in events:
            formatted_event = {
                'id': event.get('id'),
                'summary': event.get('summary', 'No title'),
                'description': event.get('description', ''),
                'start': format_event_time(event['start']),
                'end': format_event_time(event['end']),
                'raw_start': event['start'],
                'raw_end': event['end'],
                'location': event.get('location', ''),
                'status': event.get('status'),
                'creator': event.get('creator', {}).get('email', '')
            }
            formatted_events.append(formatted_event)

        return formatted_events

    except Exception as e:
        print(f"Error getting upcoming events: {e}")
        return None