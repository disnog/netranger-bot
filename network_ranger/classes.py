import os


class Config:
    """Store configuration variables"""

    class VarDef:
        def __init__(self, value="", environ=None, sensitive=False):
            """A definition of variable to be stored in the Environment. May later need to specify required or type.

                Args:
                     value: Value
                     environ (str): Name of environment variable from which to read.
                     sensitive (bool): Hide values in output (Default: False)
                """
            self.value = value
            self.environ = environ
            self.sensitive = bool(sensitive)

    def get(self, key, raise_on_keyerror=False):
        """Return the value from the specified self.config VarDef. Returns None if unset.

            Args:
                key (str): Key to return.
                raise_on_keyerror (bool):   Raise if the key is not found. (Default: False)
            """
        try:
            value = self.config[key].value
            return value
        except KeyError:
            if raise_on_keyerror:
                raise
            return None

    def __init__(self):
        self.config = dict()

        # TODO: Un-hardcode this
        welcomemessage_default = """Hi {mention}, welcome to {server}. Please _read_ and accept the rules to fully join.

We'd ask that you observe the following guidelines for this server:

__**This is a place for:**__
:white_check_mark:  networking professionals to gather and share thoughts and knowledge.
:white_check_mark:  those who want to enter the networking profession to gain exposure.
:white_check_mark:  perhaps griping about the latest Cisco bug or mismanagement priority.
:white_check_mark:  students and others looking to enter the profession to gain exposure and exchange knowledge.

__**This is not a place intended for:**__
:no_entry: server administration
:no_entry: home networking
:no_entry: [non-network] programming
:no_entry: non-networking IT disciplines

__**General rules:**__
- No cheating, whatsoever.  Asking for or distributing braindumps will result in an immediate ban.
- Keep this place 100% safe for work.
- Please attempt to use the appropriate channel for your discussion.
- Treat everyone with respect.
- No random/unprompted DMs. (Excepting DMs to mods/admins regarding the Discord server)

__**To gain access to the rest of the server**__
- Once you accept, you will lose access to #welcome.  The guidelines are available via a pinned post in #general.
- If you agree to the guidelines above, answer the following question by typing `{command_prefix}accept <ANSWER>` in this channel. e.g. if the answer is "eggs", type `{command_prefix}accept eggs`.
```
Acme Inc has developed an application which has to send data which absolutely cannot be lost by the receiver even when the data is sent over the Internet. Which common transport layer protocol should the application use? (Your answer should be the well-known initials for the protocol.)
```
"""
        self.config = {
            "welcomemessage": Config.VarDef(
                # Only consider this sensitive because it would create some very long log output.
                value=welcomemessage_default,
                sensitive=True,
            ),
            "token": Config.VarDef(value=None, environ="TOKEN", sensitive=True),
            "guild_name": Config.VarDef(value="Networking-Dev", environ="GUILD_NAME"),
            "welcomechannel_name": Config.VarDef(
                value="test-welcome", environ="WELCOMECHANNEL_NAME"
            ),
            "eggsrole_name": Config.VarDef(value="!eggs", environ="EGGSROLE_NAME"),
            "memberrole_name": Config.VarDef(
                value="Members", environ="MEMBERROLE_NAME"
            ),
            "memberchannel_name": Config.VarDef(
                value="test-general", environ="MEMBERCHANNEL_NAME"
            ),
            "logchannel_name": Config.VarDef(
                value="test-cnc", environ="LOGCHANNEL_NAME"
            ),
            "mirrorchannel_name": Config.VarDef(
                value="mirror", environ="MIRRORCHANNEL_NAME"
            ),
            "bot_description": Config.VarDef(
                value="Network Ranger", environ="BOT_DESCRIPTION"
            ),
            "command_prefix": Config.VarDef(value="$", environ="COMMAND_PREFIX"),
            "smtp_username": Config.VarDef(value=None, environ="SMTP_USERNAME"),
            "smtp_password": Config.VarDef(value=None, environ="SMTP_PASSWORD"),
            "smtp_server": Config.VarDef(value=None, environ="SMTP_SERVER"),
            "smtp_port": Config.VarDef(value=None, environ="SMTP_PORT"),
            "smtp_fromemail": Config.VarDef(value=None, environ="SMTP_FROMEMAIL"),
            "secretkey": Config.VarDef(value=None, environ="SECRETKEY"),
        }

        # TODO: Document environment variables

        # Loop through defined variables and overwrite with information from environment variables.
        for var in self.config:
            if self.config[var].environ:
                try:
                    self.config[var].value = os.environ[self.config[var].environ]
                except KeyError as e:
                    print(
                        f"Warning: Environment variable {e.args[0]} is not defined. Defaulting to "
                        f"{self.config[var].value}."
                    )
