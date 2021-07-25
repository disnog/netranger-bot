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
        welcomemessage_default = "Hi {mention}, welcome to {server}. Please **complete joining the server by accepting the rules at <https://disnog.org/join>**"
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
            "db_host": Config.VarDef(value=None, environ="DB_HOST"),
            "db_port": Config.VarDef(value=27017, environ="DB_PORT"),
            "db_user": Config.VarDef(value=None, environ="DB_USER"),
            "db_pass": Config.VarDef(value=None, environ="DB_PASS"),
            "db_name": Config.VarDef(value=None, environ="DB_NAME"),
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
