import discord
import requests
from datetime import datetime
import Key

intents = discord.Intents.all()
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('Logged in as {0.user}'.format(client))
    

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('weather'):
        # get city name from user input
        city = message.content.split()[1]

        # API request
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={Key.API_KEY}"
        response = requests.get(url)
        data = response.json()

        # extract weather data
        weather = data['weather'][0]['description']
        temp = data['main']['temp'] - 273.15
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        sunrise = data['sys']['sunrise']

        # format sunrise time
        sunrise_time = datetime.fromtimestamp(sunrise).strftime("%H:%M")

        # create output message
        output = f"Weather in {city}: {weather}\nTemperature: {temp:.2f}°C\nHumidity: {humidity}%\nWind Speed: {wind}m/s\nSunrise: {sunrise_time} EST"

        # send message to discord
        await message.channel.send(output)


client.run(Key.TOKEN)