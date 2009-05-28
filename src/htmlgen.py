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

def generate_html(config, markup, data, page_number, per_page):
    """
    Generates html given markup and data. Optionally takes already parsed posts.
    
    generate_html(dict, str, dict, list) -> str
    """
    html = markup
    html = insert_meta_colours(html)
    posts_markup = extract_post_markup(html)
    
    if not posts_markup: return html
    
    data_to_generate = data['posts'][(page_number-1) * per_page : (page_number-1) * per_page + per_page]
    
    posts = generate_posts(data_to_generate, posts_markup)
    
    post_html = ''
    for post in posts:
        # check if it is a new date
        post_index = posts.index(post)
        if post_index != 0:
            post.new_date = new_day( posts[post_index-1], post )
        else:
            post.new_date = True
        
        # get the post html
        post_html += post.generate_html()
        
    # check if we should replace images
    if not config['optimisations']['display_images']:
        images = re.findall(r'<img src=.+>', post_html)
        print str(images)
        for image in images:
            width, height = 50, 50
            post_html = post_html.replace(image, '<div style="background-color: #A8AD80; width: %spx; height: %spx" >&nbsp;</div>' % (width, height))
    
    # replace embeds if neccessary
    if not config['optimisations']['display_embeds']:
        embeds = re.findall(r'<object.+</object>',post_html)
        print str(embeds)
        for embed in embeds:
            width, height = 50, 50
            post_html = post_html.replace(embed, '<div style="background-color: #5D917D; width: %spx; height: %spx;" >&nbsp;</div>' % (width, height))
    
    html = re.sub(re.compile(r'{block:Posts}.*{/block:Posts}',re.DOTALL) , post_html, html )
    
    html = replace_several([
        ('{Title}', data['tumblelog'].get('title', ''))
        ], html)
    html = render_conditional_block('Description', [('Description', data['tumblelog'].get('description', ''))], html)
    html = render_conditional_block('PostSummary', [('PostSummary', data['tumblelog'].get('post_summary', ''))], html)
    
    return html