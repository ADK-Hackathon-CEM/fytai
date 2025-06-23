from google.adk.tools.tool_context import ToolContext
from calendar_assistant.utils import calendar_utils

def delete_event(event_id: str, event_type: str, tool_context:ToolContext) -> dict:
    """
    Delete an event from Google Calendar.

    Args:
        event_id (str): The unique ID of the event to delete
        event_type (str): The type of the event (single_event, parent_event, recurrent_event)

    Returns:
        dict: Operation status and details
    """
    print(f"Sub agent called to delete event {event_id} of type {event_type}")
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

        # Depending on the event type, we need to handle it differently
        if event_type not in ["single_event", "parent_event", "recurrent_event"]:
            return {
                "status": "error",
                "message": f"Invalid event type: {event_type}. Must be one of 'single_event', 'parent_event', or 'recurrent_event'."
            }
        
        elif event_type in ["single_event", "recurrent_event"]:
            # Call the Calendar API to delete the event
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            
            # Update user_events
            updated_events = []
            for event in user_events:
                if event_type == "single_event" and event_id == event.get("parent_event_id"):
                    continue  # remove this parent event
                elif event_type == "recurrent_event" and event_id in event.get("instances", []):
                    event["instances"] = [i for i in event["instances"] if i != event_id]
                updated_events.append(event)
            
            tool_context.state["user_events"] = updated_events

        elif event_type == "parent_event":
            # First, delete all instance events
            for event in user_events:
                if event.get("parent_event_id") == event_id:
                    for instance_id in event.get("instances", []):
                        try:
                            service.events().delete(calendarId=calendar_id, eventId=instance_id).execute()
                        except Exception as e:
                            print(f"Warning: Failed to delete instance {instance_id}: {e}")
                    break

            # Then delete the parent event
            service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
            
            # Remove the whole dictionary from user_events
            user_events = [event for event in user_events if event.get("parent_event_id") != event_id]
            tool_context.state["user_events"] = user_events

        return {
            "status": "success",
            "message": f"Event {event_id} has been deleted successfully",
            "event_id": event_id,
        }

    except Exception as e:
        return {"status": "error", "message": f"Error deleting event: {str(e)}"}