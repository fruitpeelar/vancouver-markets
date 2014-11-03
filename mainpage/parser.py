import csv
import urllib2
import re
# from pip.basecommand import open_logfile

# Retrieve CSV file from the Vancouver OpenData url
def getCSV(): 
    url = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
    response = urllib2.urlopen(url)
    cr = csv.reader(response, quotechar='"', delimiter=',',
                     quoting=csv.QUOTE_ALL, skipinitialspace=True)
    return cr

# First row has the last updated time of this data       
def getUpdateRow(cr):
    return cr.next()

# Remove the row with field names
def removeFieldNames(cr):
    return cr.next()

# If the field is empty, then return the list with empty field filled as 'N/A'
def checkEmpty(fieldlist):
    for field in fieldlist:
        if(field == ''):
            field = 'N/A'
    return fieldlist

# If the stored date of the updated date is different than the current date, then parse the information again
def checkUpdate(cr, storeddate, updatedate):
    if(storeddate != updatedate):
        parseMarketInfo(cr)
        
# Convert the open and close time of the markets
def convertTimeTo24Hr(timelist):
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

# Splice the OpenMonths into the month it opens and the month it closes
def getOpenCloseMonths(monthlist):
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

# Get updated date from the first row of the csv file
def getUpdateDate(updaterow):
    return updaterow[1]

# Parses the required market information into the corresponding lists
def parseMarketInfo(cr):
    
    # Create lists to store market info
    names = []
    types = []
    organizations = []
    addresses = []
    websites = []
    open_days = []
    open_times = []
    close_times = []
    open_month_ints = []
    vendor_numbers = []
    offerings = []
    
    # Remove field title row
    # exception here please fix
    cr.next()
    
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
            open_month_ints.append(row[13])
            vendor_numbers.append(row[14])
            offerings.append(row[15])
    
    # Retrieved parsed information    
    open_time_ints = convertTimeTo24Hr(open_times)
    close_time_ints = convertTimeTo24Hr(close_times)
    open_month_ints, close_month_ints = getOpenCloseMonths(open_month_ints)
    
    # Check if there are empty fields
    checkEmpty(offerings)
    
    # This is used as a test to check if info are getting parsed correctly
    
    return {'names':names,
        'types':types,
        'organizations': organizations,
        'addresses': addresses,
        'urls': websites,
        'open_days': open_days,
        'open_times': open_times,
        'close_times': close_times,
        'open_months': open_month_ints,
        'vendors': vendor_numbers,
        'offerings': offerings,
        'open_time_ints': open_time_ints,
        'close_time_ints': close_time_ints,
        'open_month_ints': open_month_ints,
        'close_month_ints': close_month_ints
        }

# Testing
def testRun():
    cr = getCSV()
    updateRow = getUpdateRow(cr)
    getUpdateDate(updateRow)
    removeFieldNames(cr)
    return parseMarketInfo(cr)
    
testRun()