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
import pytube
import os

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

    weather = data['weather'][0]['description']
    temp = data['main']['temp'] - 273.15
    humidity = data['main']['humidity']
    wind = data['wind']['speed']
    sunrise = data['sys']['sunrise']

    sunrise_time = datetime.fromtimestamp(sunrise).strftime("%H:%M")

    output = f"Weather in {city}: {weather}\nTemperature: {temp:.2f}°C\nHumidity: {humidity}%\nWind Speed: {wind}m/s\nSunrise: {sunrise_time} EST"

    await ctx.response.send_message(output)

@tree.command(name="art", description="Draw anything you imagine!")
async def draw_command(ctx, art: str):
                
    await ctx.response.send_message("Generating image, please wait...", delete_after=5)

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
    
@tree.command(name="play", description="Play a music!", guild=(discord.Object(id=Key.GUILD)))
async def play(ctx, url: str):
    await ctx.response.send_message("Playing music...", delete_after=5)
    channel = ctx.user.voice.channel if ctx.user.voice else None
    if not channel:
        await ctx.channel.send("You are not connected to a voice channel.")
        return
    video = pytube.YouTube(url)
    audio_stream = video.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(output_path='downloads')
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_file))
    voice_client = await channel.connect()
    voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.channel.send(f'Playing {video.title}')
    
@tree.command(name="stop", description="Stop the music", guild=(discord.Object(id=Key.GUILD)))
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if not voice_client:
        await ctx.channel.send("I am not currently in a voice channel.")
        return
    await voice_client.disconnect()
    await ctx.response.send_message("Music stopped.")
    for file_name in os.listdir("downloads"):
        file_path = os.path.join("downloads", file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")


@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=Key.GUILD))
    print("Ready!")

client.run(Key.TOKEN)