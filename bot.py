import os
from twitchio.ext import commands
import json
import requests
import json
import yaml
import regex as re

# this bit loads the config file. If not present it prompts the user to create one
try:
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    print("Please fill in the required information in a 'config.yaml' file.")
    quit()


# log method, that keeps the log file in a fixed size
def log(message, max_size=30 * 1024, num_lines_to_keep=50000):
    with open("log.txt", "a") as myfile:
        myfile.write(message)
    
    # Check the file size
    file_size = os.path.getsize("log.txt")
    
    # If the file size exceeds the maximum allowed size
    if file_size > max_size:
        with open("log.txt", "r") as file:
            # Read all the lines from the log file
            lines = file.readlines()
        
        # Remove the oldest entries by keeping the most recent ones
        lines = lines[-num_lines_to_keep:]
        
        # Rewrite the log file with the most recent entries
        with open("log.txt", "w") as file:
            file.writelines(lines)


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
        'Authorization': f'Bearer {config["oauth_password"]}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    try: 
        return json.loads(response.text)["data"][0]["profile_image_url"]
    except:
        return ''


# this is the configuration of the twitch bot
bot = commands.Bot(
    irc_token=f"oauth:{config['oauth_password']}",
    client_id=config['twitch_client_id'],
    nick=config['twitch_username'],
    prefix="!",
    initial_channels=[config['channel']]
)


# this only translate emotes that twitch says the user can use
def parse_emotes(message, emotes):
    
    msg = message.content

    if not message.tags['emotes']: return msg

    # this is an example:
    # message.content = 'henyatDance henyatKettle henyatDance'
    positional_emotes = message.tags['emotes']
    # 'emotesv2_2982b2a2007d4f17844d974f079a8866:0-10,25-35/emotesv2_73c1c0df74cb43ae883d0869bc710f44:12-23'
    positional_emotes = positional_emotes.split('/')
    # ['emotesv2_2982b2a2007d4f17844d974f079a8866:0-10,25-35','emotesv2_73c1c0df74cb43ae883d0869bc710f44:12-23']
    positional_emotes = [ item.split(':')[1] for item in positional_emotes]
    # ['0-10,25-35','12-23']
    positional_emotes = [ item.split(',')[0] for item in positional_emotes]
    # ['0-10','12-23']
    positional_emotes = [ item.split('-') for item in positional_emotes]
    # [['0','10'],['12','23']]
    positional_emotes = [ [int(i) for i in item] for item in positional_emotes]
    # [[0,10],[12,23]]
    positional_emotes = [ message.content[item[0]:item[1]+1] for item in positional_emotes]
    # ['henyatDance','henyatKettle']

    for emote in positional_emotes:
        if emote in emotes:
            msg = re.sub(r"(?<=^|\W)"+emote+r"(?=\W|$)",emotes[emote], msg)

    return msg


filter_badges = config['filter_badges'] if 'filter_badges' in config and config['filter_badges'] else []
filter_usernames = config['filter_usernames'] if 'filter_usernames' in config and config['filter_usernames'] else []
filter_messages = config['filter_messages'] if 'filter_messages' in config and config['filter_messages'] else []
emotes = config['emote_translator'] if 'emote_translator' in config and config['emote_translator'] else []
show_bit_gifters = 'show_bit_gifters' in config and config['show_bit_gifters']


# twitch bot event for when the connection is successfull
@bot.event
async def event_ready():
    print(f"connected successfully to {config['channel']}")


# twitch bot event for when a message is sent 
@bot.event
async def event_message(message):
    log_message = f"{message.author.name} ({message.author.display_name})\n{message.tags}\n{message.content}\n\n"
    log(log_message)

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

    if show_bit_gifters and 'bits' in message.tags:
        should_send = True


    if should_send:
        msg = message.content if not emotes else parse_emotes(message, emotes)
        
        send_message(message.author.display_name, msg, get_profile_picture(message.author.name))


bot.run()
