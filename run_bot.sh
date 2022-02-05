 cd ~/whatsapp-bot
 source venv/bin/activate
 xdotool mousemove 0 0 click 1 sleep 1 key --clearmodifiers super+5
 ./run_emulator.sh
 xdotool mousemove 0 0 click 1 sleep 1 key --clearmodifiers super+4
 python whatsappbot.py
 xdotool key F1 mousemove 400 400
