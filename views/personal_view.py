# -*- coding: utf-8 -*-
from message import Message
from basic_view import View
from cv2 import *
import logging

class PersonalView(View):
    def routes(self):
        return [
          ("^/jenny", self.jenny),
          ("^/camera", self.foto)]

    def jenny(self, message, match):
        return Message("bot", u"Mi vida es mucho más bonita desde que tú estás en ella.")

    def foto(self, message, match):
        try:
            # initialize the camera
            cam = cv2.VideoCapture(0)   # 0 -> index of camera
            s, img = cam.read()
            cam.release()
            if s:
                cv2.imwrite("foto.jpg",img) #save image
                return Message("bot", "foto.jpg", "image")
        except Exception as e:
            logging.exception("Error sending answer for %s:%s" % (answer.text, e))
            return Message("bot", u"error capturing picture")

