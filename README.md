![Python: 3.6 | 3.7 | 3.8](https://img.shields.io/badge/python-3.6%20%7C%203.7%20%7C%203.8-blue) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
# network-ranger
*The bot for the [Networking Discord](https://discord.neteng.xyz) server*

This bot is prepared to run either as a bare Python script, Heroku dyno, or Docker image. In this guide, 
the running configurations will be knows as 'direct', 'heroku' or docker respectively.
All configuration options are therefore intended to be set via environment variables.

## Usage

### 1) Generate a secret key (You must have the `cryptography` package installed.)
```zsh
echo "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" | python3                       1 ↵
```

### 2) Configure environment variables
If you're using Kubernetes, Docker, or Heroku, create file in the base of the project named `.env` with the contents:
Replace all values as appropriate:
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
SECRETKEY=Secret key from Step 1
DB_HOST=mongodb.hostname
DB_PORT=27017
DB_NAME=network_ranger
DB_USER=<dbuser>
DB_PASS=<dbpass>
```
If you're running this directly instead of as a container, you will need to load each one of these as an environment
 variable.

### 3) Install and Run

#### A) Kubernetes

- 3.A.1. Copy the example:
  ```zsh
  cp kube-deploy.example.yaml kube-deploy.yaml
  ```
- 3.A.2. Modify `kube-deploy.yaml` to your liking. The default should work for most users.
- 3.A.3. Create the deployment:
  ```zsh
  kubectl create -f kube-deploy.yaml
  ```
- 3.A.4. Create your secret from your .env file
  ```zsh
  kubectl create secret generic network-ranger -n network-ranger --from-env-file .env
  ```
- 3.A.5. Check that the pod is running
  ```zsh
  kubectl get pods -n network-ranger
  ```

#### B) Docker

- 3.B.1. `cd` into your directory containing the `.env` file you created in Step 2
- 3.B.2. Run the Docker container either by:
  - Loading from DockerHub to pull a the remote image:
    ```zsh
    docker run --env-file=.env netdiscord/network-ranger:latest
    ```
  - Building your own local copy, assuming that the Dockerfile is in your `pwd` and running:
    ```zsh
    docker build -t network-ranger .
    docker run --env-file=.env network-ranger
    ```

#### C) Heroku

##### A) `heroku local`
- 3.C.A.1. `cd` into your directory containing the `.env` file you created in Step 2. This must also be the base
 directory of the project in which the `Dockerfile` resides.
- 3.C.A.2. Run the container with `heroku local`

##### B) Heroku Cloud
- This is outside the scope of this guide but general instructions can be found 
[on Heroku's website](https://devcenter.heroku.com/categories/deployment).
- You will need to load the environment
 variables into your Dyno as they will not be taken directly from your `.env` file by default.
- This method is no longer actively tested.

#### D) Direct
1. Install the requirements in `requirements.txt`:
   ```zsh
   pip install -r requirements.txt
   ```
2. Run the script:
   ```zsh
   python3 network_ranger
   ```
