import ollama
import re
from weather_tool import WeatherTool

# Weather keywords for determining if query is about the weather
WEATHER_KEYWORDS = [
    "weather", "temperature", "forecast", "rain", "humidity", "wind",
    "climate", "storm", "conditions", "sunny", "cloudy", "fog", 
    "snow", "hail", "hailstorm", "thunder", "drizzle"
]

# Initialize the MCP weather tool
weather_tool = WeatherTool()

def is_weather_query(user_input):
    """
    Determines if the user is asking about the weather.

    Args:
        user_input (str): The user's question.

    Returns:
        bool: True if it's a weather-related query, False otherwise.
    """
    return any(word in user_input.lower() for word in WEATHER_KEYWORDS)

def extract_location(user_input):
    """
    Extracts a potential location from a natural language query.

    Args:
        user_input (str): The user's question.

    Returns:
        str or None: The extracted location or None if not found.
    """
    match = re.search(r"(?:weather in|in|at)\s+([\w\s]+)", user_input, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    else:
        # If it's a single word and looks like a location, assume it's the city
        if len(user_input.split()) == 1:
            location = user_input.strip()
        else:
            return None  # No valid location found
    return location.title()

# Keeps running
while True:
    user_input = input("Ask me something: ").strip()

    # Only trigger if it's a weather-related query
    if is_weather_query(user_input):
        location = extract_location(user_input)

        if location:
            weather_info = weather_tool.call_tool({"location": location})
            
            # Error handling
            if "error" in weather_info:
                print(f"Error: {weather_info['error']['message']}")
            else:
                print(f"Location: {weather_info['result']['location']}")
                print(f"Temperature: {weather_info['result']['temperature']}")
                print(f"Condition: {weather_info['result']['condition']}")
        else:
            print("I couldn't determine the location. Please specify a city.")
    else:
        # Let Ollama handle other queries
        response = ollama.chat("gemma", messages=[{"role": "user", "content": user_input}])
        print(response["message"]["content"])
