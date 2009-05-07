###
#   post_classes.py
###

# types of posts
#
# text, photo, quote, link, chat, audio, video
import sys, re, pdb

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
           

class Post(object):
    """
    This is the main class for storing data. It implements a number of methods that are intended to be overridden by a 
    child class. Most of the complexity has been packed into this class; most of the child classes simply revolve 
    around setting up the nuances for that type of post. See the comments on individual functions for more information.
    """
    
    def __init__(self, post_index, attr, markup):
        """
        The initialiser for the Post class. This should also be called by every child class. It sets up some data
        structures but expects that the child class will fill (and validate() checks that they are filled properly).
        It takes a post index (currently unused) that acts as a unique id, a dictionary of attributes and associated
        markup. IMPORTANT: no checking is done on the markup; it is assumed to be correct.
        
        Post.__init__(int, dict, str) -> Post
        """
        self._attr = attr
        self._markup = markup
        self.post_index = post_index
        self._critical_keys = []
        self._type = ''
        self._conditional_render_blocks = []
        self._replace_tags = []
    
    def validate(self):
        """
        This function is in lieu of unit testing. It checks that the data provided is adequate given a post type.
        Extra constraints for a child should be put in its own validate() function that calls this.
        
        validate() -> bool
        """
        try:
            return within_constraints([
                (type(self._attr) == dict, '%s was not able to access its attributes' % str(self)), # this should never fail, but anyway
                
                # check for keys that every post should have
                (has_keys(self._attr, ['url', 'type', 'date-gmt', 'date', 'unix-timestamp', 'id']), '%s is missing a critical key' % str(self)),
                (self._attr['format'] == 'html', '%s has an incorrect format' % str(self)),
                
                # check for the keys flagged as critical by the subclass
                (has_keys(self._attr, self._critical_keys), '%s is missing a critical attribute key' % str(self)),
                
                # check that the type set by the subclass matches its actual class
                (self._attr['type'] == self._type, '%s has an incorrect type' % (self._type) ),
                ])
        except Exception, detail:
            print "An error occurred: The validation code failed\n" + str(self) + str(detail)
            return False
            
    def generate_html(self):
        """
        This function generates the HTML for the post. In particular, this function enters data that is common to all
        posts. It then looks at the variables set by the subclass and performs a data replacement and block replacement
        on them also. If any specific functionality is needed, this class should be overridden and called by the child 
        class. If it returns nothing, the class is not validating; check the error messages.
        
        generate_html() -> str
        """
        if not self.validate(): return ''
        self.update() # tell the class to update all of its tag information
        
        output = self._markup # non-destructive 
        
        # first, replace the common data
        output = replace_several([
            ('{Permalink}', self._attr['url']),
            ('{PostID}', str(self._attr['id'])),
            ], output)
        
        # now replace the data set by the subclass
        output = replace_several(self._replace_tags, output)
        
        # and replace the blocks too
        for block_name, tag, attribute in self._conditional_render_blocks:
            output = render_conditional_block(block_name, tag, attribute, output)
        
        return output 
    
    def update(self):
        """
        This function should be overridden by the subclass. It should set attribute data and return nothing.
        
        update() -> None
        """
        pass
        
    def __str__(self):
        return "<%sPost %s: %s>" % (self._type.capitalize(), self.post_index, str(self._attr))
        
class RegularPost(Post):
    """
    A Post that contains only text.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._critical_keys = ['regular-body']
        self._type = 'regular'
    
    def update(self):
        self._replace_tags = [
            ('{Body}', self._attr['regular-body'])
            ]
        self._conditional_render_blocks = [
            ('Title', 'Title', self._attr.get('regular-title'))
            ]
            

class PhotoPost(Post):
    """
    A Post that has an image and optionally a caption.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'photo'
        self._critical_keys = ['photo-url-500', 'photo-url-400', 'photo-url-250', 'photo-url-100', 'photo-url-75']

    def update(self):
        self._replace_tags = [
            ('{PhotoAlt}', self._attr.get('photo-alt','')),
            ('{PhotoURL-500}', self._attr.get('photo-url-500','')),
            ('{PhotoURL-400}', self._attr.get('photo-url-400','')),
            ('{PhotoURL-250}', self._attr.get('photo-url-250','')),
            ('{PhotoURL-100}', self._attr.get('photo-url-100','')),
            ('{PhotoURL-75sq}', self._attr.get('photo-url-75','')),
            ]
            
        self._conditional_render_blocks = [
            ('Caption', 'Caption', self._attr.get('photo-caption', '')),
            ('HighRes', 'PhotoURL-HighRes', self._attr.get('photo-highres', '')),
            ]
            
    def generate_html(self):
        """
        This post type has a weird way of doing links, so this function handles that.
        
        generate_html() -> str
        """
        output = Post.generate_html(self)
        
        if self._attr.has_key('link'):
            output = replace_several([
            ('{LinkOpenTag}', '<a href="%s">' % self._attr.get('link', '')),
            ('{LinkCloseTag}', '</a>'),
            ('{LinkURL}', self._attr.get('link', ''))
            ], output)
        else:
            output = replace_several([
            ('{LinkOpenTag}', ''),
            ('{LinkCloseTag}', ''),
            ('{LinkURL}', self._attr.get('link', '')),            
            ], output)
            
        return output

