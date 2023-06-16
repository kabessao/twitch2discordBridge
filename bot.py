import os
from twitchio.ext import commands
import json
import requests
import json
import yaml

try:
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    # If the config file doesn't exist, create a default one and quit
    config = {
        "webhook_url": '',
        "twitch_client_id": '',
        "twitch_client_secret": '',
        "twitch_username": '',
        "oauth_password": '',
        "channel": ''
    }
    
    with open("config.yaml", "w") as config_file:
        yaml.dump(config, config_file)
    
    print("Config file created. Please fill in the required information.")
    quit()




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




bot = commands.Bot(
    irc_token=config['oauth_password'],
    client_id=config['twitch_client_id'],
    nick=config['twitch_username'],
    prefix="!",
    initial_channels=[config['channel']]
)



@bot.event
async def event_ready():
    print(f"chat replay of {config['channel']}\n\n=====================================")




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


allowed_badges = ['broadcaster','moderator','vip']



@bot.event
async def event_message(message):
    print(f"{message.author.name}\n {message.author.badges}: {message.content}\n\n")

    # import pdb; pdb.set_trace()
    # if (message.author.name != channel):
    #     returno

    if not allowed_badges:
        get_profile_picture(message.author.badges)
        send_message(message.author.name, f"{message.content}", get_profile_picture(message.author.name))

    for badge in allowed_badges:
        if badge in message.author.badges:
            get_profile_picture(message.author.badges)
            send_message(message.author.name, f"{message.content}", get_profile_picture(message.author.name))



bot.run()


