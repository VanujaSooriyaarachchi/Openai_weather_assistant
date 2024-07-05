import openai
from dotenv import load_dotenv
import os
import requests

load_dotenv()

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

class AssistantManager:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        openai.api_key = api_key
        self.model = model

    def create_assistant(self, user_message):
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ]
        )
        return response

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    manager = AssistantManager(api_key)

    location = input("Enter your location: ")
    user_message = f"I need the weather forecast for {location}."

    response = manager.create_assistant(user_message)

    assistant_reply = response['choices'][0]['message']['content']
    print(assistant_reply)

if __name__ == "__main__":
    main()