# contains the main server class

import cherrypy
from support import *
from server import *
from post_classes import *

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

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
        
        html = self.markup
        html = insert_meta_colours(html)
        posts_markup = extract_post_markup(html)
        
        self.posts = []
        for post in self.data['posts']:
            exec "self.posts.append(%sPost(self.data['posts'].index(post), post, replace_all_except_block('%s', posts_markup)))" % (post.get('type', '').capitalize(), post.get('type', '').capitalize())
        
        post_html = ''
        for post in self.posts:
            post_html += post.generate_html()
            
        html = re.sub(re.compile(r'{block:Posts}.*{/block:Posts}',re.DOTALL) , post_html, html )
        
        html = replace_several([
            ('{Title}', self.data['tumblelog'].get('title', ''))
            ], html)
        html = render_conditional_block('Description', 'Description', self.data['tumblelog'].get('description', ''), html)
        
        return html
        
    # set index as the default route
    index.exposed = True 