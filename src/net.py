##    tumblrserv.py implements a Tumblr (http://www.tumblr.com) markup parsing
##    engine and compatible webserver.
##      This is net.py which contains functions related to data transfer to 
##      and from tumblr.
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

import urllib, urllib2, cookielib, re, json, yaml, ClientForm

from support import *

def pull_data(source, should_return_data=False):
    if is_url(source): # if the user provided a url
        # and if they provided a url to a direct json source
        if source.find('/api/read/json') > -1: 
            url = source # let them keep their page size choice
        else:
            # make sure there is no trailing slash
            if source[-1] == '/': source = source[:-1] 
            url = source + "/api/read/json?num=50"
            
    # if the argument has no spaces, we are going to assume it is a username
    elif re.match(r'^[^\ ]*$', source): 
        url = "http://%s.tumblr.com/api/read/json?num=50" % source
    else:
        # exit with return code 1
        err_exit("""An invalid datasource was given. Please use a tumblr  username:
        
tumblrserv.py --pull-data example

or a full url:

tumblrserv.py --pull-data http://example.tumblr.com""") 
    
    print "Pulling data from: %s" % url
    
    # get the data
    try:
        opener = urllib2.urlopen(url)
        json_markup = opener.read()
        opener.close()
    except Exception, detail:
        err_exit("Could not get data from %s. Reason:\n%s" % (url, detail))
        
    # transform any unicode characters into their html equivalent
    # this saves a significant amount of complexity in saving files
    unicodes = re.findall(r'\\u[a-fA-F0-9]{4}', json_markup)
    for uni in unicodes: 
        # convert to html representation
        json_markup = json_markup.replace(uni, "&#%s;" % (str(int(uni[2:], 16))) )
    
    # get rid of the javascript at the start of the json
    json_markup = json_markup.replace('var tumblr_api_read = ', '')
        
    # now we can finally parse the data
    try:
        data = json.read(json_markup)
    except Exception, detail:
        err_exit("The url %s does not contain valid json." % url)
    
    if should_return_data:
        return data
    else:
        print "Writing yaml...",
        # write the data out in yaml form
        yaml_handle = open('data/data.yml', 'w')
        yaml_handle.write(yaml.dump(data, \
         default_flow_style=False).replace('\_', ''))

        print "done!\nPlease see data/data.yml for the exported tumblr data."
        sys.exit(0) # graceful exit
    
def publish_theme(url, username, password, html):
    """
    Publishes the theme to tumblr.
    
    publish_theme(url, username, password)
    """
    
    cookiejar = cookielib.CookieJar()
    tumblr_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    
    login = urllib.urlencode({'email': username, 'password': password})
    
    # now we get the auth cookie
    print "Getting auth cookie...",
    tumblr_opener.open('http://www.tumblr.com/login', login)
    print "done"
    
    # now let's get our magic key from the page
    print "Opening tumblr customize page...",
    try:
        resp = tumblr_opener.open('http://www.tumblr.com/customize')
    except:
        err_exit('Could not access the tumblr customise page. Please check your\
 login credentials.')
    print "done"
    
    # parse the forms
    print "Parsing forms...",
    forms = ClientForm.ParseResponse(resp, backwards_compat=False)
    resp.close()
    print "done"
    
    # we are interested in the 3rd form on the page
    try:
        configuration_form = forms[2]
    except IndexError:
        err_exit('The form data could not be extracted; it is likely that your \
internet connection is malfunctioning. Please check your credentials and try \
 again later.')
        
    configuration_form['edit_tumblelog[custom_theme]'] = html
    
    # now we insert the default colours
    n = 0
    colours = extract_colours(html)
    while True:
        try:
            configuration_form['params[%i]' % n] = colours[n]
        except:
            break
        n += 1
    
    # get the request object
    post_request_data = configuration_form.click()
    
    print "Posting new theme data...",
    try:
        resp2 = tumblr_opener.open(post_request_data)
    except urllib2.HTTPError, response2:
        err_exit('An error occured when attempting to post the form data. \
Please check your login credentials.')
    print "done"

    err_exit("Theme uploaded successfully.", 0)
        
    