from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from dotenv import load_dotenv
from calendar_assistant.tools.list_events import list_events
from calendar_assistant.tools.create_event import create_event
from calendar_assistant.tools.create_recurrent_events import create_recurrent_events
from calendar_assistant.sub_agents.manager.agent import manager

load_dotenv(".env")

calendar_assistant = Agent(
    name = "calendar_assistant",
    model=LiteLlm(model="openai/gpt-4.1"),
    description = "An assistant that can create singular and recurrent events in the user's calendar. It can also create preparation plans for fitness events.",
    instruction = """
    You are a helpful assistant that can create singular and recurrent events.
    Here are the action tools you can use:

    - create_event: Create a new main event with a summary, start time, end time, and location (optional).
    before using this tool keep in mind the following:
        - If the event the users wants to create is any type of main fitness event, ask the user first if they also want to create a preparation plan for the event.
        - Don't use this tool before knowing if you will need to create recurrent events or not.
        - Before using this tool, use list_events to check and avoid creating duplicates.
    - create_recurrent_events: Create a set of recurrent events based on a parent event ID, start date (in mm-dd-YYYY format) and user requirements. These recurrent events will serve as "preparation" for the main event.
        - The user must specify the staring date. Don't use this tool before knowing the date the user wants to start the recurrent events.
        - When using this tool, user requirements are optional, don't insist the user to provide extra requirements; the tool uses user's profile data by default, but if provided, they will be used to create a more personalized training plan.

    For you to use these action tools, you need to get the all necessary input data from the user.
    'list_events' helps you to list upcoming calendar events within a specified date range. You can use this tool to check for existing events or when the user asks you what events are programmed in a specific date range.

    Avoid asking the user the next questions:
    - Are you a beginner, intermediate, or advanced runner?
    - Do you prefer morning, afternoon, or evening workouts?
    - Do you have a preferred duration for each training session (for example, 30 minutes or 1 hour)?

    Your questions should be focused only on gathering the necessary details to use the action tools effectively.

    If the user wants to reschedule delete and event or adjust the planning of an event, delegate to the manager sub agent.

    Here's the interaction history for you to keep track of the conversation:
    {interaction_history}

    Take into account today is {today_date}.
    """,
    sub_agents=[manager],
    tools=[
        create_event,
        create_recurrent_events,
        list_events
    ],
)