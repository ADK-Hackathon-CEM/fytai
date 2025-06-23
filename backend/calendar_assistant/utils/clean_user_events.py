from calendar_assistant.utils.calendar_utils import get_calendar_service

def clean_user_events(user_events: list, token) -> list:
    """
    Validate user_events against the actual Google Calendar. Remove missing or cancelled parent/instance events.

    Args:
        user_events (list): A list of user event dictionaries.

    Returns:
        list: A cleaned list of user events.
    """
    service = get_calendar_service(token)
    if not service:
        print("Google Calendar service initialization failed.")
        return user_events

    cleaned_user_events = []

    for event in user_events:
        parent_id = event.get("parent_event_id")
        alias = event.get("alias", "Unnamed")
        instances = event.get("instances", [])

        try:
            parent = service.events().get(calendarId="primary", eventId=parent_id).execute()
            if parent.get("status") == "cancelled":
                service.events().delete(calendarId="primary", eventId=parent_id).execute()
                raise Exception("Parent event is cancelled")

            # Parent is valid; now clean instances
            valid_instances = []
            for instance_id in instances:
                try:
                    inst = service.events().get(calendarId="primary", eventId=instance_id).execute()
                    if inst.get("status") != "cancelled":
                        valid_instances.append(instance_id)
                except:
                    continue
            event["instances"] = valid_instances
            cleaned_user_events.append(event)

        except:
            print(f"Parent event {parent_id} for alias '{alias}' does not exist or is cancelled.")
            # Parent doesn't exist or is cancelled
            for instance_id in instances:
                try:
                    service.events().delete(calendarId="primary", eventId=instance_id).execute()
                except:
                    continue
            # Don't append this parent event
    return cleaned_user_events