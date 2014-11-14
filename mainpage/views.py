from django.http import HttpResponseRedirect
#from django.views.generic.simple import direct_to_template
from django.shortcuts import render

from google.appengine.api import users
# from googlemaps import GoogleMaps

from mainpage.models import Market
from mainpage.parser import MarketParser

from datetime import date

# api_key = "AIzaSyAWLMNHOpkHQnyBKZdjyzA_22R20VZ36_E"
# gmaps = GoogleMaps(api_key)

# renders the main_page.html upon request
def main_page(request):
    
    markets, markets_open, markets_closed, markets_upcoming = get_markets()
    print markets
    print markets_open
    print markets_closed

    if users.get_current_user():
        url = users.create_logout_url(request.get_full_path())
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = 'Login'

    template_values = {
        'url': url,
        'url_linktext': url_linktext,
        'markets': markets,
        'markets_open': markets_open,
        'markets_closed': markets_closed,
        'markets_upcoming': markets_upcoming,
    }
    return render(request, 'mainpage/main_page.html', template_values)

# renders detail page of a selected market given market's id
def view_detail(request, detail):
    id_int = int(detail)
    markets, markets_open, markets_closed, markets_upcoming = get_markets()

    if request.method == 'GET':
        market = Market.get_by_id(id_int)
        
    template_values = {'market': market,
                       'markets': markets,
                       'markets_open': markets_open,
                       'markets_closed': markets_closed,
                       'markets_upcoming': markets_upcoming,}
    
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

# (helper) populate the database with real market data
def populate_markets():
    print 'in pop market'
    
    url = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
    market_dict = MarketParser(url).testRun()
    
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
    
    markets_query = Market.query()
    markets_open_query = Market.query(Market.open_month_int <= current_month)
    markets_closed_query = markets_query.filter(Market.close_month_int < current_month)
    markets_upcoming_query = markets_query.filter(Market.open_month_int > current_month)
    
    markets = markets_query.fetch()
    markets_open = markets_open_query.fetch()
    markets_closed = markets_closed_query.fetch()
    markets_upcoming = markets_upcoming_query.fetch()
    
    markets_open[:] = [market for market in markets_open if current_month <= market.close_month_int]
    
    return markets, markets_open, markets_closed, markets_upcoming
    
