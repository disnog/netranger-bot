# network-ranger
*The bot for the [Networking Discord](https://networking-discord.github.io) server*

Note: This bot is set to run with python3

This bot is prepared to run either as a bare Python script, or as a Heroku dyno, or a Docker image. In this guide, the running configurations will be knows as 'direct', 'heroku' or docker respectively.
All configuration options are therefore intended to be set via environment variables.

Running this script is a 3 step process
1. Install the requirements in requirements .txt. This is may be done automatically by your environment
2. Set the appropriate environmental variables. This process differs based on what environment the script is running (docker, heroku
or direct)
3. Run the script



#### Installing the requirements

If you're running the script directly, use your preferred python package manager to install the requirements in `requirements.txt`. pip is a good choice. 

Heroku will automatically do this for you.
 
 Building a docker file from this source will produce a container that also automatically intalls the requirements

#### Setting the environment variables:
The environmental variables to be set are given in the next section
if you're running this in direct configuration, set it however you want to want to.

To set the environment variables when running via heroku or docker, create a file called `.env` and set the environment variables there.

Setting environmental variables in Docker : https://docs.docker.com/compose/environment-variables/#the-env-file




#### Environment variables to be set
(note the values are placeholders. You will need to set it up with real values)
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

#### Setting the environment variables
If you're running this script directly by invoking python, set the environmental variables b
docker and heroku will automatically read the file called .env and set the variables in its environment
To set the environment variables in docker or heroku (including via `heroku local`)
To run this on heroku  or docker, create  a .env file in this format
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


1. To run via docker:  create a docker image using the `Dockerfile` file provided and run the image
2. To run via heroku,  you can then run the bot via [`heroku local`](https://devcenter.heroku.com/articles/heroku-local) if you have the Heroku CLI installed or run it on the cloud .
3. For direct execution, simply run the script with `python3 network_ranger`.