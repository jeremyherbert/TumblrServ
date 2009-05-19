# support.py
import re, sys, os, yaml

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video', 'Audio', 'Conversation']

def within_constraints(constraints):
    """
    Check if a list of constraints has been met. If not, print the error message.
    
    within_constraints(list[(bool, str)]) -> bool
    """
    return_val = True
    for outcome, message in constraints:
        if not outcome: # if a particular test failed
            print "An error occurred: " + str(message) # print it
            return_val = False # we do this so that all of the errors show up, not just one
    return return_val
    
def has_keys(dict_to_check, keys):
    """
    Check if a given dictionary has all of the keys.
    
    has_keys(dict, list[str]) -> bool
    """
    return reduce(lambda x,y: x and dict_to_check.has_key(y), keys, True) 

def replace_several(replacements, instring):
    """
    Runs a replace on more than one pair of strings at a time.
    
    replace_several(list[(str,str)], str) -> str
    """
    outstring = instring
    for to_replace, replacement in replacements:
        # This can occasionally cause a Unicode error. Hopefully I fixed that problem but it is 
        # still here to make sure nothing breaks (untrusted data is untrusted data after all)
        try:
            outstring = outstring.replace(to_replace, replacement) 
        except: 
            print "There was a UnicodeError in %s." % str(self)
    return outstring
    
def render_conditional_block(block_name, tag, contents, instring):
    """
    If data is available, renders a conditional block. If the data is not available, it deletes the block. For example:
    
    if the passed data is 'hello':
    {block:Caption}<p>{Caption}</p>{/block:Caption} -> <p>hello</p>
    however if the passed data is '':
    {block:Caption}<p>{Caption}</p>{/block:Caption} -> 
    
    render_conditional_block(str, str, str, str) -> str
    """
    if contents:
           return replace_several([
               ('{block:%s}' % block_name, ''), # remove the block tags
               ('{/block:%s}' % block_name, ''), 
               ('{%s}' % tag, contents), # and insert the data we want
               ], instring)
    else:
           # if we get here, there is no data provided, so destroy the tags and everything in between
           return re.sub(re.compile(r'{block:%s}.+{/block:%s}' % (block_name, block_name), re.DOTALL), '', instring) 
           
def nice_number_formatting(number):
    """
    Puts commas into a number at every third spot to make the number more readable (this was surprisingly hard to do efficiently).
    
    nice_number_formatting(int) -> str
    """
    liststr = list(str(number)) 
    liststr.reverse() # turn the number into a list and reverse it
    
    # as the list gets one element larger each time we add a comma, we put one in every (n+n/3) spot
    for n in range(0,len(liststr),3): liststr.insert(n+n/3, ',') 
    liststr.reverse()
    return ''.join(liststr[:-1]) # drop off the comma at the end

def replace_all_except_block(block_name, markup):
    """
    Deletes all of the blocks except the one specified.
    
    replace_all_except_block(str) -> str
    """
    output = markup
    for block in post_types:
        if not block_name == block:
            output = re.sub(re.compile(r'{block:%s}.+{/block:%s}' % (block, block), re.DOTALL), '', output)
    output = replace_several([
        ('{block:%s}' % (block_name), ''),
        ('{/block:%s}' % (block_name), ''),
        ], output)
    return output
    
def contains(list_to_check, item):
    """
    Find out how many times an item is contained in a list.
    
    contains(list, obj) -> int
    """
    n=0
    for element in list_to_check:
        if element == item:
            n+=1
    return n
    
def err_exit(error_message,code=1):
    """
    Print an error message and exit.
    
    err_exit(str, int) -> None
    """
    print error_message
    sys.exit(code)
    
def next_arg(arg_list, item, n=1):
    """
    Returns the next element in a list.
    
    next_arg(list, obj, int)
    """
    return arg_list[ arg_list.index(item) + n ]
    
def is_url(string_to_check):
    """
    Runs a regex on the first argument to see if it is a url.
    
    is_url(str) -> bool
    """
    return True if re.match(r'^http://.*$', string_to_check) else False
    
def insert_meta_colours(markup):
    """
    Extracts the colours from the theme file and inserts them in the tag locations.
    
    insert_meta_colours(str) -> str
    """
    meta_colours = re.findall(r'name=\"color:(.+)\" content=\"#([0-9A-Fa-f]{3,6})\"', markup)
    for name, colour in meta_colours:
        markup = markup.replace("{color:%s}" % name, "#" + colour)
        
    return markup
    
def set_if_nexists(dict_to_set, key, data):
    """
    Sets a value only if the key does not yet exist.
    
    set_if_nexists(dict, str, obj)
    """
    if not dict_to_set.get(key):
        dict_to_set[key] = data
    
def get_config(path):
    """
    Loads and validates the configuration file.
    
    get_config(str) -> dict
    """
    
    if not os.path.exists(path): err_exit("The configuration file at %s does not exist." % path)
    
    config_handle = open(path, 'U')
    try:
        config = yaml.load(config_handle.read())
    except Exception, detail:
        err_exit("The configuration file is not valid yaml. The error given was:\n%s" % str(detail))
        
    config_handle.close()
    
    set_if_nexists(config, 'defaults', {'theme_name':'theme', 'data_name:':'data'}) # set the default values
    set_if_nexists(config['defaults'], 'theme_name', 'theme')
    set_if_nexists(config['defaults'], 'data_name', 'data')
    
    return config
    
def get_data(path):
    """
    Opens the data from a flat yaml file.
    
    get_data(str) -> dict
    """
    if not os.path.exists(path): err_exit("The data file at %s does not exist." % path)
    
    data_handle = open(path, 'U')
    try:
        data = yaml.load(data_handle.read())
    except Exception, detail:
        err_exit("The data is not valid yaml. The error given was:\n%s" % str(detail))
        
    data_handle.close()
    
    return data
    
def get_markup(path):
    """
    Opens the data from a flat yaml file.
    
    get_data(str) -> dict
    """
    if not os.path.exists(path): err_exit("The theme file at %s does not exist." % path)
    
    markup_handle = open(path, 'U')
    markup = markup_handle.read()
    markup_handle.close()
    
    return markup
    
def extract_post_markup(markup):
    """
    Returns the markup associated with posts.
    
    extract_post_markup(str) -> str
    """
    
    return re.search(r'{block:Posts}(?P<markup>.+){/block:Posts}', markup, re.DOTALL).group('markup')