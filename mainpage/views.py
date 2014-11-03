from django.http import HttpResponseRedirect
#from django.views.generic.simple import direct_to_template
from django.shortcuts import render

from google.appengine.api import users

from mainpage.models import Greeting, guestbook_key, DEFAULT_GUESTBOOK_NAME, Market
from mainpage.parser import MarketParser

from datetime import date

import urllib

def main_page(request):
    guestbook_name = request.GET.get('guestbook_name', DEFAULT_GUESTBOOK_NAME)
    
    # Ancestor Queries, as shown here, are strongly consistent with the High
    # Replication Datastore. Queries that span entity groups are eventually
    # consistent. If we omitted the ancestor from this query there would be
    # a slight chance that Greeting that had just been written would not
    # show up in a query.
    greetings_query = Greeting.query(ancestor=guestbook_key(guestbook_name)).order(-Greeting.date)
    greetings = greetings_query.fetch(10)
    
    today = date.today()
    current_month = today.month
    
    markets_query = Market.query()
    markets_open_query = Market.query(Market.open_month <= current_month)
    markets_closed_query = markets_query.filter(Market.close_month < current_month)
    markets_upcoming_query = markets_query.filter(Market.open_month > current_month)
    
    markets = markets_query.fetch()
    markets_open = markets_open_query.fetch()
    markets_closed = markets_closed_query.fetch()
    markets_upcoming = markets_upcoming_query.fetch()
    
    print 'start'
    populate_markets()
    markets_open[:] = [market for market in markets_open if current_month <= market.close_month]
    print markets_closed

    if users.get_current_user():
        url = users.create_logout_url(request.get_full_path())
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(request.get_full_path())
        url_linktext = 'Login'

    template_values = {
        'greetings': greetings,
        'guestbook_name': guestbook_name,
        'url': url,
        'url_linktext': url_linktext,
        'markets': markets,
        'markets_open': markets_open,
        'markets_closed': markets_closed,
        'markets_upcoming': markets_upcoming,
    }
    #return direct_to_template(request, 'guestbook/main_page.html', template_values)
    return render(request, 'mainpage/main_page.html', template_values)

def sign_post(request):
    if request.method == 'POST':
        guestbook_name = request.POST.get('guestbook_name')
        greeting = Greeting(parent=guestbook_key(guestbook_name))
    
        if users.get_current_user():
            greeting.author = users.get_current_user()
    
        greeting.content = request.POST.get('content')
        greeting.put()
        return HttpResponseRedirect('/?' + urllib.urlencode({'guestbook_name': guestbook_name}))
    return HttpResponseRedirect('/')

def view_detail(request):
    if request.method == 'POST':
       return 
    template_values = {'id': id,
                       }
    
    return render(request, 'mainpage/detail.html', template_values)

def create_marketstub():
    market = Market(name = 'This Market Name Is This Market',
                    address = 'Address of this Market',
                    num_vendors = '5',
                    market_type = 'No Type',
                    organization = 'No Org',
                    url = 'no url',
                    products = ['this', 'that', 'it'],
                    open_day = 'Monday',
                    open_month_string = '6-8',
                    open_time_string = '2pm - 4pm',
                    open_month = 6,
                    close_month = 8,
                    open_time = 14,
                    close_time = 16)
    market.put()
    
def populate_markets():
    print 'in pop market'
    url = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
    market_dict = MarketParser(url).testRun()
    names = market_dict['names']   
       
    names = market_dict['names']
    organizations = market_dict['organizations']
    addresses = market_dict['addresses']
         
    print names
    print organizations
    print addresses
    
    
def market_put(request):
    if request.method == 'POST':
        create_marketstub()
        
    return HttpResponseRedirect('/')
    