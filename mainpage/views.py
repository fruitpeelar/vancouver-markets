from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from django.template import Context, loader

from google.appengine.api import users

from mainpage.models import Market, Comment, User, Update
from mainpage.parser import MarketParser

from datetime import date, timedelta

# renders the main_page.html upon request
def main_page(request):
    
    markets, markets_open, markets_closed, markets_upcoming = get_markets()
    print markets
    print markets_open
    print markets_closed

    if users.get_current_user():
        url = users.create_logout_url(request.get_full_path())
        url_linktext = ' Sign out of Google'
        curret_user = users.get_current_user()
        user = check_user(curret_user)
        print "got user in mainpage"
        print user
        markets_favourite = view_favourite(request, user)
        print "got favourite markets in mainpage"
        print markets_favourite
    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = ' Sign in with Google'
        markets_favourite = None

    template_values = {
        'url': url,
        'url_linktext': url_linktext,
        'markets': markets,
        'markets_open': markets_open,
        'markets_closed': markets_closed,
        'markets_upcoming': markets_upcoming,
        'markets_favourite': markets_favourite,
    }
    return render(request, 'mainpage/main_page.html', template_values)

# renders detail page of a selected market given market's id
@csrf_exempt
def view_detail(request, market_id = None, is_inner = False):
    market = Market.get_by_id(int(market_id))
        
    template_values = {'market': market,
                       }
    if is_inner:
        template = loader.get_template('mainpage/detail.html')
        context = Context({'market': market})
        return template.render(context)
    else:
        if request.is_ajax():
            template_values['with_layout'] = False
        else:
            template_values['with_layout'] = True
        return render(request, 'mainpage/detail.html', template_values)

# create stub market upon request
def market_put(request):
    if request.method == 'POST':
        create_marketstub()
        
    return HttpResponseRedirect('/')

# populate the database with real data upon request
def populate(request):
    if request.method == 'POST':
        populate_markets()
        return HttpResponseRedirect('/')
    
    if request.method == 'GET':
        return render (request, 'mainpage/populate.html')

# add comment to a market
def add_comment(request):
    if request.POST.has_key('content') == False:
        return HttpResponse('You must have content.')
    else:
        if len(request.POST['content']) == 0:
            return HttpResponse('You must write content')
        else:
            comment_content = request.POST['content']
    
    if request.POST.has_key('market_id') == False:
        return HttpResponse('You must select a market to comment on.')
    else:
        try:
            received_id = int(request.POST['market_id'])
            market = Market.get_by_id(received_id)
            existing_comments = market.comments
        except:
            return HttpResponse('No market by that id.')

    try:
        comment = Comment(content = comment_content)
        comment.put()
        print comment
        if len(existing_comments) == 0:
            market.comments = [comment]
            market.put()
        else:
            existing_comments.append(comment)
            market.comments = existing_comments
            market.put()
        
        if request.is_ajax():
            return_data = {'msg': view_detail(request, received_id, True)}
            return HttpResponse(simplejson.dumps(return_data))
        else:
            return HttpResponse('Successfully added your comment.')
    except:
        return HttpResponse('Failed adding your comment.')
    
    return HttpResponse('Something wrong happened.')
    
def add_favourite(request):
    if request.method == 'POST':
        current_user = users.get_current_user()
        market_id = request.POST['market_id']
        market_key = Market.get_by_id(int(market_id)).key
        print "we got current user: "
        print current_user
        
        user = check_user(current_user)
        
        if len(user.favourites) == 0:
            user.favourites = [market_key]
            user.put()
        else:
            if not market_key in user.favourites:
                user.favourites.append(market_key)
                user.put()
            
        if request.is_ajax():
            return_data = {'msg': view_favourite(request, user)}
            return HttpResponse(simplejson.dumps(return_data))
        else:
            return HttpResponse('Successfully added to your favourites.')
    else:
        return HttpResponse('Failed to add to your favourites.')
    
def delete_favourite(request):
    if request.method == 'POST':
        current_user = users.get_current_user()
        market_id = request.POST['market_id']
        market_key = Market.get_by_id(int(market_id)).key
        print "we got current user in delete: "
        print current_user
        
        user = check_user(current_user)
        user.favourites.remove(market_key)
        user.put()
        
        if request.is_ajax():
            return_data = {'msg': view_favourite(request, user)}
            return HttpResponse(simplejson.dumps(return_data))
        else:
            return HttpResponse('Successfully deleted from your favourites.')
    else:
        return HttpResponse('Failed to delete from your favourites.')


def view_favourite(request, user=None):
    markets_favourite = []
    if user:
        for market_id in user.favourites:
            markets_favourite.append(market_id.get())
            
        if request.is_ajax():
            template = loader.get_template('mainpage/favourite_tab.html')
            context = Context({'markets_favourite': markets_favourite})
            return template.render(context)
        else:
            return markets_favourite
    else:
        return None
        
