from datetime import datetime
import discord
from discord import app_commands
import requests
import Key
import json
import requests
import io
import base64
from PIL import Image, PngImagePlugin

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

url = "http://127.0.0.1:7860"

@tree.command(name="weather", description="Get weather of any city!")
async def weather_command(ctx, city: str):

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

    await ctx.response.send_message(output)

@tree.command(name="draw", description="Draw anything you imagine!")
async def draw_command(ctx, art: str):
                
    await ctx.response.send_message("Generating image, please wait...")

    payload = {
        "prompt": art,
        "steps": 25,
        "negative_prompt": Key.NEGATIVE_PROMPT
    }
    response = requests.post(url=f'{url}/sdapi/v1/txt2img', json=payload)


    r = response.json()

    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",",1)[0])))

        png_payload = {
        "image": "data:image/png;base64," + i
        }
        response2 = requests.post(url=f'{url}/sdapi/v1/png-info', json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save('output.png', pnginfo=pnginfo)
    
    with open('output.png', 'rb') as f:
        file = discord.File(f, filename='output.png')    
    
    await ctx.channel.send(file=file)    

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=Key.GUILD))
    print("Ready!")

client.run(Key.TOKEN)