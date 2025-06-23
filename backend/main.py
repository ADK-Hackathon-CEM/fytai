from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from calendar_assistant.agent import calendar_assistant
from utils import call_agent_async, add_user_query_to_history, remove_all_pycache, get_profile_data, get_user_events, save_user_events, update_user_events, get_access_token
import asyncio
from dotenv import load_dotenv
from calendar_assistant.utils.calendar_utils import get_current_time, get_upcoming_events
from flask import Flask, request, jsonify, session
import threading
import os
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from calendar_assistant.utils.clean_user_events import clean_user_events
import asyncio

#remove_all_pycache()

app = Flask(__name__)
APP_NAME = "Calendar Assistant"
app.secret_key = os.urandom(24) # Generate a random secret key
CORS(app)

_db_client = None

def _initialize_firestore_client():
    """
    Initialize Firebase and return the Firestore client.
    """
    global _db_client
    if _db_client is None:
        try:
            firebase_admin.get_app()
        except ValueError:
            try:
                cred = credentials.Certificate("hackathon--adk-firebase-adminsdk-fbsvc-cf18928e0c.json")
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK inicializado desde firebase_tools.py")
            except Exception as e:
                print(f"Error al inicializar Firebase Admin SDK: {e}")
                raise

        _db_client = firestore.client()
        print("Cliente de Firestore obtenido.")
    return _db_client

_db_client = _initialize_firestore_client()

session_service = InMemorySessionService()

user_runners = {}
user_session_ids = {}

@app.route("/", methods=["POST"])
def chatbot():
    data = request.get_json()
    USER_ID = data.get("user_id")
    if not USER_ID:
        print("User not logged in.")
        return jsonify({"error": "User not logged in."}), 401

    runner = user_runners.get(USER_ID)
    SESSION_ID = user_session_ids.get(USER_ID)
    if runner is None or SESSION_ID is None:
        return jsonify({"error": "Agent not initialized yet."}), 503
    print(f"Chatbot called for user: {USER_ID}")
    user_input = data.get("message", "")
    if not user_input:
        return jsonify({"error": "No message provided."}), 400
    adk_session = asyncio.run(session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
    ))
    adk_session.state["user_input"] = user_input
    async def process():
        await add_user_query_to_history(
            session_service, APP_NAME, USER_ID, SESSION_ID, user_input
        )
        response = await call_agent_async(runner, USER_ID, SESSION_ID, user_input)
        current_adk_session = await session_service.get_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            session_id=SESSION_ID,
        )
        user_events = current_adk_session.state.get("user_events", [])
        cleaned = clean_user_events(user_events, get_access_token(USER_ID))
        save_user_events(USER_ID, cleaned)
        await update_user_events(session_service, APP_NAME, USER_ID, SESSION_ID, cleaned)
        return response
    response = asyncio.run(process())

    return jsonify({"response": response})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get("user_id")
    session['user_id'] = user_id

    USER_ID = request.json.get('user_id')
    session['user_id'] = USER_ID
    print(f"Login successful for user: {session['user_id']}")
    initial_state = {
        "interaction_history": [],
        "today_date": get_current_time(),
        "user_events": get_user_events(USER_ID),
        "profile_data": get_profile_data(USER_ID),
        "access_token" : get_access_token(USER_ID),
        "user_input" : ""
    }
    async def init_agent_for_user():
        # firebase

        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        runner = Runner(
            agent=calendar_assistant,
            app_name=APP_NAME,
            session_service=session_service,
        )
        user_runners[USER_ID] = runner
        user_session_ids[USER_ID] = new_session.id

    asyncio.run(init_agent_for_user())
    return jsonify({"message": "Login successful"}), 200

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

@app.route('/get_user_id', methods=['GET'])
def get_user_id():
    if 'user_id' in session:
        return jsonify({"user_id": session['user_id']}), 200
    return jsonify({"message": "No user ID found"}), 404

@app.route('/get_next_events', methods=['GET'])
def get_next_events():
    USER_ID = request.args.get('user_id')
    if not USER_ID:
        return jsonify({"error": "User not logged in."}), 401

    user_events = get_upcoming_events(get_access_token(USER_ID))
    if not user_events:
        return jsonify({"error": "No events found."}), 404
    next_events = [event for event in user_events]
    return jsonify(next_events), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=True)