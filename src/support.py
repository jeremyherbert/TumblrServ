##    tumblrserv.py implements a Tumblr (http://www.tumblr.com) markup parsing
##    engine and compatible webserver.
##      This is support.py which contains various helper functions.
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

import re, sys, os, yaml
from datetime import datetime

post_types = ['Regular', 'Photo', 'Quote', 'Link', 'Conversation', 'Video',\
 'Audio', 'Conversation']

def within_constraints(constraints):
    """
    Check if a list of constraints has been met. If not, print the error
    message.
    
    within_constraints(list[(bool, str)]) -> bool
    """
    return_val = True
    for outcome, message in constraints:
        if not outcome: # if a particular test failed
            print "An error occurred: " + str(message) # print it
            
            # we do this so that all of the errors show up, not just one
            return_val = False 
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
        # This can occasionally cause a Unicode error. Hopefully I fixed that
        # problem but it is still here to make sure nothing breaks (untrusted
        # data is untrusted data after all)
        try:
            outstring = outstring.replace(to_replace, replacement) 
        except: 
            print "There was a UnicodeError in %s." % str(self)
    return outstring
    
def render_conditional_block(block_name, tag_contents_list, instring):
    """
    If data is available, renders a conditional block. If the data is not
    available, it deletes the block. For example:
    
    if the passed data is 'hello':
    {block:Caption}<p>{Caption}</p>{/block:Caption} -> <p>hello</p>
    however if the passed data is '':
    {block:Caption}<p>{Caption}</p>{/block:Caption} -> 
    
    render_conditional_block(str, list, str) -> str
    """
    #pdb.set_trace()
    if tag_contents_list[0][1]: # if the first element has content
        outstring = replace_several([
               ('{block:%s}' % block_name, ''), # remove the block tags
               ('{/block:%s}' % block_name, ''), 
               ], instring)
        for tag, contents in tag_contents_list:
            outstring = outstring.replace('{%s}' % tag, contents)
            
        return outstring

    else:
           # if we get here, there is no data provided, so destroy the tags and
           # everything in between
           return delete_block(block_name, instring)
           
def delete_block(block_name, instring):
    """
    Deletes all references to a given block.
    
    delete_block(str, str) -> str
    """
    return re.sub(re.compile(r'{block:%s}.+{/block:%s}' % (block_name,\
     block_name), re.DOTALL), '', instring) 
           
def nice_number_formatting(number):
    """
    Puts commas into a number at every third spot to make the number more
    readable (this was surprisingly hard to do efficiently).
    
    nice_number_formatting(int) -> str
    """
    liststr = list(str(number)) 
    liststr.reverse() # turn the number into a list and reverse it
    
    # as the list gets one element larger each time we add a comma, we put one
    # in every (n+n/3) spot
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
            output = re.sub(re.compile(r'{block:%s}.+{/block:%s}' % (block,\
             block), re.DOTALL), '', output)
             
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
    
def render_dates(markup, attr, newdate=None):
    """
    Renders all of the date tags.
    
    render_dates(str, obj) -> str
    """
    html = markup
    if newdate:
        pass
    else:
        pass
    return html
    
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
    try:
        return arg_list[ arg_list.index(item) + n ]
    except:
        err_exit('You did not provide enough arguments!')
    
def is_url(string_to_check):
    """
    Runs a regex on the first argument to see if it is a url.
    
    is_url(str) -> bool
    """
    return True if re.match(r'^http://.*$', string_to_check) else False
    
