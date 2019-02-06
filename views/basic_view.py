from message import Message

class View:
    def routes(self):
        return []

class BasicView(View):
    def routes(self):
        return [
            ("^/ping$", self.ping),
            ("^/e(cho)?\s(?P<echo_message>[^$]+)$", self.echo)]
    
    def echo(self, driver, message, match):
        return Message("bot", "Vaco says: %s" % match.group("echo_message"))

    def ping(self, driver, message, match):
        return Message("bot", "pong")

