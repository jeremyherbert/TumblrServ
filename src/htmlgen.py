# functions to generate the html for output

import cherrypy
from support import *
from server import *
from post_classes import *

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

def generate_posts(data, posts_markup):
    """
    Generates a list of posts given the post objects and data.
    
    generate_posts(dict) -> list
    """
    posts = []
    for post in data:
        exec "posts.append(%sPost(data.index(post), post, replace_all_except_block('%s', posts_markup)))" % (post.get('type', '').capitalize(), post.get('type', '').capitalize())
    return posts

def generate_html(config, markup, data, posts=None):
    """
    Generates html given markup and data. Optionally takes already parsed posts.
    
    generate_html(dict, str, dict, list) -> str
    """
    html = markup
    html = insert_meta_colours(html)
    posts_markup = extract_post_markup(html)
    
    posts = generate_posts(data['posts'], posts_markup) if not posts else posts
    
    post_html = ''
    for post in posts:
        post_index = posts.index(post)
        if post_index != 0:
            post.new_date = new_day( posts[post_index-1], post )
        else:
            post.new_date = True
        post_html += post.generate_html()
        
    html = re.sub(re.compile(r'{block:Posts}.*{/block:Posts}',re.DOTALL) , post_html, html )
    
    html = replace_several([
        ('{Title}', data['tumblelog'].get('title', ''))
        ], html)
    html = render_conditional_block('Description', [('Description', data['tumblelog'].get('description', ''))], html)
    html = render_conditional_block('PostSummary', [('PostSummary', data['tumblelog'].get('post_summary', ''))], html)
    
    # check if we should replace images
    if not config['optimisations']['display_images']:
        images = re.findall(r'<img src=.+>', html)
        print str(images)
        for image in images:
            # try to extract width, height
            #if image.find('width') > -1 and image.find('height') > -1:
            #    height = re.search(r'height=(.+)&width=(.+)', image).group()
            #else:
            #    # just draw a 50 by 50 box
            #    height = '50'
            #    width = '50'
            width = 50
            height = 50
            html = html.replace(image, '<div style="background-color: #A8AD80; width: %spx; height: %spx" >&nbsp;</div>' % (width, height))
    
    if not config['optimisations']['display_embeds']:
        embeds = re.findall(r'<object.+</object>', html)
        print str(embeds)
        for embed in embeds:
            # try to extract width, height
            #if embed.find('width') > -1 and embed.find('height') > -1:
            #    height= re.search(r'height="(.+)">', embed).group()
            #    width = re.search(r'width="(.+)">', embed).group()
            #else:
            #    # just draw a 50 by 50 box
            #    height = '50'
            #    width = '50'
            width = 50
            height = 50
            html = html.replace(embed, '<div style="background-color: #5D917D; width: %spx; height: %spx;" >&nbsp;</div>' % (width, height))
    #pdb.set_trace()
    return html