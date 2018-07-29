python main.py sweep $(( $(date -d 'now - 3 days - 9 hours - 15 minutes' +%V) - 29))

at -f /home/user/CubeSat/cubesat-bot/daily-repeater.sh 9:00 am 
