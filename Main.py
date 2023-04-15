import discord
from discord import Attachment, app_commands
import requests
import Key
import requests
import pytube
import os
from revChatGPT.V1 import Chatbot as RevChatbot
from ImageGen import ImageGen
from EdgeGPT import Chatbot, ConversationStyle
import requests
from datetime import datetime, timedelta
from pytz import UnknownTimeZoneError, timezone

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

url = "http://127.0.0.1:7860"

bot = Chatbot(cookiePath='./cookies.json')

chatbot = RevChatbot(config={
  "access_token": Key.ACCESS_TOKEN,
})

ig = ImageGen(auth_cookie= Key.AUTH_COOKIE)

@tree.command(name="weather", description="Get weather of any city!")
async def weather_command(ctx, city: str):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={Key.API_KEY}"
    response = requests.get(url)
    data = response.json()

    weather = data['weather'][0]['description']
    temp_c = data['main']['temp']
    temp_f = (temp_c * 9/5) + 32
    feels_like_c = data['main']['feels_like']
    feels_like_f = (feels_like_c * 9/5) + 32
    temp_min_c = data['main']['temp_min']
    temp_min_f = (temp_min_c * 9/5) + 32
    temp_max_c = data['main']['temp_max']
    temp_max_f = (temp_max_c * 9/5) + 32
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    wind_deg = data['wind']['deg']
    clouds = data['clouds']['all']
    pressure = data['main']['pressure']
    visibility_m = data['visibility'] / 1609.34
    visibility_km = data['visibility'] / 1000 
    timezone_name = 'US/Eastern'
    sunrise = data['sys']['sunrise']
    sunrise_datetime = datetime.fromtimestamp(sunrise, tz=timezone('UTC'))
    sunrise_time = sunrise_datetime.astimezone(timezone(timezone_name)).strftime("%I:%M %p")
    sunset = data['sys']['sunset']
    sunset_datetime = datetime.fromtimestamp(sunset, tz=timezone('UTC'))
    sunset_time = sunset_datetime.astimezone(timezone(timezone_name)).strftime("%I:%M %p")

    if wind_deg > 337.5 or wind_deg <= 22.5:
        wind_dir = "N"
    elif wind_deg > 22.5 and wind_deg <= 67.5:
        wind_dir = "NE"
    elif wind_deg > 67.5 and wind_deg <= 112.5:
        wind_dir = "E"
    elif wind_deg > 112.5 and wind_deg <= 157.5:
        wind_dir = "SE"
    elif wind_deg > 157.5 and wind_deg <= 202.5:
        wind_dir = "S"
    elif wind_deg > 202.5 and wind_deg <= 247.5:
        wind_dir = "SW"
    elif wind_deg > 247.5 and wind_deg <= 292.5:
        wind_dir = "W"
    else:
        wind_dir = "NW"

    output = f"Weather in {city}: {weather}\nTemperature: {temp_c:.2f}°C / {temp_f:.2f}°F\nFeels like: {feels_like_c:.2f}°C / {feels_like_f:.2f}°F\nMin Temperature: {temp_min_c:.2f}°C / {temp_min_f:.2f}°F\nMax Temperature: {temp_max_c:.2f}°C / {temp_max_f:.2f}°F\nHumidity: {humidity}%\nWind Speed: {wind_speed}m/s\nWind Direction: {wind_dir} ({wind_deg}°)\nClouds: {clouds}%\nPressure:{pressure}hPa\nVisibility: {visibility_km:.2f}km / {visibility_m:.2f}mi\nSunrise: {sunrise_time} EST\nSunset: {sunset_time} EST"

    await ctx.response.send_message(output)

    
@tree.command(name="play", description="Play a music!")
async def play(ctx, url: str):
    channel = ctx.user.voice.channel if ctx.user.voice else None
    if not channel:
        await ctx.response.send_message("You are not connected to a voice channel.")
        return
    try:
        video = pytube.YouTube(url)
    except pytube.exceptions.RegexMatchError:
        await ctx.response.send_message("Invalid YouTube URL.")
        return
    await ctx.response.send_message("Playing music...", delete_after=2)
    audio_stream = video.streams.filter(only_audio=True).first()
    audio_file = audio_stream.download(output_path='downloads')
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(audio_file))
    voice_client = await channel.connect()
    voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)
    await ctx.channel.send(f'Playing {video.title} ' + url)
    

@tree.command(name="draw", description="Draw anything you imagine!")
async def draw_command(ctx, art: str):
    for file_name in os.listdir("output_images"):
        file_path = os.path.join("output_images", file_name)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")
    messageSend = "**" + str(ctx.user) + "**: " + str(art)
    await ctx.response.send_message(messageSend + "\n Generating image...... Please wait.")

    try:
        image_links = ig.get_images(prompt=art)

        output_dir = 'output_images/'
        ig.save_images(links=image_links, output_dir=output_dir)

        files = []
        
        for file_name in os.listdir(output_dir):
            if file_name.endswith(".jpeg"):
                file_path = os.path.join(output_dir, file_name)
                file = discord.File(file_path)
                files.append(file)
        
        await ctx.edit_original_response(content=messageSend)
        await ctx.edit_original_response(attachments=files)
    except:
        message = "Your prompt either had bad words or timed out. Please try again."
        await ctx.edit_original_response(content=message)

@tree.command(name="internetchat", description="Chat with internet")
async def chat(ctx, message: str):
        user_prompt = "**" + str(ctx.user) + "**: " + str(message) 
        await ctx.response.send_message(user_prompt + "\n Fecthing...")
        prompt = message
        response = (await bot.ask(prompt=prompt))["item"]["messages"][1]["adaptiveCards"][0]["body"][0]["text"]
        await ctx.edit_original_response(content=user_prompt + '\n' + response)
            
@tree.command(name="stop", description="Stop the music")
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
            
@tree.command(name="chat", description="Chat with a bot")
async def chat(ctx, message: str):
    prompt = message
    response = ""

    user_prompt = "**" + str(ctx.user) + "**: " + str(prompt) 
    await ctx.response.send_message(user_prompt + "\n Responding...")
    for data in chatbot.ask(prompt):
        response = data["message"]

    await ctx.edit_original_response(content=user_prompt + '\n' + response)

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

client.run(Key.TOKEN)   