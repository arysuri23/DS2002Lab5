import requests, pgeocode
from bs4 import BeautifulSoup
import pandas as pd

#ask user for zipcode
#zipcode = input("Please enter a U.S. postal code that you would like to get 7-day forecast for: ")

nomi = pgeocode.Nominatim("us")
location = nomi.query_postal_code("22102")
while location['place_name'] == "NaN":
    zipcode = input("Invalid U.S. zipcode, enter a different one: ")
    location = nomi.query_postal_code("221022")
#convert to latitude and longitude
lat = location['latitude']
long = location['longitude']

url = "https://forecast.weather.gov/MapClick.php?lat=" + str(lat) + "&lon=" + str(long)

page = requests.get(url)
soup = BeautifulSoup(page.content, 'html.parser')
seven_day = soup.find(id="seven-day-forecast")
forecast_items = seven_day.find_all(class_="tombstone-container")
tonight = forecast_items[0]
period_tags = seven_day.select(".tombstone-container .period-name")
periods = [pt.get_text() for pt in period_tags]
short_descs = [sd.get_text() for sd in seven_day.select(".tombstone-container .short-desc")]
temps = [t.get_text() for t in seven_day.select(".tombstone-container .temp")]
descs = [d["title"] for d in seven_day.select(".tombstone-container img")]

#current conditions
current_conditions = soup.find(id="current-conditions")
conditions = current_conditions.select("td")
humidity = conditions[1]
wind_speed = conditions[3]
dewpoint = conditions[7]
last_update = conditions[13].get_text()
index = 0
for char in range(len(last_update)):
    if last_update[char].isdigit():
        index = char
        break
last_update = last_update[char:]

curr = pd.DataFrame({
    "humidity": humidity,
    "wind_speed": wind_speed,
    "dewpoint": dewpoint,
    "last_update": last_update.strip()
}, index=[0])
print("Current conditions: ")
print(curr)

weather = pd.DataFrame({
 "period": periods,
 "short_desc": short_descs,
 "temp": temps,
 "desc":descs
})
print("Seven day forecast:")
print(weather)

