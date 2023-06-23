import os
import json
import requests
import json
import yaml
import regex as re
import sys
from twitchio.ext import commands
from multiprocessing import Process, Manager
from time import sleep

# this bit loads the config file. If not present it prompts the user to create one
config = None
try:
    with open("config.yaml", "r") as config_file:
        config = yaml.safe_load(config_file)
except FileNotFoundError:
    print("Please fill in the required information in a 'config.yaml' file.", file=sys.stderr)
    quit()


manager = Manager()
config = manager.dict(config)


# this bit loads the emotes file from the web
emote_config = None
def load_emotes_url(config): 
    while True:
        try: 
            response = requests.get(config['emote_translator_url'])

            if 200 <= response.status_code <= 299:
                tmp = yaml.safe_load(response.text)
                config['emote_translator'] = tmp['emote_translator']

        except:
            print("failed to load emote_translator from the web")
        sleep(10)


if 'emote_translator_url' in config:
    Process(target=load_emotes_url, args=(config,)).start()

# log method, that keeps the log file in a fixed size
def log(message, max_size=30 * 1024, num_lines_to_keep=1000):

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
    prefix="=",
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


def parse_bits(message):
    bits = re.findall(r"(?<=^|\W)[Cc]heer(\d+)(?=\W|$)", message)
    bits = [ int(item) for item in bits ]
    bits = sum(bits)

    return re.sub(r"(?<=^|\W)[Cc]heer\d+(\W|$)",'', message).strip(), bits

emotes = config['emote_translator'] if 'emote_translator' in config and config['emote_translator'] else []
filter_badges = config['filter_badges'] if 'filter_badges' in config and config['filter_badges'] else []
filter_usernames = config['filter_usernames'] if 'filter_usernames' in config and config['filter_usernames'] else []
filter_messages = config['filter_messages'] if 'filter_messages' in config and config['filter_messages'] else []
show_bit_gifters = config['show_bit_gifters'] if 'show_bit_gifters' in config else False
show_hyber_chat = config['show_hyber_chat'] if 'show_hyber_chat' in config else False


message_history = [] 


# twitch bot event for when the connection is successfull
@bot.event
async def event_ready():
    log(f"connected successfully to {config['channel']}")


# twitch bot event for when a message is sent 
@bot.event
async def event_message(message):
    global config
    log_message = f"{message.author.name} ({message.author.display_name})\n{message.tags}\n{message.content}\n\n"
    log(log_message)

    msg = message.content
    name = message.author.display_name

    message_history.append(message)

    if len(message_history) > 800:
        message_history.pop(0)

    should_send = 'send_all_messages' in config and config['send_all_messages']

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
        msg, bits = parse_bits(message)

        name = f"{name} gave {bits} bit{'s' if bits > 1 else ''}"
 
        should_send = True
        if show_bit_gifters is int:
            should_send = message.tags['bits'] >= show_bit_gifters

    if show_hyber_chat and 'pinned-chat-paid-amount' in message.tags:
        bits = message.tags['pinned-chat-paid-amount']
        name = f"{name} sent a Hype Chat for {bits} bits"
        should_send = True

    if should_send:
        msg = msg if not emotes else parse_emotes(message, emotes)

        if re.match(r'[^\x20-\x7F]',name):
            name = f'{message.author.name} ({name})'

        send_message(name, msg, get_profile_picture(message.author.name))
    
    
if 'mod_actions' in config and config['mod_actions']:
    @bot.event
    async def event_clearchat(data):
        if 'ban-duration' not in data.tags:
            return

        id =data.tags['target-user-id']
        messages = message_history.copy()

        messages = [ item for item in messages if item.tags['user-id'] == id ]

        if not messages:
            return

        name = messages[0].author.name
        display_name = messages[0].author.display_name

        send_message(display_name, f"`user got timed out for {data.tags['ban-duration']} seconds`", get_profile_picture(name))

        log(f"{data.tags=}")
            
        for message in messages:
            msg = message.content if not emotes else parse_emotes(message, emotes)
            
            send_message(message.author.display_name, msg, get_profile_picture(message.author.name))


bot.run()