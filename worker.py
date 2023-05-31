import time
import json
import os
import ast
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
import pandasql as ps
import requests
import math
import traceback
import logging as logger
import sys
import numpy as np
import paths
import bc as bcr
import bm as bmr
import helpers

# initialize db sql
#print( 'Connecting to DB Server ->', os.getenv('DB_SERVER'), os.getenv('DB'), os.getenv('DB_USERNAME') )
#db = database.DataBase( os.getenv('DB_SERVER'), os.getenv('DB'), os.getenv('DB_USERNAME'), os.getenv('PASSWORD') )

def checkPrices( collection ):
    try:
        #setup
        bc = bcr.ByteCell()
        bc.setParams( { 'collection' : collection } )
        
        #get the product uuids and hrefs
        productProdsResponse = bc.getProductsForPriceChecks()
        products = productProdsResponse.json()
        
        dfProducts = pd.DataFrame( products )
    
        #get every product entry and store localy to prevent db requests
        allProds = bc.getEveryProductEntry()
        allData = helpers.extractData( allProds )
        dfAllData = pd.DataFrame( allData )

        dfAllData.rename(columns = {'price':'oldPrice'}, inplace = True)

        #datafetch setup
        proxies = helpers.get_proxies()
        fetcher = bmr.DataFetch()
    except Exception as e:
        print( e )
        return e

    #products = products[0:5]

    HTTP_LIMIT_COUNT = 0

    productDataFrames = []
    #xx=0
    for product in products:
        #xx=xx+1
        #if(xx > 6):
        #    break
        #additional prep on every loop
        fetcher.setUuid( product['UUID'] )
        proxy = '' # helpers.getProxy(proxies)
        useragent = ''
        headers = {'User-Agent': useragent}
        fetcher.setHeaders( headers )
        fetcher.setProxy( proxy )

        #try send request to backmarket
        try:
            res = fetcher.getOffers()
            time.sleep( 1 )
    
            if res.status_code != 200:
                if res.status_code == 429:
                    HTTP_LIMIT_COUNT = HTTP_LIMIT_COUNT + 1
                raise Exception( {'status_code' : res.status_code} )
            
            if HTTP_LIMIT_COUNT >= 10:
                print( 'TRIGGERED - HTTP_LIMIT_COUNT : ' + str( HTTP_LIMIT_COUNT ) )
                break
            
            res = res.json()

            dfBackMarketProduct = pd.DataFrame( res )
            dfBackMarketProduct['uuid'] = product['UUID']

            #filter what we need
            try:
                # try to get only the price, backboxgrade, isdisabled, and uuid
                dfPriceAndConditionAndStatus = dfBackMarketProduct.loc[:, ["price","backboxGrade","isDisabled","uuid"]]
            except:
                # if fail, most likely because price is missing( prod not in stock ), therefore, set a default price value to continue
                dfBackMarketProduct['price'] =  {'amount': 'False', 'currency': 'USD'}
                # then get only the price, backboxgrade, isdisabled, and uuid
                dfPriceAndConditionAndStatus = dfBackMarketProduct.loc[:, ["price","backboxGrade","isDisabled","uuid"]]

            # replace all "NaN" values in the [price] column with "False", although this should not be an issue because of the try/except block
            dfPriceAndConditionAndStatus["price"] = dfPriceAndConditionAndStatus["price"].replace( np.nan, 'False' )

            # because we cant replace with an object above, replace all False with object here
            dfPriceAndConditionAndStatus['price'] = np.where(dfPriceAndConditionAndStatus['price'] == "False", {'amount': 'False', 'currency': 'USD'}, dfPriceAndConditionAndStatus['price'])

            productDataFrames.append( dfPriceAndConditionAndStatus )
        except Exception as e:
            print( e )

    # now lets merge the dataframes
    backMarketPriceData = pd.concat( productDataFrames, ignore_index=True )
    # extract the name from the backbox grade
    backMarketPriceData['backboxGrade'] = np.where( backMarketPriceData['backboxGrade'] != 5, backMarketPriceData['backboxGrade'].apply(lambda x: x.get('name')) , backMarketPriceData['backboxGrade'])
    # extract the amount from the price
    backMarketPriceData['price'] = np.where( backMarketPriceData['price'] != 'False', backMarketPriceData['price'].apply(lambda x: x.get('amount')) , backMarketPriceData['price'])

    backMarketPriceData.rename(columns = {'backboxGrade':'condition'}, inplace = True)

    merged = pd.merge( backMarketPriceData, dfAllData, how="left", on=['condition','uuid'] )
    merged.rename(columns = {'price': 'BMPRICE', 'uuid' : 'UUID', 'condition' : 'CONDITION', 'isDisabled' : 'AVAILSTATUS' }, inplace = True)

    # replace values
    merged['AVAILSTATUS'] = np.where( merged['AVAILSTATUS'] == True, "1x" , merged['AVAILSTATUS'])
    merged['AVAILSTATUS'] = np.where( merged['AVAILSTATUS'] == 'False', 1 , merged['AVAILSTATUS'])
    merged['AVAILSTATUS'] = np.where( merged['AVAILSTATUS'] == "1x", 0 , merged['AVAILSTATUS'])

    merged['PRICE'] = np.where( merged['BMPRICE'] == 'False', merged['oldPrice'] , merged['BMPRICE'])

    merged['PRICE'] = merged['PRICE'].apply( lambda x: round( helpers.calculateByteCellPrice(float(x)), 2) )
    final = merged.loc[:,['CONDITION','AVAILSTATUS','UUID','PRICE','BMPRICE']]
    print( final )

    updated = final.to_dict( 'records' )
    #print( updated )

    print('Sending request...')
    response = bc.updateProducts( { 'json' : json.dumps( { "PRODUCTS" : updated } ) } )
    print('Request sent')
    print( response.json() )