def insert_meta_colours(markup):
    """
    Extracts the colours from the theme file and inserts them in the tag
    locations.
    
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
    
    if not os.path.exists(path): err_exit("The configuration file at %s\
 does not exist." % path)
    
    config_handle = open(path, 'U')
    try:
        config = yaml.load(config_handle.read())
    except Exception, detail:
        err_exit("The configuration file is not valid yaml. The error given\
 was:\n%s" % str(detail))
        
    config_handle.close()
    
    set_if_nexists(config, 'defaults', {'theme_name':'theme',\
 'data_name:':'data'}) # set the default values
    set_if_nexists(config['defaults'], 'theme_name', 'theme')
    set_if_nexists(config['defaults'], 'data_name', 'data')
    
    return config
    
def get_data(path):
    """
    Opens the data from a flat yaml file.
    
    get_data(str) -> dict
    """
    if not os.path.exists(path): err_exit("The data file at %s does not exist."\
 % path)
    
    data_handle = open(path, 'U')
    try:
        data = yaml.load(data_handle.read())
    except Exception, detail:
        err_exit("The data is not valid yaml. The error given was:\n%s" %\
 str(detail))
        
    data_handle.close()
    
    return data
    
def get_markup(path):
    """
    Opens the data from a flat yaml file.
    
    get_data(str) -> dict
    """
    if not os.path.exists(path): err_exit("The theme file at %s does not \
exist." % path)
    
    markup_handle = open(path, 'U')
    markup = markup_handle.read()
    markup_handle.close()
    
    # We need to transform a couple of tags so that old themes still work
    markup = replace_several([
        ('block:Text', 'block:Regular'),
        ('block:Chat', 'block:Conversation'),
        ], markup)
    
    return markup
    
def extract_post_markup(markup):
    """
    Returns the markup associated with posts.
    
    extract_post_markup(str) -> str
    """
    try:
        return re.search(r'{block:Posts}(?P<markup>.+){/block:Posts}', markup,\
         re.DOTALL).group('markup')
    except:
        return ''
    
def s_suffix(number):
    """
    Returns s if number > 1
    
    s_suffix(int) -> str
    """
    return 's' if number > 1 else ''
    
def contextual_time(dt):
    """
    Generates a nice looking time string relative to now.
    
    contextual_time(datetime) -> str
    """
    month_length = {
        1: 31, # January
        2: 28, # Feburary
        3: 31, # March
        4: 30, # April
        5: 31, # May
        6: 30, # June
        7: 31, # July
        8: 31, # August
        9: 30, # September
        10: 31, # October
        11: 30, # November
        12: 31, # December
        }
    
    dt_now = datetime.now()
    time_delta = dt_now - dt
    
    seconds = time_delta.seconds
    minutes = time_delta.seconds/60
    hours = seconds/3600
    days = time_delta.days
    weeks = days/7
    years = days/365
    
    # months is tricky; we need to keep subtracting days until we 
    # reach < month length
    d = days - 365*years
    m = 0
    
    while d > month_length[12-m]:
        d -= month_length[12-m]
        m += 1

    months = 12*years + m
    
    times = ['second', 'minute', 'hour', 'day', 'week', 'month', 'year']
    times.reverse()
    
    outstring = ''
    for time in times:
        exec('outstring = str(%ss) + " %s" + s_suffix(%ss) + " ago" if %ss else\
 ""' % (time, time, time, time) )
        if outstring:
            return outstring
    
    # should never get here
    err_exit('A broken timestamp was passed to contextual_time')
    
def number_suffix(number):
    """
    Returns 'st','nd','rd','th' depending on number
    
    number_suffix(int) -> str
    """
    last_number = str(number)[-1]
    if last_number == 1:
        return 'st'
    elif last_number == 2:
        return 'nd'
    elif last_number == 3:
        return 'rd'
    else:
        return 'th'
    
def render_dates(new_date, timestamp, markup):
    """
    Renders all of the date tags in markup.
    
    render_dates(bool, str, str) -> str
    """
    html = markup
    # get the date from the timestamp
    if not re.match(r'[0-9]*', str(timestamp)):
        err_exit('Invalid timestamp given.')
        
    dt = datetime.fromtimestamp(timestamp)
    
    date_codes = [
        ('DayOfMonth', str(dt.day)),
        ('DayOfMonthWithZero', str(dt.day).zfill(2)),
        ('DayOfWeek', dt.strftime('%A')),
        ('ShortDayOfWeek', dt.strftime('%a')),
        ('DayOfWeekNumber', dt.strftime('%w')),
        ('DayOfMonthSuffix', number_suffix(dt.day)),
        ('DayOfYear', dt.strftime('%j')),
        ('WeekOfYear', dt.strftime('%U')),
        ('Month', dt.strftime('%B')),
        ('ShortMonth', dt.strftime('%b')),
        ('MonthNumber', str(dt.month)),
        ('MonthNumberWithZero', str(dt.month).zfill(2)),
        ('Year', str(dt.year)),
        ('ShortYear', str(dt.year)[2:]),
        ('AmPm', dt.strftime('%p').lower()),
        ('CaptialAmPm', dt.strftime('%p').upper()),
        ('12Hour', dt.strftime('%I')),
        ('24Hour', str(dt.hour)),
        ('12HourWithZero', dt.strftime('%I').zfill(2)),
        ('24HourWithZero', str(dt.hour).zfill(2)),
        ('Minutes', str(dt.minute).zfill(2)),
        ('Seconds', str(dt.second).zfill(2)),
        ('Beats', str(dt.microsecond * 1000).zfill(2)),
        ('Timestamp', str(timestamp)),
        ('TimeAgo', contextual_time(dt)),
        ]
    
    if new_date:
        html = render_conditional_block('NewDayDate', date_codes, html)
        html = delete_block('SameDayDate', html)
    else:
        html = render_conditional_block('SameDayDate', date_codes, html)
        html = delete_block('NewDayDate', html)
    
    return html
    
def new_day(post_before, post):
    """
    Check if a day is new or not.
    
    new_day(obj, obj) -> bool
    """
    dt_before = datetime.fromtimestamp(post_before._attr['unix-timestamp'])
    dt_after = datetime.fromtimestamp(post._attr['unix-timestamp'])
    
    if dt_before.day == dt_after.day and dt_before.month == dt_after.month and\
     dt_before.year == dt_after.year: 
        return False
    return True
    
def replace_with_static_urls(markup):
    """
    Replaces paths to files on the server with locally served versions
    
    replace_with_static(str) -> str
    """
    output = markup
    urls = []
    for filename in os.listdir('static'):
        
        try:
            urls += re.findall(r'src=\"(?P<url>.+\/%s)\"' % filename, output)
        except:
            pass
            
        try:
            urls += re.findall(r'url\(\'(?P<url>.+\/%s)\'\)' % filename, output)
        except:
            pass
            
        try:
            urls += re.findall(r'url\((?P<url>.+\/%s)\)' % filename, output)
        except:
            pass
            
        for url in urls:
            output = output.replace(url, '/%s' % filename)
    return output
    
def extract_colours(markup):
    """
    Extracts the meta colours from given markup
    
    extract_colours(str) -> list
    """
    return re.findall(r'<meta name="color:.+" content="#(.+)"/>', markup)