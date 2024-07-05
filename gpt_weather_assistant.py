import datetime as dt 
import requests

BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
API_KEY = "8df75a916e6ea5e9a30a982e2a5f4037"

def kelvin_to_celsius(kelvin):
        celsius = kelvin - 273.15
        return celsius

while True:
    CITY = input("Enter a city: ")

    url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp_kelvin = data['main']['temp']
            temp_celsius = kelvin_to_celsius(temp_kelvin)
            print(f"Temperature in {CITY}: {temp_celsius:.2f}°C")
        else:
            print(f"Failed to retrieve data. Status code: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

    choice = input("Do you want to check another city? (yes/no): ").lower()

    if choice != 'yes':
        print("Exiting program...")
        break