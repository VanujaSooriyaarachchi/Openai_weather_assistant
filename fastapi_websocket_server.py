import os
import requests
import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
import logging

load_dotenv()

app = FastAPI()

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


def get_weather_forecast(location: str):
    appid = os.getenv("OPENWEATHER_API_KEY")
    url = f'http://api.weatherapi.com/v1/current.json?q={location}&key={appid}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Log the full response for debugging purposes
            logger.info(f"API response: {data}")
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


def create_assistant_response(user_message):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_message}
        ]
    )
    return response['choices'][0]['message']['content']


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f'Received message: {data}')
            if "weather" in data.lower() or "temperature" in data.lower():
                # Extract location from the message
                location = data.split(" in ")[-1].replace("?", "").strip()
                forecast = get_weather_forecast(location)
                if "temperature" in forecast:
                    reply = f"The current temperature in {location} is {forecast['temperature']}°F."
                else:
                    reply = "Sorry, I couldn't fetch the weather data."
            else:
                reply = create_assistant_response(data)

            await websocket.send_text(reply)
    except WebSocketDisconnect:
        logger.info("Client disconnected")


@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
