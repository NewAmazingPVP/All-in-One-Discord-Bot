from datetime import datetime
import discord
from discord import app_commands
import requests
import Key

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="weather", description="My first application Command", guild=discord.Object(id=Key.GUILD))
async def first_command(ctx, city: str):

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

    await ctx.channel.send(output)

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=Key.GUILD))
    print("Ready!")

client.run(Key.TOKEN)
