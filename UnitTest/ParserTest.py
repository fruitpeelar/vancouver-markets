'''
Created on Nov 26, 2014

@author: JunOh
'''

from mainpage.parser import MarketParser
import unittest
import urllib2
import csv
import re
import time
import json
import datetime

class TestParser(unittest.TestCase):
    def setUp(self):
        url = 'ftp://webftp.vancouver.ca/OpenData/csv/CommunityFoodMarketsandFarmersMarkets.csv'
        self.mp = MarketParser(url)
        
    def test_checkEmpty(self):
        fieldlist = ["",'','emptycheck']
        self.assertEqual(self.mp.checkEmpty(fieldlist), ['N/A','N/A','emptycheck'])
    
    def test_getOpenCloseMonths(self):
        monthslist = ['Jan-Feb', 'Jan to Feb', 'Mid-Jan to Feb', 'not months']
        self.assertEqual(self.mp.getOpenCloseMonths(monthslist), ([1,1,1], [2,2,2]))
    
    def test_convertTimeTo24Hr(self):
        timelist = ['N/A', '1am', '2AM', '3am', '12am', '1pm', '2PM', '3pm', '12PM', '111am', '114pm', '24pm']
        self.assertEqual(self.mp.convertTimeTo24Hr(timelist), ([1, 2, 3, 0, 13, 14, 15, 12]))
    
        

if __name__ == '__main__':
    unittest.main()
