# CubeBot
The bot for the UoS3 CubeSat project.

Use
sweep - Move all cards that are labelled as 'Done' to the Done list, recording their completion and under what list they were completed in. 
review - Take all the cards that have been completed in the log file (representative of the last week), and send them to the target specified in the config file.
archive - Clear all cards from the Done list (for use at the start of a new week).

Contributing
Before using the bot, you must provide a Trello API key and token. These should be specified in a seperate config.py file as a Config class with members KEY, TOKEN, BOARD_ID, EMAIL + EMAIL_PASSWORD (for send requests via SMTP), and TARGET_EMAIL. You must also add a data directory for logs. To keep your details private and off the repository, please create the following .gitignore:
venv/
data/
.idea/
config.py
__pycache__/