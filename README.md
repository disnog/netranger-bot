![Python: 3.6 | 3.7 | 3.8](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
# network-ranger
*The bot for the [Networking Discord](https://networking-discord.github.io) server*

This bot is prepared to run either as a bare Python script, Heroku dyno, or Docker image. In this guide, 
the running configurations will be knows as 'direct', 'heroku' or docker respectively.
All configuration options are therefore intended to be set via environment variables.

Running this script is a 3 step process
1. Install the requirements in `requirements.txt`. This may be done automatically by your environment.
2. Set the appropriate environmental variables. This process differs based on what environment the script is running
 (docker, heroku or direct)
3. Run the script

#### Installing the requirements

If you're running the script directly, use your preferred python package manager to install the requirements in
 `requirements.txt`. pip is a good choice. 

Heroku will automatically do this for you.
 
Building a docker file from this source will produce a container that also automatically installs the requirements.

#### Setting the environment variables:
The environmental variables to be set are given in the next section.

If you're running this in direct configuration, set the environment variables in your execution environment.

To set the environment variables when running via heroku or docker, create a file called `.env` and set the
 environment variables there.

Setting environmental variables in Docker : https://docs.docker.com/compose/environment-variables/#the-env-file

#### Environment variables to be set
Replace values as appropriate:
```
BOT_DESCRIPTION='[testing] The Networking Discord Bot'
COMMAND_PREFIX=^
EGGSROLE_NAME='!eggs'
GUILD_NAME=Networking-Dev
LOGCHANNEL_NAME=cnc
MEMBERCHANNEL_NAME=general
MEMBERROLE_NAME=Members
TOKEN=<YourBotsPrivateToken>
WELCOMECHANNEL_NAME=welcome
MIRRORCHANNEL_NAME=egg-qc
SMTP_USERNAME=mysmtpusername
SMTP_PASSWORD=mysmtppassword
SMTP_SERVER=in-v3.mailjet.com
SMTP_PORT=587
SMTP_FROMEMAIL=bot@domain.com
SECRETKEY=<Generate this with Fernet.generatekey()>
```

1. To run via docker, create a docker image using the `Dockerfile` file provided and run the image
2. To run via heroku, you can then run the bot via [`heroku local`](https://devcenter.heroku.com/articles/heroku-local)
 if you have the Heroku CLI installed or run it in the Heroku cloud.
3. For direct execution, simply run the script with `python3 network_ranger`.