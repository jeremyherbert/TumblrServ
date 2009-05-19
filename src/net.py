# Contains functions related to data transfer to and from tumblr

import urllib2, re, json, yaml

def pull_data(source, should_return_data=False):
    if is_url(source): # if the user provided a url
        if source.find('/api/read/json') > -1: # and if they provided a url to a direct json source
            url = source # let them keep their page size choice
        else:
            if source[-1] == '/': source = source[:-1] # make sure there is no trailing slash
            url = source + "/api/read/json?num=50"
    elif re.match(r'^[^\ ]*$', source): # if the argument has no spaces, we are going to assume it is a username
        url = "http://%s.tumblr.com/api/read/json?num=50" % source
    else:
        err_exit("""An invalid datasource was given. Please use a tumblr username:
        
tumblrserv.py --pull-data example

or a full url:

tumblrserv.py --pull-data http://example.tumblr.com""") # exit with return code 1
    
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
        json_markup = json_markup.replace(uni, "&#%s;" % (str(int(uni[2:], 16))) )
    
    # get rid of the javascript at the start of the json
    json_markup = json_markup.replace('var tumblr_api_read = ', '')
        
    # now we can finally parse the data
    try:
        data = json.read(json_markup)
    except Exception, detail:
        pdb.set_trace()
        err_exit("The url %s does not contain valid json." % url)
    
    if should_return_data:
        return data
    else:
        print "Writing yaml...",
        # write the data out in yaml form
        yaml_handle = open('data/data.yml', 'w')
        yaml_handle.write(yaml.dump(data, default_flow_style=False).replace('\_', ''))
        print "done!\nPlease see data/data.yml for the exported tumblr data."
        sys.exit(0) # graceful exit
    
def publish_theme(url, username, password):
    pass