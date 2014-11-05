from google.appengine.ext import ndb

DEFAULT_GUESTBOOK_NAME = 'default_guestbook'

# We set a parent key on the 'Greetings' to ensure that they are all in the same
# entity group. Queries across the single entity group will be consistent.
# However, the write rate should be limited to ~1/second.

def guestbook_key(guestbook_name=DEFAULT_GUESTBOOK_NAME):
    '''Constructs a Datastore key for a Guestbook entity with guestbook_name.'''
    return ndb.Key('Guestbook', guestbook_name)

class Greeting(ndb.Model):
    '''Models an individual Guestbook entry.'''
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)
    
class Market(ndb.Model):
    '''Models an individual Market entry.'''
    name = ndb.StringProperty(required = True)
    address = ndb.StringProperty(required = True)
    num_vendors = ndb.StringProperty(required = True)
    market_type = ndb.StringProperty(required = True)
    organization = ndb.StringProperty()
    url = ndb.StringProperty(required = True)
    products = ndb.StringProperty(required = True)
    open_day = ndb.StringProperty(required = True)
    open_month = ndb.StringProperty(required = True)
    open_time = ndb.StringProperty(required = True)
    close_time = ndb.StringProperty(required = True)
    open_month_int = ndb.IntegerProperty(required = True)
    close_month_int = ndb.IntegerProperty(required = True)
    open_time_int = ndb.IntegerProperty(required = True)
    close_time_int = ndb.IntegerProperty(required = True)
    