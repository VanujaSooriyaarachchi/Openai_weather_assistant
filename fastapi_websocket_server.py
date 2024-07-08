import os
import requests
import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv

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


def get_weather_forecast(location: str):
    appid = os.getenv("OPENWEATHER_API_KEY")
    url = f'http://api.weatherapi.com/v1/current.json?q={location}&key={appid}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Extract relevant weather information
            temperature = data["current"]["temp_f"]

            # Return the weather data
            return {
                "temperature": temperature
            }
        else:
            return {}
    except requests.exceptions.RequestException as e:
        print("Error occurred during API request:", e)
        return {}


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
            print('Received message:', data)
            if "weather" in data.lower():
                location = data.split()[-1]
                forecast = get_weather_forecast(location)
                reply = f"The current temperature in {location} is {forecast['temperature']}°F."
            else:
                reply = create_assistant_response(data)

            await websocket.send_text(reply)
    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/")
async def get():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
