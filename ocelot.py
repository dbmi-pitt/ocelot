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
        walkscore = resp.get('walkscore')
        if walkscore is not None:
            walkscoredesc = resp.get('description')
        else:
            walkscore = 'n/a'
            walkscoredesc = 'n/a'

        bike = resp.get('bike')
        if bike is not None:
            bikescore = bike.get('score')
            bikescoredesc = bike.get('description')
        else:
            bikescore = 'n/a'
            bikescoredesc = 'n/a'
        transit = resp.get('transit')
        if transit is not None:
            transitscore = transit.get('score')
            transitscoredesc = transit.get('description')
        else:
            transitscore = 'n/a'
            transitscoredesc = 'n/a'
        scores = {'walkscore': walkscore, 'walkscoredesc': walkscoredesc,'bikescore': bikescore,'bikescoredesc':bikescoredesc, 'transitscore': transitscore,'transitscoredesc':transitscoredesc}
    else:
        scores = {'walkscore': 'n/a', 'walkscoredesc': 'n/a', 'bikescore': 'n/a',
                  'bikescoredesc': 'n/a', 'transitscore': 'n/a', 'transitscoredesc': 'n/a'}

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
# sheet1.write(0, 1, 'latitude')
# sheet1.write(0, 2, 'longitude')
sheet1.write(0, 1, 'tract')
sheet1.write(0, 2, 'walkscore')
sheet1.write(0, 3, 'walkscoredesc')
sheet1.write(0, 4, 'bikescore')
sheet1.write(0, 5, 'bikescoredesc')
sheet1.write(0, 6, 'transitscore')
sheet1.write(0, 7, 'transitscoredesc')

# Loop through input spreadsheet and obtain census tract and walk scores.
for index, row in dfgeodata.iterrows():
    address = row['STREET'].replace(' ', '-') + '-' + row['CITY'] + '-' + row['STATE'] + '-' + str(row['ZIP'])
    lat = row[' latitude']
    long = row[' longitude']
    studyid = row['STUDY_ID']

    print('Study ID:',studyid,'lat: ',lat,'long:',long)
    # Comment these lines to use actual values.
    # lat = latpoc
    # long = longpoc
    # address = addresspoc
    # Comment these lines to use actual values.

    tract = getCensusTract(latpoc, long)
    print('   tract:',tract)
    scores = getWalkScores(address, latpoc, long)
    print('   scores:',scores)

    xlrow = index+1
    sheet1.write(xlrow, 0, studyid)
    # sheet1.write(xlrow, 1, lat)
    # sheet1.write(xlrow, 2, long)
    sheet1.write(xlrow, 1, tract)
    sheet1.write(xlrow, 2, scores.get('walkscore'))
    sheet1.write(xlrow, 3, scores.get('walkscoredesc'))
    sheet1.write(xlrow, 4, scores.get('bikescore'))
    sheet1.write(xlrow, 5, scores.get('bikescoredesc'))
    sheet1.write(xlrow, 6, scores.get('transitscore'))
    sheet1.write(xlrow, 7, scores.get('transitscoredesc'))


wbout.save('ocelot.xls')