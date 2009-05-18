# contains the main server class

import cherrypy

class TumblrServ(object):
    def index(self):
        return self.html
    index.exposed = True