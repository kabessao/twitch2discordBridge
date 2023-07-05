import os
import json
import requests
import regex as re
import sys
from time import sleep

# this only translate emotes that twitch says the user can use
def parse_emotes(message: str, tags: dict, emotes: dict):
    
    if not tags['emotes']: return message

    # this is an example:
    # message.content = 'henyatDance henyatKettle henyatDance'
    positional_emotes = tags['emotes']
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
    positional_emotes = [ message[item[0]:item[1]+1] for item in positional_emotes]
    # ['henyatDance','henyatKettle']

    for emote in positional_emotes:
        if emote in emotes:
            message = re.sub(r"(?<=^|\W)"+emote+r"(?=\W|$)",emotes[emote], message)

    return message


# log method, that keeps the log file in a fixed size
def logger(message, max_size=30 * 1024, num_lines_to_keep=1000, config=dict()):


    print(message)

    if 'log_file' in config and not config['log_file']:
        return

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
def send_webhook_message(username, message, url, config):
    payload = {
        'content': message,
        'username': username,
        'avatar_url': url
    }

    headers = {
        'Content-Type': 'application/json'
    }

    requests.post(config['webhook_url'], data=json.dumps(payload), headers=headers)


# this is responsible for getting the profile picture of of the user
def get_twitch_profile_picture(username, config):
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
