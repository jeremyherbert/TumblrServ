#!/usr/bin/env python
#################################
#
#	tumblrserv.py
#
#################################

import os, sys, ftplib, yaml, cherrypy, re, pdb

from src.post_classes import *
from src import json

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

def replace_all_except_block(block_name, markup):
    output = markup
    for block in post_types:
        if not block_name == block:
            output = re.sub(re.compile(r'{block:%s}.+{/block:%s}' % (block, block), re.DOTALL), '', output)
    output = replace_several([
        ('{block:%s}' % (block_name), ''),
        ('{/block:%s}' % (block_name), ''),
        ], output)
    return output

if os.path.exists('data/data.yml'):
    temp_handle = open('data/data.yml', 'r')
    data = yaml.load(temp_handle.read())
    temp_handle.close()
else:
    print "The file data/data.yml does not exist."
    sys.exit(1)
    
temp_handle = open('themes/theme.thtml', 'r')
theme_markup = temp_handle.read()
temp_handle.close()

posts_markup = re.search(r'{block:Posts}(?P<markup>.+){/block:Posts}', theme_markup, re.DOTALL).group('markup')
        
meta_colours = re.findall(r'name=\"color:(.+)\" content=\"#([0-9A-Fa-f]{3,6})\"', theme_markup)
for name, colour in meta_colours:
    theme_markup = theme_markup.replace("{color:%s}" % name, "#" + colour)

posts = []
for post in data['posts']:
    exec "posts.append(%sPost(data['posts'].index(post), post, replace_all_except_block('%s', posts_markup)))" % (post.get('type', '').capitalize(), post.get('type', '').capitalize())

post_html = ''
for post in posts:
    post_html += post.generate_html()
    
final = re.sub(re.compile(r'{block:Posts}.*{/block:Posts}',re.DOTALL) , post_html, theme_markup, )

final = replace_several([
    ('{Title}', data['tumblelog'].get('title', ''))
    ], final)
final = render_conditional_block('Description', 'Description', data['tumblelog'].get('description', ''), final)

repl = '''<iframe src="http://www.tumblr.com/dashboard/iframe?src=http%3A%2F%2Filikewatermelon.tumblr.com%2F" 
border="0" scrolling="no" width="278" height="25" allowTransparency="true"
frameborder="0" style="position:absolute; z-index:1337; top:0px; right:0px; border:0px;
background-color:transparent; overflow:hidden;" id="tumblr_controls"></iframe></body>
'''
final = final.replace('</body>', repl)
temp = open('out.html', 'w')
temp.write(final.encode('utf-8'))
temp.close()