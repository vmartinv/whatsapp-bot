# -*- coding: utf-8 -*-
from message import Message
from basic_view import View
from cv2 import *
import logging
import time
import subprocess
import re

class PersonalView(View):
    def routes(self):
        return [
          ("^/jenny$", self.jenny),
          ("^/v(ideo)?(\s+(?P<duration>\d+)(\s+(?P<fps>\d+(\.\d+)?))?)?$", self.video),
          ("^/c(amera)?$", self.camera)]

    def jenny(self, driver, message, match):
        return Message("bot", u"Mi vida es mucho más bonita desde que tú estás en ella.")

    def camera(self, driver, message, match):
        try:
            # initialize the camera
            cam = cv2.VideoCapture(0)   # 0 -> index of camera
            s, img = cam.read()
            cam.release()
            if s:
                cv2.imwrite("image.jpg",img) #save image
                return Message("bot", "image.jpg", "image/jpeg")
        except Exception as e:
            logging.exception("Error sending answer for %s:%s" % (answer.text, e))
            return Message("bot", u"error capturing picture")

    def video(self, driver, message, match):
        cap = cv2.VideoCapture(0)
        start = time.time()
        duration = int(match.group("duration")) if match.group("duration") is not None else 3
        fps = float(match.group("fps")) if match.group("fps") is not None else 20
        imgs = []
        last_frame = time.time()
        for i in range(1000):
            # Capture frame-by-frame
            ret, frame = cap.read()
            imgs.append("image%d.png" % i)
            cv2.imwrite(imgs[-1], frame) #save image
            if time.time() - start >= duration:
                break
            waiting = 1/fps - (time.time()-last_frame)
            if waiting > 0:
                time.sleep(waiting)
            last_frame = time.time()
        # When everything done, release the capture
        cap.release()
        fake_fps = 20 if fps>5 else 5
        subprocess.check_call(("ffmpeg -r "+str(fake_fps)+" -i image%d.png -vcodec mpeg4 -y image.mp4").split(' '))
        for img in imgs:
            os.remove(img)

        return Message("bot", "image.mp4", "video/mp4")

# for tests
def main():
    PersonalView().video(None, None, re.compile("^/v(ideo)?(\s+(?P<duration>\d+)(\s+(?P<fps>\d+(\.\d+)?))?)?$").match("/video 60 1"))
    

if __name__=="__main__":
    main()
