# Oddsportal-parser-bot

This project consists of two parts:
* A minute-by-minute parser for oddsportal.com, written using Selenium
* A bot for configuring the parsing settings and receiving notifications about new predictions from selected players


## Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Technologies](#technologies)

## Installation

To clone the repository and install dependencies, run the following commands:

```bash
git clone https://github.com/Vanilara/Oddsportal-parser-bot.git
cd Oddsportal-parser-bot
pip install -r requirements.txt
python3 database/remake_database.py
```

run `python3 bot.py` and `python3 parse.py` as daemons


## Usage
Send the selected `ADMIN_TOKEN` to the bot with a command. After that, you will gain access to adding players and setting filters. To receive signals without access to the admin panel, use the `USER_TOKEN`.

## Configuration

Before running the project, you need to set up the `.env` file. Example configuration file:

# .env
```
ODDSPORTAL_LOGIN = oddsportal.com login
ODDSPORTAL_PASSW = oddsportal.com password
BOT_TOKEN = Aiogram bot token
ADMIN_TOKEN = Token for admin panel
USER_TOKEN = Token for only receiving updates
```

## Technologies
* Python 3.10
* Aiogram 3.x
* Selenium