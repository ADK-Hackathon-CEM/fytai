
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from calendar_assistant.utils.calendar_utils import get_calendar_service
from dateutil import parser
from google.adk.tools.tool_context import ToolContext


def get_summary(user_input: str, parent_event_summary: str) -> str:
    """
    Generate a summary based on user input and an optional parent event summary.
    
    Args:
        user_input (str): The input provided by the user.
        parent_event_summary (str, optional): The summary of a parent event if available.
        
    Returns:
        str: A generated summary based on the provided inputs.
    """
    model = ChatOpenAI(model='gpt-4.1')

    prompt = f"""
    You are a helpful assistant that generates a summary based on user input and an optional parent event summary.
    Your summary will be used to do some research and planning for the user.
    Your task is to create a concise and informative summary that captures the essence of the user's input.
    User Input: {user_input}

    Parent Event Summary: {parent_event_summary if parent_event_summary else "No parent event summary provided. Answer only based on user input."}
    """

    # prompt = load_prompt('prompts/summary_generator.txt', variables)
    try:
        answer = model.invoke([HumanMessage(content=prompt)])
        answer_content = answer.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

    return answer_content.strip() if answer_content else None

def get_summary_from_event_id(event_id: str, token) -> str:
    """
    Extract a summary from an event dictionary.
    
    Args:
        event_id (str): The event id
        
    Returns:
        str: The summary extracted from the event.
    """
    service = get_calendar_service(token)
    if not service:
        return {
            "status": "error",
            "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            "events": [],
        }

    # ID del calendario y del evento
    calendar_id = 'primary'

    # Get event details
    event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
    start_datetime_str = event['start']['dateTime']              # '2025-06-15T10:00:00'
    dt = parser.isoparse(start_datetime_str)                     # datetime object
    formatted_date = dt.strftime("%Y%m%d")   

    if not event:
        print(f"Evento con ID {event_id} no encontrado.")
        return None

    # EXtract summary
    summary = event.get('summary', 'Untitled')
    print(f"Resumen del evento: {summary}")

    return summary, formatted_date


def get_day_event(day, date, availability, weekly_plan, parsed_date):
    model = ChatOpenAI(model='gpt-4.1')
    prompt = f"""
    You are a helpful assistant that generates a json-formatted event based on the availability, weekly plan path, and count.
    The day event you generate must be according to the provided day of the week.

    Day: {day}, {date}
    Availability: {availability} (24-hour format, e.g., 6-8 means 6 AM to 8 AM)
    Weekly Plan Path: {weekly_plan}
    UNTIL must be equal to: {parsed_date}

    ### Output format:
```json
{{
    'summary': 'Event Name',
    'description': 'Description of the event',
    'start': {{
        'dateTime': 'yyyy-mm-ddThh:mm:00',
        'timeZone': 'America/Mexico_City',
    }},
    'end': {{
        'dateTime': 'yyyy-mm-ddThh:mm:00',
        'timeZone': 'America/Mexico_City',
    }},
    'recurrence': [
        'RRULE:FREQ=WEEKLY;UNTIL={parsed_date}T050000Z'
    ]
}}
```
    """
    try:
        answer = model.invoke([HumanMessage(content=prompt)])
        answer_content = answer.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

    return answer_content.strip() if answer_content else None