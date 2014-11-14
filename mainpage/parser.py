import csv
import urllib2
import re
import time
import json
# from pip.basecommand import open_logfile

class MarketParser:
    def __init__(self, url):
        response = urllib2.urlopen(url)
        time.sleep(2)
        self.cr = csv.reader(response, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True) 
               
    # Retrieve CSV file from the Vancouver OpenData url
    def getCSV(self): 
        return self.cr

    # First row has the last updated time of this data
    def getUpdateRow(self, cr):
        return cr.next()

    # Remove the row with field names
    def removeFieldNames(self, cr):
        return cr.next()

    # If the field is empty, then return the list with empty field filled as 'N/A'
    def checkEmpty(self, fieldlist):
        checkedOfferings = []
        for field in fieldlist:
            if(not field):
                field = 'N/A'
            checkedOfferings.append(field)
        return checkedOfferings

    # If the stored date of the updated date is different than the current date, then parse the information again
    def checkUpdate(self, cr, storeddate, updatedate, i):
        if(storeddate != updatedate):
            return self.parseMarketInfo(self, cr)
            # Keep how many updates have happened
            i += 1
    
    # Get updated date from the first row of the csv file
    def getUpdateDate(self, updaterow):
        return updaterow[1]
    
    # Geocode address string to get google maps 
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
        
    # Parses the required market information into the corresponding lists
    def parseMarketInfo(self, cr, lastUpdateDate, updatedate, updateCount):
        # Check if updated date has changed
        if (lastUpdateDate != updatedate):
            # Increment update count
            updateCount += 1
            
            # Change last update time to the newly changed date
            lastUpdateDate = updatedate
            
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
            checkedOfferings = []
            lats = []
            lons = []
            
            for row in cr:
                # Only iterate and parse when the name field is not empty
                if row[1] != '':
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
            checkedOfferings = self.checkEmpty(offerings)
            
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
                    'offerings': checkedOfferings,
                    'open_time_ints': open_time_ints,
                    'close_time_ints': close_time_ints,
                    'open_month_ints': open_month_ints,
                    'close_month_ints': close_month_ints,
                    'lats': lats,
                    'lons': lons
                    }
      
    # Splice the OpenMonths into the month it opens and the month it closes     
    def getOpenCloseMonths(self, monthlist):
        openMonths = []
        closeMonths = []

        # Create dictionary that maps Month to the corresponding integer
        monthDict = {
                     'January':1, 'February':2, 'March':3,
                     'April':4, 'May':5, 'June':6,
                     'July':7, 'August':8, 'September':9,
                     'October':10, 'November':11, 'December':12
                     }
    
        # Split the month range, which is given as: Month1-Month2, at hyphen
        for monthrange in monthlist:
            months = re.split(r'-', ''.join(monthrange))
            # Use the monthDict and get corresponding integer value of the opening and closing months
            if months[0].strip() in monthDict:
                openMonths.append(monthDict.get(months[0].strip()))
                closeMonths.append(monthDict.get(months[1].strip()))
            # Handle Yaletown Farmer's market case (Mid-August to September)
            else:
                openMonths.append(monthDict.get(months[1].split()[0]))
                closeMonths.append(monthDict.get(months[1].split()[2]))
        return openMonths, closeMonths

    # Convert the open and close time of the markets
    def convertTimeTo24Hr(self, timelist):
        market24Time = []
        # Iterate all the times given in the timelist
        for twelvetime in timelist:
            # Convert list to string
            stringTime = ''.join(twelvetime)
        
            # Take off am and pm and convert time to int
            ampmtime = re.findall(r'\d+', twelvetime) 
            ampmtime = int(''.join(ampmtime))
            
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
        return market24Time 
    
    # TESTING UPDATE
    testingdate = " "
    numUpdate = 0
    
    # Testing
    def testRun(self):
        cr = self.getCSV()
        updateRow = self.getUpdateRow(cr)
        updateDate = self.getUpdateDate(updateRow)
        self.removeFieldNames(cr)
        return self.parseMarketInfo(cr, self.testingdate, updateDate, self.numUpdate)
