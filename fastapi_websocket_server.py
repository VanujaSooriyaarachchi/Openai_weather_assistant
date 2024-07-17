import os
import requests
import openai
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import socketio
import json

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Socket.IO server
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")
app_asgi = socketio.ASGIApp(sio, app)

# Function to get weather forecast
def get_weather_forecast(location: str):
    appid = os.getenv("OPENWEATHER_API_KEY")
    if not appid:
        logger.error("OpenWeather API key is not set")
        return {"error": "OpenWeather API key is not set"}

    url = f'http://api.weatherapi.com/v1/current.json?q={location}&key={appid}'
    logger.info(f"Fetching weather data from URL: {url}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            logger.debug(f"API response: {data}")
            if "current" in data and "temp_f" in data["current"]:
                temperature = data["current"]["temp_f"]
                return {"temperature": temperature}
            else:
                logger.error(f"Invalid API response: {data}")
                return {"error": "Invalid API response"}
        else:
            logger.error(f"Error fetching weather data: {response.status_code} - {response.text}")
            return {"error": f"Error fetching weather data: {response.status_code}"}
    except requests.exceptions.RequestException as e:
        logger.error(f"Exception during API request: {e}")
        return {"error": "Exception during API request"}

# Function to create assistant response using OpenAI API
def create_assistant_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        logger.error(f"Exception during OpenAI API request: {e}")
        return "Sorry, I couldn't process your request."

# Socket.IO events
@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    global reply
    logger.info(f"Received message from {sid}: {data}")

    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        logger.error("Invalid JSON received")
        await sio.send(json.dumps({"message": "Invalid JSON received"}), to=sid)
        return

    user_message = data.get("message", "")

    if user_message.lower() == "open_chat":
        greeting_message = "Hi, I'm your weather assistant."
        await sio.send(json.dumps({"message": greeting_message}), to=sid)
        logger.info(f"Sent greeting message: {greeting_message}")
    elif "weather" in user_message.lower() or "temperature" in user_message.lower():
        location = user_message.split(" in ")[-1].replace("?", "").strip()
        forecast = get_weather_forecast(location)
        if "temperature" in forecast:
            reply = f"The current temperature in {location} is {forecast['temperature']}°F."
        else:
            reply = "Sorry, I couldn't fetch the weather data."
    else:
        reply = create_assistant_response(user_message)

    await sio.send(json.dumps({"message": reply}), to=sid)

# REST endpoint to trigger Socket.IO event
class EventMessage(BaseModel):
    message: str

@app.post("/trigger_event")
async def trigger_event(event_message: EventMessage):
    await sio.emit("message", json.dumps({"message": event_message.message}))
    return {"message": "Event triggered"}

# Serve HTML file for the root endpoint
@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app_asgi, host="0.0.0.0", port=5000)
