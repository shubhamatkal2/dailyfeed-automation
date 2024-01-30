#VALUES
import requests
#api key for nasa
nasa_apod_api_key = "aMl9SENMnFAAmx0L31NNHpQ1EkPT5O5sd2POD3hF"
# Wikipedia API endpoint for events on this day
wiki_api_url = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/"
api_key_weather = '4f69271658fc4924ba6110506242701'  # Replace with your actual API key
latitude = '19.83392508672324'  # Replace with the desired latitude
longitude = '75.88525328466898'  # Replace with the desired longitude
harvard_art_api = "a4637dea-dbd1-462d-a11d-4f9647b8937a"


def get_weather(api_key, lat, lon):
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        'key': api_key,
        'q': f"{lat},{lon}",
        'days': 1  # Get forecast for 1 day (today)
    }

    response = requests.get(base_url, params=params)
    data = response.json()

    if 'error' in data:
        print(f"Error: {data['error']['message']}")
        return None

    forecast = data['forecast']['forecastday'][0]
    date = forecast['date']
    condition = forecast['day']['condition']['text']
    temperature_celsius = forecast['day']['avgtemp_c']
    will_it_rain = forecast['day']['daily_will_it_rain']
    city = data['location']['name']

    condition_image_map = {
    'Clear': 'weather/sunny.png',  # Replace with actual image URL
    'Partly cloudy': 'weather/partly-cloudy.png',  # Replace with actual image URL
    'Cloudy': 'weather/cloudy.png',  # Replace with actual image URL
    'Rain':'weather/rain.png',  # Replace with actual image URL
    # Add more conditions and image URLs as needed
    }

    # Get image URL based on the condition
    condition_image_url = condition_image_map.get(condition)
    rain_statement = ""
    if will_it_rain == 0:
        rain_statement = "It will not rain today."
    elif will_it_rain == 1:
        rain_statement = "It will rain today!"
    print("Below is condition")
    print(condition)
    print(type(condition))
    return city,condition,temperature_celsius,rain_statement, condition_image_url

get_weather(api_key_weather, lat=latitude, lon=longitude)