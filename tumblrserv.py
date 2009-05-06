#!/usr/bin/env python
#################################
#
#	tumblrserv.py
#
#################################

import os, sys, ftplib, yaml, cherrypy

from src.post_classes import *
from src import json

print "hellooo"

test_text = {'bookmarklet': 0,
 'date': 'Sun, 03 May 2009 18:45:00',
 'date-gmt': '2009-05-03 08:45:00 GMT',
 'feed-item': '',
 'format': 'html',
 'from-feed-id': 0,
 'id': 102894242,
 'mobile': 0,
 'regular-body': '<p>Neutrophils (a type of white blood cell) are so good at their job of destroying cells that they often damage some tissue of the host. So when the host is deciding whether and how to attack a germ, it actually takes into account the level of collateral damage that will occur. Neat!</p>\n<p><i>taken from: doi:10.1038/nri1785</i></p>',
 'regular-title': 'Interesting fact of the day',
 'type': 'regular',
 'unix-timestamp': 1241340300,
 'url': 'http://ilikewatermelon.tumblr.com/post/102894242'}
 
test_photo = {'bookmarklet': 0,
             'date': 'Tue, 05 May 2009 19:36:09',
             'date-gmt': '2009-05-05 09:36:09 GMT',
             'feed-item': '',
             'format': 'html',
             'from-feed-id': 0,
             'id': 103686985,
             'mobile': 0,
             'photo-caption': 'srsly.',
             'photo-url-100': 'http://22.media.tumblr.com/hq1cnYRytn3ya31czE9Ird3No1_100.jpg',
             'photo-url-250': 'http://15.media.tumblr.com/hq1cnYRytn3ya31czE9Ird3No1_250.jpg',
             'photo-url-400': 'http://20.media.tumblr.com/hq1cnYRytn3ya31czE9Ird3No1_400.jpg',
             'photo-url-500': 'http://5.media.tumblr.com/hq1cnYRytn3ya31czE9Ird3No1_500.jpg',
             'photo-url-75': 'http://20.media.tumblr.com/hq1cnYRytn3ya31czE9Ird3No1_75sq.jpg',
             'photos': [],
             'type': 'photo',
             'unix-timestamp': 1241516169,
             'url': 'http://ilikewatermelon.tumblr.com/post/103686985'}
 
mk_t = """<li class="post text">{block:Title}<h3><a href="{Permalink}">{Title}</a></h3>{/block:Title}{Body}</li>
"""

mk_p = """<li class="post photo"><img src="{PhotoURL-400}" alt="{PhotoAlt}"/>{block:Caption}<div class="caption">{Caption}</div>{/block:Caption}</li>
"""

t = TextPost(0,test_text,mk_t)
p = PhotoPost(1, test_photo, mk_p)