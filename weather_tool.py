import requests
import urllib.parse
import re

class WeatherTool:
    """
    Implements the Model Context Protocol tool for fetching weather data directly from OpenWeatherMap.
    """

    API_KEY = "b64bd32bc583620420b95bdcdde304c5"
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        """
        Initializes the weather tool with metadata for the Model Context Protocol (MCP).
        """
        self.tool_info = {
            "name": "weather_tool",
            "description": "Fetches real-time weather information for a given location.",
            "parameters": {
                "location": {
                    "type": "string",
                    "description": "City or location name to get the weather for."
                }
            }
        }
    
    def extract_location(self, user_query):
        """
        Extracts the most likely location from the user's query.

        Args:
            user_query (str): The full text input from the user.

        Returns:
            str: Extracted location or None if not found.
        """
        user_query = user_query.strip()

        # Look for patterns
        match = re.search(r'weather in ([\w\s,-]+)', user_query, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
        else:
            # Try extracting last word as fallback
            words = user_query.split()
            location = words[-1] if words else None

        # Normalize location
        if location:
            location = location.title()

        return location

    def call_tool(self, parameters):
        """
        Calls the OpenWeatherMap API directly with the given location.

        Parameters:
            parameters (dict): Must contain a "location" key.

        Returns:
            dict: JSON-RPC 2.0 formatted response.
        """

        # Gets location from parameters
        location = parameters.get("location")

        # If location is missing, return an error
        if not location:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32602, "message": "Missing 'location' parameter"},
                "id": None
            }

        # Clean and normalize location
        location = self.extract_location(location)

        if not location:
            return {"jsonrpc": "2.0", "error": {"code": -32602, "message": "Invalid location provided"}, "id": None}

        # Encode location
        location_encoded = urllib.parse.quote(location)

        # Construct API request URL with parameters
        url = f"{self.BASE_URL}?q={location_encoded}&appid={self.API_KEY}&units=metric"

        try:
            # Send a GET request to the OpenWeatherMap API
            response = requests.get(url)

            # Returns the result if code = 200
            if response.status_code == 200:
                data = response.json()
                
                # Extract relevant weather data
                temperature = data["main"]["temp"]
                condition = data["weather"][0]["description"].capitalize()

                return {
                    "jsonrpc": "2.0",
                    "result": {
                        "location": location,
                        "temperature": f"{temperature}°C",
                        "condition": condition
                    },
                    "id": 1
                }
            
            # Failed return error city not found
            elif response.status_code == 404:
                return {"jsonrpc": "2.0", "error": {"code": -32000, "message": "City not found"}, "id": 1}
            
            # Failed return other API error
            else:
                return {"jsonrpc": "2.0", "error": {"code": -32000, "message": f"API Error: {response.status_code}"}, "id": 1}

        except Exception as e:
            # If any error occurs, return an error
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32099,
                    "message": f"Request failed: {str(e)}"
                },
                "id": 1
            }