def check_user(current_user):
    if current_user:
        user_query = User.query(User.username == current_user)
        user = user_query.get()
        print user_query
        print user
        if user == None:
            user = User(username = current_user)
            print "created a new user"
    return user
# not in use right now
# def get_details(request):
#     print "in get_details"
#     market = None
#     if request.method == 'GET':
#         try:
#             print "it is get"
#             received_id = request.GET['market_id']
#             print received_id
#             market = Market.get_by_id(int(received_id))
#             print "market created"
#         except:
#             print "in excpetion"
#             return HttpResponse("no market by the given id")
#     template_values = {'market': market,
#                        }
#     return render(request, 'mainpage/detail.html', template_values)

# (helper) create a stub market and put it into the database
def create_marketstub():
    market = Market(name = 'This Market Name Is This Market',
                    address = 'Address of this Market',
                    lat = 49.287092,                       #added currentLocation as stub
                    lon = -123.117703,                     #lat/lon
                    num_vendors = '5',
                    market_type = 'No Type',
                    organization = 'No Org',
                    url = 'no url',
                    products = 'this, that, it',
                    open_day = 'Monday',
                    open_month = '6-8',
                    open_time = '2pm',
                    close_time = '6pm',
                    open_month_int = 6,
                    close_month_int = 8,
                    open_time_int = 14,
                    close_time_int = 16)
    market.put()

'''
Check if a week has passed since last update and return boolean
'''
def updateTime():
    # Compare time: set to 2014/11/05/ 00AM as reference
    # If last updated time is not present, then set compareDate as given otherwise use last updated time
    update_record = get_update()
    
    if update_record == None:
        update_record = Update(update_count = 1)
        print "Update created!"
        print update_record.last_update
        return True
    else:
        last_update = update_record.last_update
        
        now = date.today()
        diff = now - timedelta(days=7)
             
        # if difference in time is greater than 7 days, then return true, else false
        if (diff > last_update):
            # Update the last updated time with current time
            update_record.last_update = now
            update_record.put()
            return True
        else:
            return False

# (helper) populate the database with real market data
def populate_markets():
    print 'in pop market'
    
    url = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
    # if(updateTime(late_update)):
    market_dict = MarketParser(url).ParseMarkets()
    
    # put returned values to the corresponding variables
    names = market_dict['names']
    types = market_dict['types']
    organizations = market_dict['organizations']
    addresses = market_dict['addresses']
    urls = market_dict['urls']
    open_days = market_dict['open_days']
    open_times = market_dict['open_times']
    close_times = market_dict['close_times']
    open_months = market_dict['open_months']
    vendors = market_dict['vendors']
    offerings = market_dict['offerings']
    open_times_ints = market_dict['open_time_ints']
    close_time_ints = market_dict['close_time_ints']
    open_month_ints = market_dict['open_month_ints']
    close_month_ints = market_dict['close_month_ints']
    lats = market_dict['lats']       #added lat/lon 
    lons = market_dict['lons']
    print len(names)
    
    # put market data into the database
    for x in range (0, len(names)):
        
        market = Market(name = names[x],
                    address = addresses[x],
                    num_vendors = vendors[x],
                    market_type = types[x],
                    organization = organizations[x],
                    url = urls[x],
                    products = offerings[x],
                    open_day = open_days[x],
                    open_month = open_months[x],
                    open_time = open_times[x],
                    close_time = close_times[x],
                    open_month_int = open_month_ints[x],
                    close_month_int = close_month_ints[x],
                    open_time_int = open_times_ints[x],
                    close_time_int = close_time_ints[x],
                    lat = lats[x],                  #added lat/lon for each market
                    lon = lons[x])
        market.put()

    print market_dict

# (helper) organize markets into four categories
def get_markets():
    
    today = date.today()
    current_month = today.month
    
    #all markets - ordered by name
    markets_query = Market.query().order(Market.name)
    #open markets - ordered by open month
    markets_open_query = Market.query(Market.open_month_int <= current_month).order(Market.open_month_int)
    #closed markets - ordered by close month
    markets_closed_query = Market.query(Market.close_month_int < current_month).order(Market.close_month_int)
    #upcoming markets - ordered by open month
    markets_upcoming_query = Market.query(Market.open_month_int < current_month + 2).order(Market.open_month_int)
    
    markets = markets_query.fetch()
    markets_open = markets_open_query.fetch()
    markets_closed = markets_closed_query.fetch()
    markets_upcoming = markets_upcoming_query.fetch()
    
    markets_open[:] = [market for market in markets_open if current_month <= market.close_month_int]
    markets_upcoming[:] = [market for market in markets_upcoming if current_month < market.open_month_int]
    
    return markets, markets_open, markets_closed, markets_upcoming

# retrieve the Update entity, always have only one Update entity
def get_update():
    return Update.query().get()
    