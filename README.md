# twitch2discordBridge

## ATTENTION
This project is not in development anymore, and was entirely re-written in Golang.

I found a lot of limitations in Python that made things too complex for me to move this forward. You could say it was "skill issues" but honestly I was not enjoying making everything in Python, so I jumped to Golang and never looked back. 

You can check the Golang version in [here](https://github.com/kabessao/Twitch2DiscordBridge-Go/)

## Description

replicates twitch chat into a discord chat through webhooks

for the twitch bit you can go to https://chatterino.com/client_login, copy your credentials, and set them up on the config file


you can just execute `python bot.py` to execute, but you can go the Docker/Podman route.


If you decide to go the podman route, install podman and podman-compose, and if you decide to use docker and docker-compose just replace `podman-compose` to `docker-compose` in `Makefile`.


If you want to launch only one instance just create a `config.yaml` and just execute `make`, This will create an image called `twitch2discord-bridge:default` and a container called `t2d_bot`.

If you want to launch multiple intances of the bot (each for a different webhook for example) create one or more config files with any name you choose like `<name>.yaml` (Ex.: `henya.yaml`) and execute `make`. This will create images with the name you choose (Ex.: `twitch2discord-bot:henya`) and also a container (Ex.: `t2d_henya`), and if you have multiple config files it will do the same for each.

If you want to build just for one of them just do `make <name>` (Ex.: `make henya`) and only that image/container will be updated.
