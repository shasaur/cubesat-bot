import argparse
import sys

import backend as bot
from config import Config

# Command line arguments:
# - 0 : The command
# - 1 : The command option (week number, week number, N/A respectively)

if len(sys.argv) > 1:

    if sys.argv[1] == "sweep":
        bot.move_done_cards(Config.BOARD_ID, sys.argv[2])

    elif sys.argv[1] == "review":
        bot.review_weekly_progress(sys.argv[2])

    elif sys.argv[1] == "archive":
        bot.refresh_done_list(Config.BOARD_ID)

    else:
        print("CubeBot does not understand this command. "
              "Please choose from [sweep, review, archive].")

else:
    print("Please enter a command for the CubeBot.")