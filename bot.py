import requests
import yaml
import regex as re
import sys
from twitchio.ext import commands
from multiprocessing import Process, Manager
from time import sleep


from utils import *

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
def load_emotes_url(config): 
    while True:
        try: 
            response = requests.get(config['emote_translator_url'])

            if 200 <= response.status_code <= 299:
                tmp = yaml.safe_load(response.text)
                config['emote_translator'] = tmp['emote_translator']

        except:
            print("failed to load emote_translator from the web", file=sys.stderr)
        sleep(10)


if 'emote_translator_url' in config:
    Process(target=load_emotes_url, args=(config,)).start()

def log(message):
    logger(message,config=config)

def send_message(username, message, url):
    send_webhook_message(username, message, url, config)


# this is responsible for getting the profile picture of of the user
def get_profile_picture(username):
    return get_twitch_profile_picture(username, config)


# this is the configuration of the twitch bot
bot = commands.Bot(
    irc_token=f"oauth:{config['oauth_password']}",
    client_id=config['twitch_client_id'],
    nick=config['twitch_username'],
    prefix="=",
    initial_channels=[config['channel']]
)


filter_badges = config['filter_badges'] if 'filter_badges' in config and config['filter_badges'] else []
filter_usernames = config['filter_usernames'] if 'filter_usernames' in config and config['filter_usernames'] else []
filter_messages = config['filter_messages'] if 'filter_messages' in config and config['filter_messages'] else []
show_bit_gifters = config['show_bit_gifters'] if 'show_bit_gifters' in config else False
show_hyber_chat = config['show_hyber_chat'] if 'show_hyber_chat' in config else False
prevent_ping = config['prevent_ping'] if 'prevent_ping' in config else True
blacklist = config['blacklist'] if 'blacklist' in config and config['blacklist'] else []


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

    msg = str(message.content)
    display_name = str(message.author.display_name)
    name = str(message.author.name)

    if blacklist and name in blacklist: return

    if re.match(r'[^\x20-\x7F]',display_name):
        display_name = f'{name} ({display_name})'

    message_history.append(message)

    emotes = config['emote_translator'] if 'emote_translator' in config and config['emote_translator'] else []

    if len(message_history) > 800:
        message_history.pop(0)

    should_send = 'send_all_messages' in config and config['send_all_messages']

    for badge in filter_badges:
        if badge in message.author.badges:
            should_send = True
            break

    for username in filter_usernames:
        if username == name:
            should_send = True
            break

    for regex in filter_messages:
        if re.compile(regex).match(msg):
            should_send = True

    if show_bit_gifters and 'bits' in message.tags:
        msg = re.sub(r"(?<=^|\W)[Cc]heer\d+(\W|$)",'', msg).strip()
        bits = message.tags['bits']

        display_name = f"{display_name} gave {bits} bit{'s' if bits > 1 else ''}"
 
        should_send = True

        if not msg:
            msg = "`empty message`"
        if show_bit_gifters is int:
            should_send = message.tags['bits'] >= show_bit_gifters

    if show_hyber_chat and 'pinned-chat-paid-amount' in message.tags:
        bits = message.tags['pinned-chat-paid-amount']
        display_name = f"{display_name} sent a Hype Chat for {bits} bits"
        should_send = True

    if should_send:
        msg = msg if not emotes else parse_emotes(msg, message.tags, emotes)

        if prevent_ping:
            msg = re.sub(r"@(?=here|everyone)", '', msg)

        send_message(display_name, msg, get_profile_picture(message.author.name))
    
    
if 'mod_actions' in config and config['mod_actions']:
    @bot.event
    async def event_clearchat(data):
        global config
        log(f"{data.tags=}")

        if 'ban-duration' not in data.tags:
            return

        emotes = config['emote_translator'] if 'emote_translator' in config and config['emote_translator'] else []

        id =data.tags['target-user-id']
        messages = message_history.copy()

        messages = [ item for item in messages if item.tags['user-id'] == id ]

        if not messages:
            return

        name = messages[0].author.name
        display_name = messages[0].author.display_name

        send_message(display_name, f"`user got timed out for {data.tags['ban-duration']} seconds`", get_profile_picture(name))

        for message in messages:
            msg = message.content if not emotes else parse_emotes(message.content, message.tags, emotes)
            
            send_message(message.author.display_name, msg, get_profile_picture(message.author.name))


bot.run()
