from google.adk.tools.tool_context import ToolContext

def check_type_of_event(event_id: str, tool_context: ToolContext) -> dict:
    """
    Function to check if the event is a single event or a recurrent event.
    """
    print(f"Sub agent called to check type of event {event_id}")
    user_events = tool_context.state.get("user_events", [])

    if not user_events:
        return {"status": "error", "message": "No user events found in memory."}

    for event in user_events:
        if event_id == event.get("parent_event_id"):
            if not event.get("instances"):
                return {
                    "status": "success",
                    "type": "single_event",
                    "alias": event.get("alias")
                }
            else:
                return {
                    "status": "success",
                    "type": "parent_event",
                    "alias": event.get("alias")
                }
        for instance in event.get("instances", []):
            if event_id == instance:
                parent_event_id = event.get("parent_event_id")
                parent_event_alias = event.get("alias")
                return {"status": "success", "type": "recurrent_event", "alias": event.get("alias"), "parent_event_alias": parent_event_alias}

    return {"status": "sucess","type": "single_event", "message": "Event not found in user events memory. Event was not created by this agent."}