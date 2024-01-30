import pandas as pd
import os
import requests
import random
import time
from datetime import datetime
from affirmations import affirmation_set
import wikiquotes
from marathi import hindu_quotes
from bible import bible_verses
from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

#VALUES
#api key for nasa
nasa_apod_api_key = os.environ.get('NASAAPI')
# Wikipedia API endpoint for events on this day
wiki_api_url = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/"
api_key_weather =os.environ.get('WEATHERAPI')
latitude = '19.83392508672324'  # Replace with the desired latitude
longitude = '75.88525328466898'  # Replace with the desired longitude
harvard_art_api = os.environ.get('HARVARDAPI')


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
    'Sunny': 'weather/sunny.png',  # Replace with actual image URL
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
    return city,condition,temperature_celsius,rain_statement, condition_image_url

def pick_random_affirmation():
    # Pick a random affirmation from the set
    random_affirmation  = random.choice(tuple(affirmation_set))
    
    # Format the selected affirmation in HTML
    html_affirmation = f"{random_affirmation}"
    return html_affirmation


def fetch_nasa_image():
    # Fetch NASA's Picture of the Day from APOD API
    # You may need to replace DEMO_KEY with your NASA API key
    url = "https://api.nasa.gov/planetary/apod"
    params = {"api_key": nasa_apod_api_key}
    response = requests.get(url, params=params)
    data = response.json()
    return data


#create a function to fetch things happened on today from wiki
def fetch_on_this_day():
    # Get the current date
    current_date = datetime.now()
    month = str(current_date.month).zfill(2)  # Ensure leading zero for single-digit months
    day = str(current_date.day).zfill(2)      # Ensure leading zero for single-digit days

    # Construct the API URL for the current date
    api_url_today = f"{wiki_api_url}{month}/{day}"

    # Make a GET request to the Wikipedia API
    response = requests.get(api_url_today)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        return data
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")

#wikiquote for the day
def generate_wiki_quote_div():
    wikiquote_tuple = wikiquotes.quote_of_the_day("english")
    quote, author = wikiquote_tuple

    # Inline styles for simplicity
    div_style = "font-family: Arial, sans-serif; border: 1px solid #ccc; padding: 10px;"

    # HTML div template
    div_template = f"""
    <div style="{div_style}">
        <h1>Quote of the Day</h1>
        <blockquote>
            <p>{quote}</p>
            <footer>{author}</footer>
        </blockquote>
    </div>
    """

    return quote, author


def generate_art_json():
    base_url = "https://api.harvardartmuseums.org/object"
    api_key = harvard_art_api  # Replace with your Harvard API key
    params = {
        'apikey': api_key,
        'size': 1,
        'sort': 'random'
    }

    max_retries = 3
    delay_seconds = 3

    for _ in range(max_retries):
        response = requests.get(base_url, params=params)
        data = response.json()

        try:
            image_url = data['records'][0]['primaryimageurl']
            print("Image URL exists for art")
            return data, image_url
        except KeyError:
            print("Image URL is None. Retrying after 3 seconds...")
            time.sleep(delay_seconds)

    # If all retries fail, return None
    print("Image URL is still None after retries.")
    return data, None


def create_art_div(art_data):
    title = art_data['records'][0]['title']
    artist_name  = art_data.get('records', [{}])[0].get('people', [{}])[0].get('displayname', 'Not Available')
    art_link = art_data['records'][0].get("url", "Not available")    #['url']

    return title ,artist_name, art_link


def create_html_div(heading, content):
    return f"<div><h2>{heading}</h2><p>{content}</p></div>"

def get_random_marathi_quote():
    selected_marathi = random.choice(hindu_quotes)
    return selected_marathi

def get_random_bible_verse():
    selected_bible_verse = random.choice(bible_verses)
    verse_text = selected_bible_verse["verse"]
    reference = selected_bible_verse["reference"]
    return f"{verse_text} {reference}"

def get_random_quran_verse():
    # Read Quran verses from CSV
    quran_df = pd.read_csv('./src/quranverses.csv', encoding='latin1')

    # Randomly select a verse
    selected_verse = quran_df.sample(n=1)

    # Extract verse details
    verse_text = selected_verse['Verse'].values[0]

    # Create HTML div for Quran verse
    return verse_text


