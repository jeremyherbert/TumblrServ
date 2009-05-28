##    tumblrserv.py implements a Tumblr (http://www.tumblr.com) markup parsing
##    engine and compatible webserver.
##      This is server.py which contains the main server controller class.
##
##    Copyright (C) 2009 Jeremy Herbert
##    Contact mailto:jeremy@jeremyherbert.net
##
##    This program is free software; you can redistribute it and/or
##    modify it under the terms of the GNU General Public License
##    as published by the Free Software Foundation; either version 2
##    of the License, or (at your option) any later version.
##    
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##    
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
##    02110-1301, USA.

import cherrypy
from support import *
from server import *
from post_classes import *
from htmlgen import *

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video',\
 'Audio', 'Conversation']

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
        self.markup = get_markup('themes/%s.thtml' %\
         config['defaults']['theme_name'])
        self.data = get_data("data/%s.yml" % config['defaults']['data_name'])
        
    def reload(self):
        """
        Reloads the markup from disk.
        
        TumblrServ.reload(self) -> None
        """
        self.markup = get_markup('themes/%s.thtml' %\
         self.config['defaults']['theme_name'])
    
    def index(self, page='1', per_page='10', q=None):
        """
        The index page for the controller. This should not be called outside of
        CherryPy.
        
        TumblrServ.index(self, str, str) -> str
        """
        self.reload()
        
        if self.config['optimisations'].get('do_nothing') == True:
            return self.markup
        
        # generate html with 10 per page
        html = generate_html(self.config, self.markup, self.data, int(page),\
         int(per_page)) 
        
        # we are not in search mode, so delete all the search blocks
        html = delete_block('SearchPage', html)
        html = replace_several([
            ('{SearchQuery}', ''),
            ('action="/search"', 'action="/"'),
        ], html)
        
        html = replace_with_static_urls(html)
        
        total_pages = len(self.data['posts'])/int(per_page)
        
        # if we are on the first page
        if int(page) < 2:
            html = render_conditional_block('PreviousPage', [('PreviousPage',\
             '')], html)
        else:
            html = render_conditional_block('PreviousPage', [('PreviousPage',\
             '/?page=%s&per_page=%s' % ( str(int(page)-1), per_page ) )], html)
        
        # if we are on the last page
        if int(page)+1 > total_pages:
            html = render_conditional_block('NextPage', [('NextPage', '')],\
             html)
             
        else:
            html = render_conditional_block('NextPage', [('NextPage',\
             '/?page=%s&per_page=%s' % ( str(int(page)+1), per_page ) )], html)
        
        html = replace_several([
            ('{CurrentPage}', page),
            ('{TotalPages}', str(total_pages))
        ], html)
        
        html = html.replace('{RSS}', self.config['defaults']['rss_url'])
        
        # a nice easter egg for testing!
        html = html.replace('{MeaningOfLife}', '42') 
        
        return html
        
    # set index as the default route
    index.exposed = True 


