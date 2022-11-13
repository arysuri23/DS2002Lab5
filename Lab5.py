import requests, pgeocode,  pymongo, pprint

from bs4 import BeautifulSoup
import pandas as pd
import math

#MONGODB VARIABLES
host_name = "localhost"
port = "27017"

atlas_cluster_name = "sandbox"
atlas_default_dbname = "local"

conn_str = {
    "local" : f"mongodb://{host_name}:{port}/",
}

client = pymongo.MongoClient(conn_str["local"])

print(f"Local Connection String: {conn_str['local']}")


#ask user for zipcode
zipcode = input("Please enter a U.S. postal code that you would like to get 7-day forecast for: ")

nomi = pgeocode.Nominatim("us")
location = nomi.query_postal_code(zipcode)
if isinstance(location['place_name'], float):
    if math.isnan(location['place_name']):
        while math.isnan(location['place_name']):
            zipcode = input("Invalid U.S. zipcode, enter a different one: ")
            location = nomi.query_postal_code(zipcode)
            if not isinstance(location['place_name'], float):
                break
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
periods = [str(pt.get_text()) for pt in period_tags]
short_descs = [str(sd.get_text()) for sd in seven_day.select(".tombstone-container .short-desc")]
temps = [str(t.get_text()) for t in seven_day.select(".tombstone-container .temp")]
descs = [str(d["title"]) for d in seven_day.select(".tombstone-container img")]

#current conditions
current_conditions = soup.find(id="current-conditions")
conditions = current_conditions.select("td")
humidity = conditions[1].get_text()
wind_speed = conditions[3].get_text()
dewpoint = conditions[7].get_text()
last_update = conditions[13].get_text()
index = 0
for char in range(len(last_update)):
    if last_update[char].isdigit():
        index = char
        break
last_update = last_update[char:]

curr = {
    "zipcode": zipcode,
    "humidity": humidity,
    "wind_speed": wind_speed,
    "dewpoint": dewpoint,
    "last_update": last_update.strip()
}
print("Current conditions: ")
print(curr)

weather = {
"zipcode": zipcode,
 "period": periods,
 "short_desc": short_descs,
 "temp": temps,
 "desc":descs
}
print("Seven day forecast:")
print(pd.DataFrame.from_dict(weather))


db = client["weather_database"]
current_conditions_db = db.current_conditions
current_conditions_db_id = current_conditions_db.insert_one(curr).inserted_id

seven_day_db = db.seven_day
seven_day_db_id = seven_day_db.insert_one(weather).inserted_id
print("Database info")
print(client.list_database_names())
print(db.list_collection_names())
print(db.current_conditions_db)
print(db.seven_day)


