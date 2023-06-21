# twitch2discordBridge
replicates twitch chat into a discord chat through webhooks

for the twitch bit you can go to https://chatterino.com/client_login, copy your credentials, and set them up on the config file


you can just execute `python bot.py` to execute, but you can go the Docker/Podman route.


If you decide to go the podman route, install podman and podman-compose, and if you decide to use docker and docker-compose just replace `podman-compose` to `docker-compose` in `Makefile`.


If you want to launch only one instance just create a `config.yaml` and just execute `make`, This will create an image called `twitch2discord-bridge:default` and a container called `t2d_bot`.

If you want to launch multiple intances of the bot (each for a different webhook for example) create one or more config files with any name you choose like `<name>.yaml` (Ex.: `henya.yaml`) and execute `make`. This will create images with the name you choose (Ex.: `twitch2discord-bot:henya`) and also a container (Ex.: `t2d_henya`), and if you have multiple config files it will do the same for each.

If you want to build just for one of them just do `make <name>` (Ex.: `make henya`) and only that image/container will be updated.
