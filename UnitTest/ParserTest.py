'''
Created on Nov 26, 2014
UnitTest for MarketParser
@author: JunOh Park
'''

from mainpage.parser import MarketParser
import unittest
import csv

class TestParser(unittest.TestCase):
    '''
    setUp is always run before each test function
    '''
    def setUp(self):
        # URL to check what happens when incorrect URL is given
        self.url = 'Wrong URL'
        # Correct URL of Vancouver database
        self.url2 = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
        # Test csv file pathway
        self.url3 = 'file:///Users/JunOh/git/KingSejong/UnitTest/testline.csv'
    
    '''
    Test if retrieving csv file is working correctly comparing test CSV file retreived from getCSV
    function with actually opening the test file with csv.reader
    '''
    def test_getCSV(self):
        mp = MarketParser(self.url3)
        with open('testline.csv') as csvfile:
            testline = csv.reader(csvfile, quotechar='"', delimiter=',',
            quoting=csv.QUOTE_ALL, skipinitialspace=True)
            # Test all 3 lines of the test file
            self.assertEqual(testline.next(), mp.getCSV().next())
            self.assertEqual(testline.next(), mp.getCSV().next())
            self.assertEqual(testline.next(), mp.getCSV().next())
        # Test if giving incorrect URL raises Exception
        self.assertRaises(Exception, MarketParser(self.url).getCSV())
    
    '''
    Test if empty fields are correctly field with 'N/A'
    '''
    def test_checkEmpty(self):
        mp = MarketParser(self.url2)
        # Simple test case for empty fields
        fieldlist = ["",'','emptycheck']
        self.assertEqual(mp.checkEmpty(fieldlist), ['N/A','N/A','emptycheck'])
    
    '''
    Test if months are correctly changed to corresponding int value
    and put into opening or closing months lists
    '''
    def test_getOpenCloseMonths(self):
        mp = MarketParser(self.url2)
        # Simple test case for getting opening months and closing months in int value
        monthslist = ['Jan-Feb', 'Jan to Feb', 'Mid-Jan to Feb', 'not months', 'AUGUST - JANUARy']
        self.assertEqual(mp.getOpenCloseMonths(monthslist), ([1,1,1,8], [2,2,2,1]))
    
    '''
    Test if converting time in 12 hour format is correctly translated to 24 hour format
    '''
    def test_convertTimeTo24Hr(self):
        mp = MarketParser(self.url2)
        # Test case that test cases that are not correct time, not a time value at all, or correct time
        timelist = ['N/A', '1am', '2AM', '3am', '12am', '1pm', '2PM', '3pm', '12PM', '111am', '114pm', '24pm']
        self.assertEqual(mp.convertTimeTo24Hr(timelist), ([1, 2, 3, 0, 13, 14, 15, 12]))
    
    '''
    Test if the first two rows (update row and field name row) are correctly taken out
    '''
    def test_removeUpdateRowAndFieldRow(self):
        mp = MarketParser(self.url2)
        # Use test csv file to see if the function is correctly getting rid of the first two rows
        with open('testline.csv') as csvfile:
            testline = csv.reader(csvfile, quotechar='"', delimiter=',',
            quoting=csv.QUOTE_ALL, skipinitialspace=True)
            self.assertEqual(mp.removeUpdateRowandFieldNames(testline), ['testline2', ''])

if __name__ == '__main__':
    unittest.main()
