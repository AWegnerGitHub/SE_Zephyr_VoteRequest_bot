Zephyr Vote Requests Chat Bot
=============================

Zephyr is a headless chatbot that monitors chat rooms on the [Stack Exchange](http://stackexchange.com/) network for vote requests from other users. It utilizes [ChatExchange](https://github.com/Manishearth/ChatExchange) and was inspired by [SmokeDetector](https://github.com/Charcoal-SE/SmokeDetector) and the Shadow's Den [word association bot](https://github.com/ProgramFOX/SE-Chatbot).

## Setup

You need to clone this repository first. Then, initialize the ChatExchange sub-module and install required packages.

```
git submodule init
git submodule update
pip install -r requirements.txt
```

The MySQL connector is also required. Get that from [here](http://dev.mysql.com/downloads/connector/python/)

### User Settings (optional)

If you wish to run this bot without any input on your part, you need to create a `user_settings.py` file that contains the login information this bot will utilize. Remember, there is a 20 reputation requirement to be able to post to a room. If you do not create this file, you will be prompted for login information each time the bot starts. If you are running the bot and saving data to a database, you must utilize this method and provide an `API_KEY` and `API_TOKEN`

The file should look like this. Remember to substitute the correct values or the login with fail:

```
email = "bot_login_email@email.com"
password = "botpassword"

API_KEY = "api_key_to_utilize"
ACCESS_TOKEN = "api_token_to_utilize"

API_QUESTION_FILTER = "!)b00Tmc6-NwEWPUJj(Ee*fmFv5pIBk3fwa2aR.mlGWVVa"
API_ANSWER_FILTER = "!.G(S6Mb_2mL_oRfX0bI*RkP3pY.6a"

DATABASE = "database_name"
DB_USER = "database_user"
DB_PASS = "database_passowrd"
DB_HOST = "localhost"
DB_PORT = "3306"
```

## Configuration

### Rooms to monitor and post to

The file `rooms.txt` contains a list of dictionaries. Each dictionary contains information on which room to connect to, monitor, and post requests to. Below is a description of each field in the dictionary. By default, this bot monitors these rooms:

 - Tavern on the Meta on `meta.stackexchange.com`
 - PHP on `stackoverflow.com`
 - Javascript on `stackoverflow.com`
 - Python on `stackoverflow.com`
 - HTML / CSS / Webdesign on `stackoverflow.com`
 
Each dictionary in the list has the following settings:

 - `site` - This is the site the chat room is hosted on. There are three valid values for Stack Exchange: `meta.stackexchange.com`, `stackexchange.com` and `stackoverflow.com`.
 - `room_number` - This is the room number of the chat room to join
 - `monitor` - This is a `True`/`False` value. If set to `True`, the bot will watch this room for messages that match anything in the `patterns.txt` file. If set to `False`, it will not monitor the room. Rooms that are being posted to probably should not have this value set to `True` to reduce noise in the room.
 - `post_requests` - This is a `True`/`False` value. If set to `True`, the bot will post flag requests to this room. If set to `False`, the bot will never speak in this room. 
 
### Patterns to monitor

The file `patterns.txt` contains a list of dictionaries. Each dictionary contains information about what pattern to watch for and what the pattern means if it is matched. Below is a description of each field in the dictionary. By default, this bot matches these requests:

 - Close Votes: `cv-pls`, `cv-plz`, `close-pls`, `close-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format
 - Not an answer: `flag-naa`, `naa` and if any of these appear in the `[tag:*]` format
 - Very Low Quality: `vlq` and if any of these appear in the `[tag:*]` format
 - Not an answer: `naa`, `flag-naa` and if any of these appear in the `[tag:*]` format
 - Link Only: `link-only` and if any of these appear in the `[tag:*]` format
 - Delete Votes: `dv-pls`, `dv-plz`, `delv-pls`, `delv-plz`, `delete-pls`, `delete-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format
 - Undelete Votes: `undv-pls`, `undv-plz`, `undelv-pls`, `undelv-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format
 - Reopen Votes: `ro-pls`, `ro-plz`, `rov-pls`, `rov-plz`, `reopen-pls`, `reopen-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format
 - Review Reject: Not yet functional
 - Review Request: `rv-pls`, `rv-plz`, `review-pls`, `review-plz`  and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format
 - Flag Request: `flag-pls`, `flag-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format. 
 - Spam: `spam`, reports from the [Phamhilator](https://github.com/ArcticEcho/Phamhilator/wiki) bot and [Blaze](https://github.com/Charcoal-SE/Blaze)
 - Offensive: `offensive`
 - Close/Delete Votes: `nuke-pls`, `nuke-plz` and if any of these appear in the `[tag:*-pls]`/`[tag:*-plz]` format

 
The value `should_post` is a boolean value that indicates whether a match to this pattern should trigger the bot posting the match. If set to `False`, the bot will silently save information to the database without posting a notice.

### Important Note

It is important to note that the `patterns.txt` and `rooms.txt` files are JSON objects. This means that certain characters are escaped with a backslash (`\`). This is why a portion of the regular expression looks like this `http://.*\\.com` even though only a single `\` should be required to escape the period. This pattern will translate to `http://.*\.com` when loaded into the application.

If you are not comfortable editing these files directly, the `create_config_files.py` script has been provided. Modify the `patterns` and `rooms` lists in this file, then run it via the command 

`python create_config_files.py`

This will update your `patterns.txt` and `rooms.txt` files. The bot will need to be restarted to utilize these new settings.

## Running the bot

Use this command to run the bot:

`python run_bot.py`

If you did not create the `user_settings.py` file, you will be prompted for an email address and password that the bot will utilize.

## Troubleshooting

This script monitors the Stack Exchange chat rooms by watching over HTTP. Due to the nature of the internet, server issues on Stack Exchange's side and a large number of other reasons, sometimes a connection fails. The application attempts to recover from an occasional hiccup, but if it is unable to (or an extended outage occurs), the bot does not recover automatically. The solution to these problems is to simply restart the bot.

If you are curious if your patterns will detect specific messages, the `show_patterns.py` script is included. You simply need to include the chat message you are curious about in the `test_strings` list and run the script. This is, obviously, not a full test suite but it is a nice quick way to see how the bot's posting logic will behave.
