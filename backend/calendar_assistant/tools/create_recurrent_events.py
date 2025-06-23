from google.adk.tools.tool_context import ToolContext
from datetime import datetime, timedelta
from calendar_assistant.utils import helpers, calendar_utils, research
import json

def create_recurrent_events(parent_event_id:str, user_requirements:str, start_date:str, tool_context: ToolContext) -> dict:
    """
    Function to create a new planning.
    This function creates a set of recurrent events based on a summary, start date (in mm-dd-YYYY format) and a parent event ID.
    Args:
        parent_event_id (str): The ID of the parent event from which to create recurrent events.
        user_requirements (str): User requirements for the training plan (optional).
        start_date (str): The start date for the recurrent events in mm-dd-YYYY format.
    """
    print(f"Agent called create_recurrent_events with args: {parent_event_id}\n {start_date}")
    user_events = tool_context.state.get("user_events", [])
    profile_data = tool_context.state.get("profile_data", "No general info provided")
    user_input = getattr(tool_context.state, "user_input", "")
    token = tool_context.state["access_token"]
    if not token:
        return {"status": "error", "message": "Access token is missing. Please authenticate first."}

    try:
        weekly_plan = {"sunday":{}, "monday":{}, "tuesday":{}, "wednesday":{}, "thursday":{}, "friday":{}, "saturday":{}}
        schedule_preferences = profile_data

        ######### get weekday to know last sunday's dateavailability
        start_date = calendar_utils.normalize_date_string(start_date)
        date_obj = datetime.strptime(start_date, "%m-%d-%Y")
        days_to_subtract = (date_obj.weekday() + 1) % 7
        sunday_date = date_obj - timedelta(days=days_to_subtract)
        parent_event_summary, parsed_date = helpers.get_summary_from_event_id(parent_event_id, token)
        alias = parent_event_summary
        print(parsed_date)
        summary = helpers.get_summary(user_input, parent_event_summary)
        
        # Create a weekly plan based on the summary and google research
        weekly_plan_path = research.research_week_plan(summary, schedule_preferences, user_requirements)
        with open(weekly_plan_path, "r", encoding="utf-8") as f:
            content = f.read()
        days = weekly_plan.keys()
        days_to_add = 0
        parent_event_instances = []
        for day in days:
            day_event = helpers.get_day_event(day, sunday_date + timedelta(days=days_to_add), schedule_preferences, content, str(parsed_date))
            print(day_event)
            weekly_plan[day]["event"] = day_event

            data = json.loads(day_event.replace("```json", "").replace("```", "").strip())
            service = calendar_utils.get_calendar_service(token)
            created = service.events().insert(calendarId='primary', body=data).execute()
            print('Created event:', created.get('htmlLink'))

            # Get the event instances
            instances = service.events().instances(calendarId='primary', eventId=created['id']).execute()
            first_instace = instances['items'][0]
            instance_start = first_instace.get("start", {}).get("dateTime")
            instance_dt = datetime.strptime(instance_start, "%Y-%m-%dT%H:%M:%S%z")
            if instance_dt.date() < date_obj.date():
                service.events().delete(calendarId='primary', eventId=first_instace['id']).execute()
                print(f"Deleted only the instance on {instance_dt.date()} (before official start_date)")

            day_instances = service.events().instances(calendarId='primary', eventId=created['id']).execute()
            for instance in day_instances.get('items', []):
                intance_id = instance.get('id')
                parent_event_instances.append(intance_id)

            days_to_add += 1

        for event in user_events:
            if event.get("parent_event_id") == parent_event_id:
                event["instances"] = parent_event_instances
                break
        print(user_events)
        tool_context.state['user_events'] = user_events

        return {"status": "success", "message": f"Recurrent events '{summary}' created from {start_date}"}
    
    except Exception as e:
        print(f"Error creating recurrent events: {e}")
        return {"status": "error", "message": f"Error creating recurrent events: {str(e)}"}