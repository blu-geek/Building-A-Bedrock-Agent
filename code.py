import json
import os
import requests
from datetime import datetime

def lambda_handler(event, context):
    # Extract information from the event
    agent = event['agent']
    actionGroup = event['actionGroup']
    function = event['function']
    parameters = event.get('parameters', [])
    
    # Initialize variables for city and units
    city = None
    units = 'Fahrenheit'
    
    # Extract 'city' and 'units' from parameters
    for param in parameters:
        if param['name'] == 'city':
            city = param['value']
        elif param['name'] == 'units':
            units = param['value']
    
    # Log extracted parameters
    print(f"City: {city}, Units: {units}")
    
    # API configuration
    API_KEY = os.environ.get('OPENWEATHERMAP_API_KEY')  # Store API key in Lambda environment variables
    unit_system = 'imperial' if units.lower() == 'fahrenheit' else 'metric'
    
    try:
        # Make API call to OpenWeatherMap
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': API_KEY,
            'units': unit_system
        }
        
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
        weather_data = response.json()
        
        # Extract relevant weather information
        temperature = weather_data['main']['temp']
        weather_description = weather_data['weather'][0]['description']
        humidity = weather_data['main']['humidity']
        feels_like = weather_data['main']['feels_like']
        
        # Create weather message
        weather_message = (
            f"Current weather in {city}: {temperature}°{units[0]} with {weather_description}. "
            f"Feels like {feels_like}°{units[0]}. Humidity: {humidity}%"
        )
        
        responseBody = {
            "TEXT": {
                "body": weather_message
            }
        }
        
    except requests.RequestException as e:
        print(f"Error fetching weather data: {str(e)}")
        responseBody = {
            "TEXT": {
                "body": f"Sorry, I couldn't fetch the weather information for {city}. Please try again later."
            }
        }
    
    # Construct the response
    action_response = {
        'actionGroup': actionGroup,
        'function': function,
        'functionResponse': {
            'responseBody': responseBody
        }
    }
    
    function_response = {
        'response': action_response,
        'messageVersion': event['messageVersion']
    }
    
    print("Response: {}".format(function_response))
    return function_response
