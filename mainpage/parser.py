import csv
import urllib2
import re
import time
import json
import datetime
from datetime import date, timedelta
# from pip.basecommand import open_logfile

class MarketParser:
    def __init__(self, url):
        # Initialize the class by getting the csv file from Vancouver database
        response = urllib2.Request(url)
        try:
            print "initialize using: " and url
            result = urllib2.urlopen(response, timeout=10)
            time.sleep(3)
            self.cr = csv.reader(result, quotechar='"', delimiter=',',
            quoting=csv.QUOTE_ALL, skipinitialspace=True)
        except Exception:
            print "Fatal Error!"
    
    '''           
    Retrieve CSV file from the Vancouver OpenData url
    '''
    def getCSV(self):
        try:
            return self.cr
        except Exception:
            print "CSV file not present!"
    
    '''            
    Remove first row with update time and second row with fieldnames
    '''
    def removeUpdateRowandFieldNames(self, cr):
        cr.next()
        return cr.next()

    '''
    If the field is empty, then return the list with empty field filled as 'N/A'
    '''
    def checkEmpty(self, fieldlist):
        emptyCheckedList = []
        for field in fieldlist:
            if(not field):
                field = 'N/A'
            emptyCheckedList.append(field)
        return emptyCheckedList
    
    '''
    Geocode address string to get google maps 
    '''
    def geocodeMarket(self, listOflat, listOflon, address):
        #take address string and geocode it into a json object
        addressString = address + ", Vancouver, B.C."
        addressString = urllib2.quote(addressString)
        url="https://maps.googleapis.com/maps/api/geocode/json?address=%s" % addressString

        response = urllib2.urlopen(url)
        jsongeocode = json.loads(response.read())
                    
        #parse json to extract lat/lon
        lat = jsongeocode['results'][0]['geometry']['location']['lat']
        lon = jsongeocode['results'][0]['geometry']['location']['lng']
        #append lat/lon to lists    
        listOflat.append(lat)
        listOflon.append(lon)
    
    '''
    Precond: cr is not None
    Assumption: the csv file from the vancouver db is consistent in its format
    Parses the required market information into the corresponding lists
    '''
    def parseMarketInfo(self, cr):
        # Create lists to store market info
        names = []
        types = []
        organizations = []
        addresses = []
        websites = []
        open_days = []
        open_times = []
        close_times = []
        open_months = []
        vendor_numbers = []
        offerings = []
        lats = []
        lons = []
            
        for row in cr:
            # Only iterate and parse when the name field is not empty
            # Assumption: if market data is filled out, then name must be always present
            if row[1] != None:
                names.append(row[1])
                types.append(row[0])
                organizations.append(row[2])
                addresses.append(row[7])
                websites.append(row[9])
                open_days.append(row[10])
                open_times.append(row[11])
                close_times.append(row[12])
                open_months.append(row[13])
                vendor_numbers.append(row[14])
                offerings.append(row[15])
                # Geocode address string into lat/lon and put into lats/lons list
                self.geocodeMarket(lats, lons, row[7])
                
        # Check if there are empty fields and change empty fields to N/A
        offerings = self.checkEmpty(offerings)
        vendor_numbers = self.checkEmpty(vendor_numbers)
        types = self.checkEmpty(types)
        organizations = self.checkEmpty(organizations)
        addresses = self.checkEmpty(addresses)
        websites = self.checkEmpty(websites)
        open_days = self.checkEmpty(open_days)
        open_times = self.checkEmpty(open_times)
        close_times = self.checkEmpty(close_times)
        open_months = self.checkEmpty(open_months)
            
        # Retrieved parsed information    
        open_time_ints = self.convertTimeTo24Hr(open_times)
        close_time_ints = self.convertTimeTo24Hr(close_times)
        open_month_ints, close_month_ints = self.getOpenCloseMonths(open_months)
            
        # This is used as a test to check if info are getting parsed correctly
        return {'names':names,
                'types':types,
                'organizations': organizations,
                'addresses': addresses,
                'urls': websites,
                'open_days': open_days,
                'open_times': open_times,
                'close_times': close_times,
                'open_months': open_months,
                'vendors': vendor_numbers,
                'offerings': offerings,
                'open_time_ints': open_time_ints,
                'close_time_ints': close_time_ints,
                'open_month_ints': open_month_ints,
                'close_month_ints': close_month_ints,
                'lats': lats,
                'lons': lons
                }
    
    '''  
    Splice the OpenMonths into the month it opens and the month it closes   
    '''  
    def getOpenCloseMonths(self, monthlist):
        openMonths = []
        closeMonths = []

        # Create dictionary that maps Month to the corresponding integer
        monthDict = {
                     'january':1, 'jan':1, 'february':2, 'feb':2, 'march':3, 'mar':3,
                    'april':4, 'apr':4, 'may':5, 'june':6, 'jun':6,
                    'july':7, 'jul':7, 'august':8, 'aug':8, 'september':9, 'sep':9,
                    'october':10, 'oct':10, 'november':11, 'nov':11, 'december':12, 'dec':12
                    }
    
        # Split the month range at '- or to'
        for monthrange in monthlist:
            months = re.split(r'-|to', ''.join(monthrange))
            refinedMonthRange = []
            # Use the monthDict and get corresponding integer value of the opening and closing months
            for month in months:
                if(month.strip().lower() in monthDict):
                    intMonth = monthDict.get(month.strip().lower())
                    refinedMonthRange.append(intMonth)
            # Divide opening months and closing months and make new lists for each of them
            if refinedMonthRange:
                openMonths.append(refinedMonthRange[0])
                closeMonths.append(refinedMonthRange[1])
        return openMonths, closeMonths

    '''
    Convert the open and close time of the markets
    '''
    def convertTimeTo24Hr(self, timelist):
        market24Time = []
        # Iterate all the times given in the timelist
        for twelvetime in timelist:
            # Convert list to string
            stringTime = ''.join(twelvetime).lower()
        
            # Take off am and pm and convert time to int
            try:
                ampmtime = re.findall(r'\d+', twelvetime) 
                ampmtime = int(''.join(ampmtime))
                # Check if time(in am-pm style) is valid (between 0-12)
                if (ampmtime >= 0 and ampmtime <= 12):
                    # 12pm = 1200
                    if(ampmtime == 12 and re.search('pm', stringTime)):
                        ampmtime = 12
                    # 12am = 0000
                    elif(ampmtime == 12 and re.search('am', stringTime)):
                        ampmtime = 0
                    # all other pm = time + 12
                    elif re.search('pm', stringTime):
                        ampmtime = ampmtime + 12
                        # otherwise am time stays the same
                        # Add the converted time to the new list and return the list
                    market24Time.append(ampmtime)
            # if string cannot be converted to integer(wrong data) then move to next item
            except:
                continue
        return market24Time 
     
    '''
    Merge all the parsing and retrieve the info
    '''
    def ParseMarkets(self):
        cr = self.getCSV()
        self.removeUpdateRowandFieldNames(cr)
        return self.parseMarketInfo(cr)
