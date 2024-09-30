import os
from dotenv import load_dotenv

load_dotenv()


class ConfigMaker():
    class Oddsportal:
        LOGIN = os.getenv('ODDSPORTAL_LOGIN')
        PASSW = os.getenv('ODDSPORTAL_PASSW')

    class Bot:
        TOKEN = os.getenv('BOT_TOKEN')
        ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')
        USER_TOKEN = os.getenv('USER_TOKEN')

Config = ConfigMaker()