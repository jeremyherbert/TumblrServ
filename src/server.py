# contains the main server class

import cherrypy
from support import *
from server import *
from post_classes import *
from htmlgen import *

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

class Search(object):
    """
    Handles the data searching. This uses a very slow algorithm, but it is not supposed to be used in production anyway.
    """
    def __init__(self, config, data):
        """
        Initialises the class.
        
        Search.__init__(self, config, data) -> None
        """
        self.config = config
        self.data = data
    
    def search(self, query=None):
        """
        Searches for posts containing a query.
        
        Search.search(self, str)
        """
        if not query:
            return ''
            
        self.markup = get_markup('themes/%s.thtml' % config['defaults']['theme_name'])
        posts = generate_posts(data, extract_post_markup(self.markup))
        filtered_posts = []
        
        for post in posts:
            for key in post._attr.keys():
                if post._attr[key].find(query) > -1:
                    filtered_posts.append(post)
                    continue
                    
        html = generate_html(self.config, self.markup, None, filtered_posts)
        
    search.exposed = True

class TumblrServ(object):
    """
    The main server object for CherryPy
    """
    def __init__(self, config):
        """
        Initialises the class by loading initial data.
        
        TumblrServ.__init__(self, dict) -> None
        """
        self.config = config
        self.markup = get_markup('themes/%s.thtml' % config['defaults']['theme_name'])
        self.data = get_data("data/%s.yml" % config['defaults']['data_name'])
        
        TumblrServ.search = Search(self.config, self.data)
        
    def reload(self):
        """
        Reloads the markup from disk.
        
        TumblrServ.reload(self) -> None
        """
        self.markup = get_markup('themes/%s.thtml' % self.config['defaults']['theme_name'])
    
    def index(self, search=None, page=None):
        """
        The index page for the controller. This should not be called outside of CherryPy.
        
        TumblrServ.index(self, str, str) -> str
        """
        self.reload()
        
        if self.config['optimisations'].get('do_nothing') == True:
            return self.markup
        
        html = generate_html(self.config, self.markup, self.data)
        
        # we are not in search mode, so delete all the search blocks
        html = delete_block('SearchPage', html)
        html = html.replace('{SearchQuery}', '')
        
        return html
        
    # set index as the default route
    index.exposed = True 


