# twitch2discordBridge
replicates twitch chat into a discord chat through webhooks

you will need to create a twitch bot to use it.

if you leave the `OAuth Redirect url's` empty on the bot creator you'll need to use your own credentials. It's weird, I know.

Just go to https://twitchapps.com/tmi/ , right click the `connect` button, and copy the url
it'll be something like this

```https://id.twitch.tv/oauth2/authorize?response_type=token&client_id=<copyThisCode>&redirect_uri=...```

Copy the code mentioned. It's your `client_id`.

Now click on the `connect` button and copy the code given. The whole code.

Go back to your bot and copy the `client secret`. If it's not being displayed you can generate a new one. 

And finally, go to your channel, and copy your username, not the Display name.