class QuotePost(Post):
    """
    A Post that contains a quote and a source.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'quote'
        self._critical_keys = ['quote-text']
        
    def update(self):
        self._replace_tags = [
            ('{Quote}', self._attr.get('quote-text', '')),
            ('{Length}', 'medium'), # this is pretty cheap, but there is no data on what length corresponds to a given classification
            ]
            
        self._conditional_render_blocks = [
            ('Source', 'Source', self._attr.get('quote-source', '')),
            ]

class LinkPost(Post):
    """
    A Post that contains a URL.
    """        
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'link'
        self._critical_keys = ['link-url']
        
    def update(self):
        self._replace_tags = [
            ('{URL}', self._attr.get('link-url', '')),
            ('{Name}', self._attr.get('link-text', self._attr.get('link-url', ''))), # the docs say that if there is no name, use the url
            ('{Target}', 'target="_blank"'),
            ]
            
        self._conditional_render_blocks = [
            ('Description', 'Description', self._attr.get('link-description', '')),
            ]

class ConversationPost(Post):
    """
    A Post that contains dialog between two or more people.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'conversation'
        self._critical_keys = ['conversation', 'conversation-text']
    
    def update(self):
        self._conditional_render_blocks = [
            ('Title', 'Title', self._attr.get('conversaton-title', '')),
            ]
            
    def validate(self):
        """
        This post has a special condition that the chat is not only there, but in list form and with enough people
        
        validate() -> bool
        """
        return Post.validate(self) and within_constraints([
            (type(self._attr['conversation']) == list, '%s has no accessible conversation lines' % str(self)),
            (len(self._attr['conversation']) > 0, '%s does not have enough lines in the conversation' % str(self)),
            ])
        
    def generate_html(self):
        """
        The HTML generation for the conversation is by far the most complex. Comments on lines should help explain
        what is happening.
        
        generate_html() -> str
        """
        output = Post.generate_html(self) # generate the normal stuff
        try:
            # grab the info on how to render a line
            line_rule = re.search(r'{block:Lines}(?P<linerule>.+){/block:Lines}', output, re.DOTALL).group('linerule') 
        except:
            pass
        
        lines_html = ''
        used_usernames = ''
        current_id = 0
        for line in self._attr['conversation']:
            # render the label block
            line_html = render_conditional_block('Label', 'Label', line.get('label', ''), line_rule)
            
            if used_usernames.find(line.get('name', '')) > -1: # set a unique id
                current_id += 1
            else:
                used_usernames += line.get('name', '')
                
            odd_even = ('even') if self._attr['conversation'].index(line) % 2 == 0 else ('odd') # set the css odd/even property
                
            # and finally replace all the data in the line
            line_html = replace_several([ 
                ('{Name}', line.get('name', '')),
                ('{Line}', line.get('phrase', '').replace('\r', '')),
                ('{UserNumber}', str(current_id)),
                ('{Alt}', odd_even)
                ], line_html)
            
            # this is for human readability only
            lines_html += line_html + "\n"
        
        return re.sub(re.compile(r'{block:Lines}.+{/block:Lines}', re.DOTALL) , lines_html, output) # sub in the new data
        
class VideoPost(Post):
    """
    A Post that contains a video. The embed tags can be complicated, but they are mostly insulated from view.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'video'
        self._critical_keys = ['video-player']
        
    def update(self):
        self._replace_tags = [
            ('{Video-500}', re.sub(r'width=\"\d+\"', 'width="500"', self._attr.get('video-player', ''))),
            ('{Video-400}', re.sub(r'width=\"\d+\"', 'width="400"', self._attr.get('video-player', ''))),
            ('{Video-250}', re.sub(r'width=\"\d+\"', 'width="250"', self._attr.get('video-player', ''))),
            ]
            
        self._conditional_render_blocks = [
            ('Caption', 'Caption', self._attr.get('video-caption', '')),
            ]
            
class AudioPost(Post):
    """
    A Post that contains an audio file.
    """
    def __init__(self, post_index, attr, markup):
        Post.__init__(self, post_index, attr, markup)
        self._type = 'audio'
        self._critical_keys = ['audio-player', 'audio-plays']
        
    def update(self):
        self._replace_tags = [
            ('{AudioPlayer}', self._attr.get('audio-player', '')),
            ('{PlayCount}', str(self._attr.get('audio-plays', ''))),
            ('{FormattedPlayCount}', nice_number_formatting(self._attr.get('audio-plays', '')) ),
            ('{AudioPlayerGrey}', re.sub(r'&color=[0-9A-Fa-f]{6}', '&color=EEEEEE', self._attr.get('audio-player', ''))),
            ('{AudioPlayerWhite}', re.sub(r'&color=[0-9A-Fa-f]{6}', '&color=FFFFFF', self._attr.get('audio-player', ''))),
            ('{AudioPlayerBlack}', re.sub(r'&color=[0-9A-Fa-f]{6}', '&color=000000', self._attr.get('audio-player', ''))),
            ]

        self._conditional_render_blocks = [
            ('Caption', 'Caption', self._attr.get('audio-caption', '')),
            ('ExternalAudio', 'ExternalAudioURL', self._attr.get('audio-url'))
            ]