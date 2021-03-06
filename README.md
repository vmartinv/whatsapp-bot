# Meet Vaco: A working bot for Whatsapp
Whatsapp makes adding bots really hard. Since it doesn't provide an API, and
connecting directly to Whatsapp server results in your number getting
detected quickly (thus banned), this implementation uses whatsapp web.

In order to do that we setup an emulator and send our QR image by
simulating a fake webcam. This setup is complicated but guarantees
that it doesn't get banned and also it can be fully automated.

# Features

- /search: gets results from Google (can also follow links from the first result page)
- /around: gets results around you from Google Maps, by providing your location previously.
- /url: Given a link it can get a screenshot of the page. If it's a video it will send the video.
- /tts: Text to speech in several languages
- /camera: Takes a picture using the server webcam and sends it.
- /video: Records a video using the server webcam, with customizable duration and fps.
- /play: plays audio files

# Setup
1. Setup an Android Emulator (I used android-studio to create a Google Pixel with API 28, but other versions should work fine)
2. Install Whatsapp in the emulator and register it with a number (don't use your personal number as you can eventually get banned)
3. Install the Python libraries:

        > pip install -r requirements.txt
4. Install v4l2loopback kernel module (linux required) and gst-launch-1.0.
5. Close the emulator and run `./run_emulator.sh` (you should adjust the name of the emulator)
6. Run `python2 whatsappbot.py` to finally run the bot.
7. The bot will put the QR on the fake webcam. Go to Whatsapp on the emulator and scan the QR in order to login into Whatsapp web.
8. The bot should be working. Next logins won't require scanning the QR again.
9. Some features require ffmpeg and espeak installed to work.

# Warning
This is not very much tested and many steps can get broken,
you will need to understand the code deeply in order to get it working.
I built it for my personal use and some parts of the code are really dirty.
But hey! it works :D (for me at least)
