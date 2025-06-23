from calendar_assistant.tools.create_recurrent_events import create_recurrent_events
from google.adk.tools.tool_context import ToolContext
from calendar_assistant.utils import calendar_utils

def adjust_planning(parent_event_id: str, user_requirements: str, start_date:str, tool_context:ToolContext) -> dict:
    print(f"Sub agent called to adjust planning for parent event {parent_event_id}")
    try:
        user_events = tool_context.state.get("user_events", [])
        token = tool_context.state.get("access_token")
        service = calendar_utils.get_calendar_service(token)
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Always use primary calendar
        calendar_id = "primary"
        
        # Check if the parent_event_id is valid
        for event in user_events:
            if parent_event_id == event.get("parent_event_id"):
                if not event.get("instances"):
                    event_type = "single_event"
                    return {
                        "status": "error",
                        "message": "Invalid parent event ID. Ask the user to provide a valid parent event"
                    }
                else:
                    event_type = "parent_event"
                    break
            for instance in event.get("instances", []):
                if parent_event_id == instance:
                    # If the parent event ID matches an instance we overwrite the parent_event_id and point to a valid parent event
                    parent_event_id = event.get("parent_event_id")
                    event_type = "parent_event"
                    break
        
        # If we didn't find a valid parent event ID, return an error
        if not event_type or event_type != "parent_event":
            return {
                "status": "error",
                "message": f"Ivalid Parent event ID {parent_event_id}"
            }

        # Delete the recurrent events from the parent event and update the user_events
        if event_type == "parent_event":
            # First, delete all instance events
            for event in user_events:
                if event.get("parent_event_id") == parent_event_id:
                    for instance_id in event.get("instances", []):
                        try:
                            service.events().delete(calendarId=calendar_id, eventId=instance_id).execute()
                        except Exception as e:
                            print(f"Warning: Failed to delete instance {instance_id}: {e}")
                    # After deleting all instances, we can empty the instances list
                    event["instances"] = []
                    break
            
            # Remove the whole dictionary from user_events
            tool_context.state["user_events"] = user_events

        else:
            return {
                "status": "error",
                "message": f"Invalid parent event ID. Ask the user to provide a valid parent event."
            }
        
        # Now we can create the recurrent events based on the user requirements
        result = create_recurrent_events(
            parent_event_id=parent_event_id,
            user_requirements=user_requirements,
            start_date=start_date,
            tool_context=tool_context
        )

        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"Planning adjusted successfully for parent event {parent_event_id}."
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to adjust planning: {result['message']}"
            }

    except Exception as e:
        return {"status": "error", "message": f"Error adjusting planning from parent event ID: {str(e)}"}
