import yaml
import builder
import routes
import routesbytecell
import time
import json
import copy
from time import sleep
from tqdm import tqdm
from alive_progress import alive_bar
import database
from random import *
import os
from dotenv import load_dotenv
import pandas as pd
import requests
import helpers
import math
import traceback
import logging as logger

load_dotenv()

# initialize db sql
db = database.DataBase( os.getenv('DB_SERVER'), os.getenv('DB'), os.getenv('USERNAME'), os.getenv('PASSWORD') )


def checkPrices():
    #setup
    bc = routesbytecell.ByteCell( )
    bc.setParams( { 'collection' : 'iphone' } )

    #get the product uuids and hrefs
    targetProds = bc.getProductsForPriceChecks()
    tarData = targetProds.json()#helpers.extractData( targetProds )
    #print(tarData)
    #return
    dfTarData = pd.DataFrame( tarData )
    
    #get every product entry and store localy to prevent db requests
    allProds = bc.getEveryProductEntry()
    allData = helpers.extractData( allProds )
    dfAllData = pd.DataFrame( allData )
    
    #datafetch setup
    proxies = helpers.get_proxies()
    fetcher = routes.DataFetch()

    #start looping target prods
    #tarData = [ { 'UUID' : 'b51131db-e2ac-4c16-9dff-004cf5714ed6' } ] # fe903edb-00f2-4a91-b497-d55fd4873c76 cbbc065f-728e-4e7d-8844-c6b4a3f39c61
    
    #testing
    #tarData = tarData[0:5]

    updated = []
    HTTP_LIMIT_COUNT = 0

    for target in tarData:
        #additional prep on every loop
        fetcher.setUuid( target['UUID'] )
        proxy = helpers.getProxy(proxies)
        useragent = helpers.getUserAgent() #'X-Forwarded-For':'1.1.1.1'
        headers = {'User-Agent': useragent}#, 'X-Forwarded-For': proxy }
        fetcher.setHeaders( headers )
        fetcher.setProxy( proxy )

        #try send request
        try:
            res = fetcher.getOffers()#.json()
            #sleep for a couple of sec
            #time.sleep( randint(1, 3) )
            time.sleep( 1 )
    
            #if "error" in res:
            #    raise Exception( res )

            if res.status_code != 200:
                if res.status_code == 429:
                    HTTP_LIMIT_COUNT = HTTP_LIMIT_COUNT + 1
                raise Exception( {'status_code' : res.status_code} )
            
            if HTTP_LIMIT_COUNT >= 10:
                print( 'TRIGGERED - HTTP_LIMIT_COUNT : ' + str( HTTP_LIMIT_COUNT ) )
                break
            
            res = res.json()
            
            dfRes = pd.DataFrame( res )
            try:
                df2 = dfRes.loc[:, ["price","backboxGrade","isDisabled"]]
            except Exception as e:
                raise Exception( { 'error' : e } )

            l = df2.values.tolist()

            for i in l:
                d = {
                        'UUID'          :   target['UUID'],
                        'PRICE'         :   '',
                        'BMPRICE'       :   '',
                        'CONDITION'     :   '',
                        'AVAILSTATUS'   :   ''
                    }

                try:
                    if i[0]['amount']:
                        d['BMPRICE'] = round(float( i[0]['amount'] ), 2)

                except Exception as ex:
                    if math.isnan( i[0] ):
                        d['BMPRICE'] = 0

                d['CONDITION'] = i[1]['name']
                d['AVAILSTATUS'] = int( not i[2] )
                d['PRICE'] = round(helpers.calculateByteCellPrice( d['BMPRICE'] ), 2)

                #d['PRICECHAGNED'] = 1 if d['BMPRICE'] != b else 0

                updated.append( d )
                #print( d )
            #print( "==============================" )

        except Exception as e:
            #traceback.format_exc()
            #logger.exception( e )
            print( e )
            #set product default to not avail for all otpions
            updated.extend( setAsNotAvail( target['UUID'] ) )
    #print( updated )
    print('Request sent...')
    response = bc.updateProducts( { 'json' : json.dumps( { "PRODUCTS" : updated } ) } )
    print( response.json() )
        
def setAsNotAvail( uuid ):
    conditions = ['Fair','Good','Excellent']
    data = []

    for c in conditions:
        o = {
            'UUID'          :   uuid,
            'PRICE'         :   0.00,
            'BMPRICE'       :   0.00,
            'CONDITION'     :   c,
            'AVAILSTATUS'   :   0
        }

        data.append( o )
    
    return data