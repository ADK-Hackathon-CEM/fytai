from google.adk.tools.tool_context import ToolContext
from calendar_assistant.utils import calendar_utils

def reschedule_event(event_id: str, start_time: str, end_time: str, location: str, event_type:str, tool_context:ToolContext) -> dict:
    """
    Edit an existing event in Google Calendar - reschedule individual event.

    Args:
        event_id (str): The ID of the event to edit
        start_time (str): New start time (e.g., "2023-12-31 14:00", pass empty string to keep unchanged)
        end_time (str): New end time (e.g., "2023-12-31 15:00", pass empty string to keep unchanged)
        location (str): New location (pass empty string to keep unchanged)
        event_type (str): Type of the event (single_event, parent_event)

    Returns:
        dict: Information about the edited event or error details
    """
    print(f"Sub agent called to reschedule event {event_id} of type {event_type}")
    try:
        user_events = tool_context.state.get("user_events", [])
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


        if event_type not in ["single_event", "parent_event", "recurrent_event"]:
            return {
                "status": "error",
                "message": f"Invalid event type: {event_type}. Must be one of 'single_event', 'parent_event', or 'recurrent_event'."
            }
        
        if event_type == "single_event":
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
                "message": "Single Event updated successfully",
                "event_id": updated_event['id'],
            }
        
        if event_type == "parent_event":
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
                "message": "Parent Event updated successfully. Proceed using 'adjust_planning' tool to update recurrent events.",
                "event_id": updated_event['id']
            }

    except Exception as e:
        return {"status": "error", "message": f"Error updating event: {str(e)}"}