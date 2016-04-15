# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 08:42:34 2016

@author: Gretel_MacAir
"""

# %%Import libs
import requests
import urllib
import re
import os
from datetime import datetime
import sys
import getopt

# %% Define Functions

# Functions to download the Property Tax Bill
# and Notice of Property Value PDFs from the NYC website


def get_PTBtaxPDF(number, street, area):
    '''
    Downloads the latest Property Tax Bill from NYC for a certain address
    Enter number and street as strings
    Use area '1' for Manhattan (Default)
    Use area '2' for Bronx
    Use area '3' for Brooklyn
    Use area '4' for Queens
    Use area '5' for Staten Island
    The PDF will be stored in your current working dir
    '''
    params = {'FBORO': area, 'FHOUSENUM': number, 'FSTNAME': street}
    request1 = requests.post(
        "HTTP://webapps.nyc.gov:8084/CICS/fin1/find001i",
        data=params)
    request1Text = request1.text
    request1List = request1Text.split('<input type=')
    request1InputList = request1List[1:-1]
    request1Dict = {}
    for n in range(22):
        templist = request1InputList[n]
        key = templist.split('"\r\n')[0].split('"hidden" name="')[1]
        value = templist.split('value="')[1].split('">\r\n')[0]
        request1Dict[key] = value
    params = request1Dict
    request2 = requests.post(
        "HTTP://NYCPROP.NYC.GOV/nycproperty/nynav/jsp/stmtassesslst.jsp",
        data=params)
    request2Text = request2.text
    bbl = re.findall('bbl=\d+', request2Text)
    bbl = bbl[0].split('=')[1]
    dateTemp1 = request2Text.split(' - Quarterly Property Tax Bill')[0]
    dateTemp2 = dateTemp1.split('\t')[-1]
    dateTemp3 = datetime.strptime(dateTemp2, '%B %d, %Y')
    stmtDateLast = dateTemp3.strftime('%Y%m%d')
    path = os.getcwd()
    name = '/PTB' + number + " " + street + '.pdf'
    pathName = path + name
    url = 'http://nycprop.nyc.gov/nycproperty/StatementSearch?bbl=' + bbl + '&stmtDate=' + stmtDateLast + '&stmtType=SOA'
    urllib.urlretrieve(url, pathName)
    return url


def get_NPVtaxPDF(number, street, area):
    '''
    Downloads the latest Notice of Property Value
    from NYC for a certain address
    Enter number and street as strings
    Use area '1' for Manhattan (Default)
    Use area '2' for Bronx
    Use area '3' for Brooklyn
    Use area '4' for Queens
    Use area '5' for Staten Island
    The PDF will be stored in your current working dir
    '''
    params = {'FBORO': area, 'FHOUSENUM': number, 'FSTNAME': street}
    request1 = requests.post(
        "HTTP://webapps.nyc.gov:8084/CICS/fin1/find001i",
        data=params)
    request1Text = request1.text
    request1List = request1Text.split('<input type=')
    request1InputList = request1List[1:-1]
    request1Dict = {}
    for n in range(22):
        templist = request1InputList[n]
        key = templist.split('"\r\n')[0].split('"hidden" name="')[1]
        value = templist.split('value="')[1].split('">\r\n')[0]
        request1Dict[key] = value
    params = request1Dict
    request2 = requests.post(
        "HTTP://NYCPROP.NYC.GOV/nycproperty/nynav/jsp/stmtassesslst.jsp",
        data=params)
    request2Text = request2.text
    bbl = re.findall('bbl=\d+', request2Text)
    bbl = bbl[0].split('=')[1]
    dateTemp1 = request2Text.split(' - Notice of Property Value')[0]
    dateTemp2 = dateTemp1.split('\t')[-1]
    dateTemp3 = datetime.strptime(dateTemp2, '%B %d, %Y')
    stmtDateLast = dateTemp3.strftime('%Y%m%d')
    path = os.getcwd()
    name = '/NPV' + number + " " + street + '.pdf'
    pathName = path + name
    url = 'http://nycprop.nyc.gov/nycproperty/StatementSearch?bbl=' + bbl + '&stmtDate=' + stmtDateLast + '&stmtType=NPV'
    urllib.urlretrieve(url, pathName)
    return url

# %% Call Funtions for range of hoursenumbers in street


def main(argv):
    upToNumber = (0, 1000)
    street = ''
    area = 1
    try:
        opts, args = getopt.getopt(argv, "u:s:a:", ["upto=", "street=", "area="])
    except getopt.GetoptError:
        print 'NYC_GetPDF.py -u <upto> -s <street> -a <area>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'Help NYC_GetPDF.py -u <upto> -s <street> -a <area>'
            sys.exit()
        elif len(opts) != 3:
            print 'Not 3 NYC_GetPDF.py -u <upto> -s <street> -a <area>'
            sys.exit()
        else:
            if opt in ("-u", "--upto"):
                upto = arg
                numbers = (0, upto)
            elif opt in ("-s", "--street"):
                street = arg
            elif opt in ("-a", "--area"):
                area = arg
            for n in numbers:
                number = str(n)
                try:
                    get_PTBtaxPDF(number, street, area)
                    get_NPVtaxPDF(number, street, area)
                except:
                    pass

if __name__ == "__main__":
    main(sys.argv[1:])
