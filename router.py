"""
    The Route Layer.
    Here the message is routed to its proper view.
    The routes are defined with regular expressions and callback functions (just like any web framework).
"""
import re
import logging

from views.basic_view import BasicView
from views.personal_view import PersonalView
from views.media import MediaViews
# ~ from views.super_views import SuperViews
# ~ from views.group_admin import GroupAdminViews
# ~ from views.google import GoogleViews
# ~ from views.bing import BingViews
# ~ from views.quiz import QuizView
from views.help_view import HelpView


class RouteLayer():
    def __init__(self):
        """
            The definition of routes and views (callbacks)!

            For the simple message handling, just calls the callback function, and expects a message entity to return.
            For more complex handling, like asynchronous file upload and sending, it creates a object passing 'self',
            so the callback can access the 'self.toLower' method
        """
        routes = []
        # Basic view (echo/ping)
        routes.extend(BasicView().routes())
        
        # Personal view (camera capturing)
        routes.extend(PersonalView().routes())
        
        # Google views to handle tts, search and youtube
        # ~ routes.extend(GoogleViews(self).routes)

        # Bing views to handle image search
        # ~ routes.extend(BingViews(self).routes)

        # Media views to handle url print screen and media download
        routes.extend(MediaViews().routes())

        # adds super fun views
        # ~ routes.extend(SuperViews(self).routes)

        # adds quiz views
        # ~ routes.extend(QuizView(self).routes)

        # group admin views disabled by default.
        # read the issue on: https://github.com/joaoricardo000/whatsapp-bot-seed/issues/4
        # enable on your own risk!
        # routes.extend(GroupAdminViews(self).routes)
        
        # help view
        routes.extend(HelpView().routes())

        self.views = [(re.compile(pattern), callback) for pattern, callback in routes]

    def route(self, driver, message):
        if message.type == "text":
            "Get the text from message and tests on every route for a match"
            try:
                for route, callback in self.views:
                    match = route.match(message.data)
                    if match:  # in case of regex match, the callback is called, passing the message and the match object
                        logging.info("(MSG)[%s]:\t%s" % (message.sender, message.data))
                        return callback(driver, message, match)
            except Exception as e:
                logging.exception("Error routing message: %s from %s\n%s" % (message.data, message.sender, e))
        return None