def fetch_html_for_this_day(on_this_day):
  events_today = on_this_day.get("selected", [])
  # Format events as HTML and print

  html_events = '<ul style="margin-left:45px; font-size: 20px;color: #030637;">'
  for event in events_today:
      event_text = event.get("text", "")
      event_year = event.get("year", "")
      html_events += f"<li>{event_text} ({event_year})</li>"
  html_events += "</ul>"
  return html_events



# #  data for variables
current_date = datetime.now().strftime("%Y-%m-%d")
current_day = datetime.now().strftime("%A")
r_aff = pick_random_affirmation()
city,condition,temperature_celsius,will_it_rain, condition_image__= get_weather(api_key_weather, latitude, longitude)
nasa_data = fetch_nasa_image()
wikiquote_ , wikiauthor_ = generate_wiki_quote_div()
get_random_marathi_quote_ = get_random_marathi_quote()
get_random_bible_verse_ = get_random_bible_verse()
get_random_quran_verse_ = get_random_quran_verse()
#below is parent functions of art 
art_data, image_url_art = generate_art_json()
#done till this
arttitle_ , artist_ , artlink_ = create_art_div(art_data)  #this is dependent
artlink_show = ""
if image_url_art != None:
    artlink_show = image_url_art
else:
    artlink_show = "https://nrs.harvard.edu/urn-3:HUAM:777601"  
html_events_ = fetch_html_for_this_day(fetch_on_this_day())   #this is dependent (now i have data so i am using that)
time_string_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S")



# Function to update variables
def update_variables():
    global current_date, current_day, r_aff, city, condition, temperature_celsius, will_it_rain, condition_image__
    global nasa_data, wikiquote_, wikiauthor_, get_random_marathi_quote_, get_random_bible_verse_, get_random_quran_verse_
    global art_data, image_url_art, arttitle_, artist_, artlink_, artlink_show, html_events_, time_string_

    # Update data
    current_date = datetime.now().strftime("%Y-%m-%d")
    current_day = datetime.now().strftime("%A")
    r_aff = pick_random_affirmation()
    city, condition, temperature_celsius, will_it_rain, condition_image__ = get_weather(api_key_weather, latitude, longitude)
    nasa_data = fetch_nasa_image()
    wikiquote_, wikiauthor_ = generate_wiki_quote_div()
    get_random_marathi_quote_ = get_random_marathi_quote()
    get_random_bible_verse_ = get_random_bible_verse()
    get_random_quran_verse_ = get_random_quran_verse()

    # Art data
    art_data, image_url_art = generate_art_json()
    arttitle_, artist_, artlink_ = create_art_div(art_data)
    artlink_show = image_url_art if image_url_art else "https://nrs.harvard.edu/urn-3:HUAM:777601"

    # HTML events
    html_events_ = fetch_html_for_this_day(fetch_on_this_day())

    # Time string
    time_string_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_variables, 'cron', hour=5, minute=0)  # Schedule the update function every day at 5 am
scheduler.start()

@app.route('/')
def index():
    # Render the HTML file with variables
    return render_template('index.html', 
                           current_date=current_date, 
                           current_day=current_day, 
                           pick_random_affirmation = r_aff,
                           city_=city, 
                           condition_image_=str(condition_image__), 
                           condition_=condition, 
                           temp_=temperature_celsius, 
                           rain_=will_it_rain, 
                           nasa_data=nasa_data, 
                           wikiquote_=wikiquote_, 
                           wikiauthor_=wikiauthor_, 
                           get_random_marathi_quote=get_random_marathi_quote_, 
                           get_random_bible_verse=get_random_bible_verse_, 
                           get_random_quran_verse=get_random_quran_verse_, 
                           artlink_show = str(artlink_show),
                           arttitle_=arttitle_, 
                           artist_=artist_, 
                           artlink_=str(artlink_), 
                           html_events=html_events_, 
                           time_string=time_string_)

if __name__ == '__main__':
    app.run(debug=True)
