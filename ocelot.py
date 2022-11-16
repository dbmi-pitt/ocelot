#!/usr/bin/env python
# coding: utf-8

# Ocelot
# Obtains census tract and Walk Score for a set of geocoordinates.

# Note Geocoordinates that correspond to the home address of a study participant constitute Patient Identifying
# Information (PII). Without an explicit waiver or approval from the UPMC IRB, geocoordinates should not be used as
# arguments to endpoints of public APIs.

# This notebook will demonstrate proof of concept using the address for DBMI:

# 5607 Baum Boulevard, Suite 500
# Pittsburgh, PA 15206-3701
# (40.4581259,-79.9352492)
# --------------------------

import pandas as pd
import os
from urllib.request import Request
import requests
import argparse

import xlwt
from xlwt import Workbook

# ------
class RawTextArgumentDefaultsHelpFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawTextHelpFormatter
):
    pass

parser = argparse.ArgumentParser(
    description='Obtains Census Tract and Walk Scores for a set of address/geocoordinate data for study IDs',
    formatter_class=RawTextArgumentDefaultsHelpFormatter)
parser.add_argument("file", help="full path to input spreadsheet name")
args = parser.parse_args()

# Obtain census tract using the Census Geocoder API.
def getCensusTract(lat, long):
    # Instructions:
    # https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html
    fmt = 'json'
    urlCensus = 'https://geocoding.geo.census.gov/geocoder/geographies/coordinates?x=' + str(long) + '&y=' + str(
        lat) + '&benchmark=Public_AR_Census2020&vintage=Census2020_Census2020&layers=10format=json'
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(urlCensus, headers=headers)
    if response.status_code == 200:
        resp = response.json()
        res = resp.get('result')
        tract = res.get('geographies').get('Census Tracts')[0].get('TRACT')
    else:
        tract = 'ERROR'
    return tract


# Obtain Walk Score information

def getWalkScores(address, lat, long):
    # Instructions:
    # https://www.walkscore.com/professional/api.php

    # API key from Walk Score
    apikey = '2f0368204f0cd4d0ce377c36eb01c8b0'

    urlWalkScore = 'https://api.walkscore.com/score?format=json&address=' + address + '&lat=' + str(
        lat) + '&lon=' + str(long) + '&transit=1&bike=1&wsapikey=' + apikey
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    response = requests.get(urlWalkScore, headers=headers)
    if response.status_code == 200:
        resp = response.json()
        walk = resp.get('walkscore')
        bike = resp.get('bike').get('score')
        transit = resp.get('transit').get('score')
        scores = {'walk': walk, 'bike': bike, 'transit': transit}
    else:
        scores = 'ERROR'
    return scores


# ##########################
# Read set of geocoordinates.
geopath = args.file
dfgeodata = pd.read_excel(geopath)

# Proof of concept values
latpoc = 40.4581259
longpoc = -79.9352492
addresspoc = '5607-Baum-Blvd.-Pittsburgh-PA-15206'


# Create Excel output
wbout = Workbook()
# Create sheet.
sheet1 = wbout.add_sheet('Output')
sheet1.write(0, 0, 'study id')
sheet1.write(0, 1, 'latitude')
sheet1.write(0, 2, 'longitude')
sheet1.write(0, 3, 'tract')
sheet1.write(0, 4, 'walk')
sheet1.write(0, 5, 'bike')
sheet1.write(0, 6, 'transit')

# Loop through input spreadsheet and obtain census tract and walk scores.
for index, row in dfgeodata.iterrows():
    address = row['STREET'].replace(' ', '-') + '-' + row['CITY'] + '-' + row['STATE'] + '-' + str(row['ZIP'])
    lat = row[' latitude']
    long = row[' longitude']
    studyid = row['STUDY_ID']

    print('Study ID:',studyid,'lat: ',lat,'long:',long)
    # Comment these lines to use actual values.
    lat = latpoc
    long = longpoc
    address = addresspoc
    # Comment these lines to use actual values.

    tract = getCensusTract(latpoc, long)
    print('   tract:',tract)
    scores = getWalkScores(address, latpoc, long)
    print('   walk: ',scores.get('walk'),'bike: ', scores.get('bike'), 'transit: ', scores.get('transit'))

    xlrow = index+1
    sheet1.write(xlrow, 0, studyid)
    sheet1.write(xlrow, 1, lat)
    sheet1.write(xlrow, 2, long)
    sheet1.write(xlrow, 3, tract)
    sheet1.write(xlrow, 4, scores.get('walk'))
    sheet1.write(xlrow, 5, scores.get('bike'))
    sheet1.write(xlrow, 6, scores.get('transit'))


wbout.save('ocelot.xls')