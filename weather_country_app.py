import tkinter as tk
import requests
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
import sqlite3 as sql

connect = sql.connect("searches.db")
cursor = connect.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS searches (country TEXT, capital TEXT, population INTEGER, condition TEXT, temperature INTEGER, humidity INTEGER, wind_speed INTEGER)"
)
connect.commit()


window = tk.Tk()
window.title("Country App")
window.geometry("400x250")

label = tk.Label(window, text="Enter a Country name in the box below!")
label.pack()
entry = tk.Entry(
    width=30,
)
entry.pack()


def country_weather():

    response = requests.get("https://scrapethissite.com/pages/simple/")

    soup = BeautifulSoup(response.content, "html.parser")

    user = entry.get().title()

    found = False

    countries = soup.find_all("div", class_="col-md-4 country")
    for country in countries:
        name = country.find("h3", class_="country-name")
        name2 = name.get_text(strip=True)
        if user == name2:

            name = country.find("h3", class_="country-name")
            capital = country.find("span", class_="country-capital")
            capital_name = capital.get_text(strip=True)
            population = country.find("span", class_="country-population")
            found = True

    if not found:
        label.config(text="country not found!")
    if found:
        city_wttr = f"https://wttr.in/{capital_name}?format=j1"

        try:
            req_get = requests.get(city_wttr)
            weather_data = req_get.json()
            area_name = weather_data["nearest_area"][0]["areaName"][0]["value"]
            ratio = SequenceMatcher(None, capital_name, area_name).ratio()

            if ratio < 0.5:
                label.config(text="city not found!")
            else:

                current_wttr = weather_data["current_condition"]
                current = current_wttr[0]
                label.config(text=f"""
                {name.get_text(strip=True)} | capital: {capital.get_text(strip=True)} | population: {population.get_text(strip=True)}
                                             
                Weather in {capital_name}
                condition: {current['weatherDesc'][0]['value']}
                Temperature: {current['temp_C']} feels like : {current['FeelsLikeC']}
                humidity: {current['humidity']}%
                wind speed: {current['windspeedKmph']}
                
                        """)

                cursor.execute(
                    "INSERT INTO searches (country, capital , population, condition, temperature, humidity, wind_speed) VALUES(?, ?, ?, ?, ?, ?, ?)",
                    (
                        user,
                        capital_name,
                        population.get_text(strip=True),
                        current["weatherDesc"][0]["value"],
                        current["temp_C"],
                        current["humidity"],
                        current["windspeedKmph"],
                    ),
                )
                connect.commit()

        except requests.exceptions.RequestException as e:
            label.config(text="something went wrong!")


def show_history():
    cursor.execute("SELECT * FROM searches ORDER BY rowid DESC LIMIT 5")
    rows = cursor.fetchall()
    history = "Last 5 searches:\n"
    for row in rows:
        history += f"{row[0]} | {row[1]} | {row[3]} | {row[4]}°C\n"

    label.config(text=history)

button = tk.Button(
    window, text="click me to see weather & info", command=country_weather
)
button.pack()

button1 = tk.Button(
    window, text="click me to see history!", command=show_history
)
button1.pack()

window.mainloop()
