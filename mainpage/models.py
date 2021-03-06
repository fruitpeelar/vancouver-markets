from google.appengine.ext import ndb

class Comment(ndb.Model):
    '''Models an individual Comment.'''
    content = ndb.TextProperty(required = True)
    author = ndb.UserProperty()
    date = ndb.DateTimeProperty(auto_now_add = True)
   
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
    lat = ndb.FloatProperty(required = True)     #added lat/lon properties
    lon = ndb.FloatProperty(required = True)
    comments = ndb.StructuredProperty(Comment, repeated = True)
    
class User(ndb.Model):
    username = ndb.UserProperty(required = True)
    favourites = ndb.KeyProperty(kind=Market, repeated = True)
    
class Update(ndb.Model):
    last_update = ndb.DateProperty(auto_now_add = True)
    update_count = ndb.IntegerProperty(required = True)

# class Update_Date(ndb.model):
#     '''Models a update property entry.'''
#     lastUpdateDate = ndb.StringProperty(required = True)
#     updateCount = ndb.IntegerProperty(required = True)
    