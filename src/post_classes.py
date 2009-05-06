###
#   post_classes.py
###

# types of posts
#
# text, photo, quote, link, chat, audio, video
import sys, re, pdb

def within_constraints(constraints):
    return_val = True
    for outcome, message in constraints:
        if not outcome:
            print "An error occurred: " + str(message)
            return_val = False
    return return_val
    
def has_keys(dict_to_check, keys):
    return reduce(lambda x,y: x and dict_to_check.has_key(y), keys, True)

def replace_several(replacements, instring):
    outstring = instring
    for to_replace, replacement in replacements:
        outstring = outstring.replace(str(to_replace), str(replacement))
    return outstring
    
def render_block_if(block_name, tag, contents, instring):
    if contents:
           return replace_several([
               ('{block:%s}' % block_name, ''), 
               ('{/block:%s}' % block_name, ''), 
               ('{%s}' % tag, contents),
               ], instring)
    else:
           return re.sub(r'{block:%s}.+{/block:%s}' % (block_name, block_name), '', instring)

class Post(object):
    def __init__(self, post_index, attr, markup):
        self._attr = attr
        self._markup = markup
        self.post_index = post_index
        self._critical_keys = []
    
    def validate(self):
        try:
            return within_constraints([
                (type(self._attr) == dict, '%s was not able to access its attributes' % str(self)),
                (has_keys(self._attr, ['url', 'type', 'date-gmt', 'date', 'unix-timestamp', 'id']), '%s is missing a critical key' % str(self)),
                (self._attr['format'] == 'html', '%s has an incorrect format' % str(self)),
                
                (has_keys(self._attr, self._critical_keys), '%s is missing a critical attribute key' % str(self)),
                (self._attr['type'] == self._type, '%s has an incorrect type' % (self._type) ),
                ])
        except Exception, detail:
            print "An error occurred: The validation code failed\n" + str(self) + str(detail)
            return False
            
    def generate_html(self):
        return replace_several([
            ('{Permalink}', self._attr['url']),
            ('{PostID}', self._attr['id']),
            ], self._markup)
        
    def __str__(self):
        return "<%sPost %s: %s>" % (self._type.capitalize(), self.post_index, str(self._attr))
        
class TextPost(Post):        
    def __init__(self, post_index, attr, markup):
        self._type = 'regular'
        self._critical_keys = ['regular-body']
        Post.__init__(self, post_index, attr, markup)
            
    def generate_html(self):
        if not self.validate(): return ''
        
        output = Post.generate_html(self)
        output = render_block_if('Title', 'Title', self._attr.get('regular-title', ''), output)
        
        output = replace_several([
            ('{Body}', self._attr['regular-body']),
            ], output)
            
        return output

class PhotoPost(Post):        
    def __init__(self, post_index, attr, markup):
        self._type = 'photo'
        self._critical_keys = ['photo-url-500', 'photo-url-400', 'photo-url-250', 'photo-url-100', 'photo-url-75']
        Post.__init__(self, post_index, attr, markup)
            
    def generate_html(self):
        if not self.validate(): return ''
        
        output = Post.generate_html(self)
        output = render_block_if('Caption', 'Caption', self._attr.get('photo-caption', ''), output)
        output = render_block_if('HighRes', 'PhotoURL-HighRes', self._attr.get('photo-highres', ''), output)
        
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
            
        output = replace_several([
            ('{PhotoAlt}', self._attr.get('photo-alt','')),
            ('{PhotoURL-500}', self._attr.get('photo-url-500','')),
            ('{PhotoURL-400}', self._attr.get('photo-url-400','')),
            ('{PhotoURL-250}', self._attr.get('photo-url-250','')),
            ('{PhotoURL-100}', self._attr.get('photo-url-100','')),
            ('{PhotoURL-75sq}', self._attr.get('photo-url-75','')),
            ], output)
            
        return output

class QuotePost(Post):
    def __init__(self, post_index, attr, markup):
        self._type = 'quote'
        self._critical_keys = ['quote']
        Post.__init__(self, post_index, attr, markup)
            
    def generate_html(self):
        if not self.validate(): return ''
        
        output = Post.generate_html(self)
        output = render_block_if('Source', 'Source', self._attr.get('quote-source', ''), output)
        
        output = replace_several([
            ('{Quote}', self._attr.get('quote-text', '')),
            ('{Length}', 'medium'), # this is cheap, but no one actually uses this so it doesn't matter
            ], output)
            
        return output

class LinkPost(Post):        
    def __init__(self, post_index, attr, markup):
        self._type = 'link'
        self._critical_keys = ['URL']
        Post.__init__(self, post_index, attr, markup)
        
    def generate_html(self):
        if not self.validate(): return ''
        
        output = Post.generate_html(self)
        output = render_block_if('Source', 'Source', self._attr.get('quote-source', ''), output)
        
        output = replace_several([
            ('{Quote}', self._attr.get('quote-text', '')),
            ('{Length}', 'medium'), # this is cheap, but no one actually uses this so it doesn't matter
            ], output)
            
        return output

class ChatPost(Post):        
    def __init__(self, post_index, attr, markup):
        self._type = 'chat'
        self._critical_keys = ['URL']
        Post.__init__(self, post_index, attr, markup)

    def generate_html(self):
        if not self.validate(): return ''

        output = Post.generate_html(self)
        output = render_block_if('Source', 'Source', self._attr.get('quote-source', ''), output)

        output = replace_several([
            ('{Quote}', self._attr.get('quote-text', '')),
            ('{Length}', 'medium'), # this is cheap, but no one actually uses this so it doesn't matter
            ], output)

        return output