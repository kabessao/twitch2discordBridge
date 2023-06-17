import os
from twitchio.ext import commands
import json
import requests
import json
import yaml
import re


# this bit loads the config file. If it isn't available it creates the file and quits
try:
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    # If the config file doesn't exist, create a default one and quit
    config_text = """
webhook_url: 'DISCORD WEBHOOK URL'
twitch_client_id: 'YOUR TWITCH ID'
twitch_client_secret: 'YOUR TWITCH SECRET'
twitch_username: 'YOUR TWITCH USERNAME'
oauth_password: 'YOUR TWITCH OAUTH PASSWORD (NOT YOUR REAL PASSWORD)'
channel: 'THE CHANNEL NAME'

# any configuration bellow is not mandatory, you can delete any of the tags if you're not gonna use it 

# filtering by badges only work if the badge is visible.
# you can check the log.txt to see what badges are being used by users
filter_badges: 
  - broadcaster
  - vip
  - moderator

# this uses the username, not the display name.
# in the log.txt it will be like this: 
# USERNAME (DISPLAY_NAME)
filter_usernames: 
   - cyberdruga

# this uses regex. Go nuts 
filter_messages:
  - 'Cheer\d+.*' # this detects any cheer people sends
"""
    
    with open("config.yaml", "w") as text_file:
        text_file.write(config_text)
    
    print("Config file created. Please fill in the required information.")
    quit()


# just a simple log method
def log(message):
    with open("log.txt", "a") as myfile:
        myfile.write(message)


# this sends a message to the configured discord webhook
def send_message(username, message, url):
    payload = {
        'content': message,
        'username': username,
        'avatar_url': url
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.post(config['webhook_url'], data=json.dumps(payload), headers=headers)


# this is responsible for getting the profile picture of of the user
def get_profile_picture(username):
    url = f"https://api.twitch.tv/helix/users?login={username}"

    payload = {}
    headers = {
    'Client-ID': config['twitch_client_id'],
    'Authorization': f'Bearer {config["oauth_password"].replace("oauth:","")}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    try: 
        return json.loads(response.text)["data"][0]["profile_image_url"]
    except:
        return ''


# this is the configuration of the twitch bot
bot = commands.Bot(
    irc_token=config['oauth_password'],
    client_id=config['twitch_client_id'],
    nick=config['twitch_username'],
    prefix="!",
    initial_channels=[config['channel']]
)


# twitch bot event for when the connection is successfull
@bot.event
async def event_ready():
    print(f"chat replay of {config['channel']}\n\n=====================================")




# twitch bot event for when a message is sent 
@bot.event
async def event_message(message):
    log_message = f"{message.author.name} ({message.author.display_name})\n {message.author.badges}: {message.content}\n\n"
    print(log_message)
    log(log_message)

    filter_badges = config['filter_badges'] if 'filter_badges' in config else []
    filter_usernames = config['filter_usernames'] if 'filter_usernames' in config else []
    filter_messages = config['filter_messages'] if 'filter_messages' in config else []

    should_send = not (filter_badges or filter_usernames or filter_messages)

    for badge in filter_badges:
        if badge in message.author.badges:
            should_send = True
            break

    for username in filter_usernames:
        if username == message.author.name:
            should_send = True
            break

    for regex in filter_messages:
        if re.compile(regex).match(message.content):
            should_send = True


    if should_send:
        send_message(message.author.display_name, f"{message.content}", get_profile_picture(message.author.name))


bot.run()
