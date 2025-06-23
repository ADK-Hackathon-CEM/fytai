from google.adk.tools.tool_context import ToolContext
from calendar_assistant.utils import calendar_utils

def reschedule_recurrent_event(event_id: str, start_time: str, end_time: str, location: str, tool_context:ToolContext) -> dict:
    """
    Edit an existing event in Google Calendar - reschedule recurrent event.

    Args:
        event_id (str): The ID of the event to edit
        start_time (str): New start time (e.g., "2023-12-31 14:00", pass empty string to keep unchanged)
        end_time (str): New end time (e.g., "2023-12-31 15:00", pass empty string to keep unchanged)
        location (str): New location (pass empty string to keep unchanged)

    Returns:
        dict: Information about the edited event or error details
    """
    print(f"Sub agent called to reschedule recurrent event {event_id}")
    try:
        # Get calendar service
        token = tool_context.state.get("access_token")
        service = calendar_utils.get_calendar_service(token)
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Always use primary calendar
        calendar_id = "primary"

        # First get the existing event
        try:
            event = (
                service.events().get(calendarId=calendar_id, eventId=event_id).execute()
            )
        except Exception:
            return {
                "status": "error",
                "message": f"Event with ID {event_id} not found in primary calendar.",
            }

        # Get timezone from the original event
        timezone_id = "America/Mexico_City"  # Default
        if "start" in event and "timeZone" in event["start"]:
            timezone_id = event["start"]["timeZone"]

        # Update start time if provided
        if start_time:
            start_dt = calendar_utils.parse_datetime(start_time)
            if not start_dt:
                return {
                    "status": "error",
                    "message": "Invalid start time format. Please use YYYY-MM-DD HH:MM format.",
                }
            event["start"] = {"dateTime": start_dt.isoformat(), "timeZone": timezone_id}
        # Update end time if provided
        if end_time:
            end_dt = calendar_utils.parse_datetime(end_time)
            if not end_dt:
                return {
                    "status": "error",
                    "message": "Invalid end time format. Please use YYYY-MM-DD HH:MM format.",
                }
            event["end"] = {"dateTime": end_dt.isoformat(), "timeZone": timezone_id}
        # Update location if provided
        if location:
            event["location"] = location

        # Update the event
        updated_event = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        print(f"Updated event ID: {updated_event['id']}")

        return {
            "status": "success",
            "message": "Event updated successfully",
            "event_id": updated_event['id'],
        }

    except Exception as e:
        return {"status": "error", "message": f"Error updating event: {str(e)}"}