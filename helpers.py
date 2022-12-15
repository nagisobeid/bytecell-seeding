import yaml
import builder
import routes
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

load_dotenv()

GLOBAL_UUIDS = []

# initialize db sql
db = database.DataBase( os.getenv('DB_SERVER'), os.getenv('DB'), os.getenv('USERNAME'), os.getenv('PASSWORD') )

def loadYaml( ):
    with open(r'../data.yml') as yamlFile:
        data = yaml.load( yamlFile, Loader=yaml.FullLoader )
        return data

def fillHrefs():
    # GET PRODUCTS MISSING HREFS
    fetcher = routes.DataFetch( )

    prodIds = db.getProdsMissingHrefs()
    for index, row in prodIds.iterrows():
        #api call to bm 'offers' endpoint
        fetcher.setUuid( row['UUID'] )
        print(row['UUID'])
        try:
            data = fetcher.getOffers()
            if data.status_code != 200:
                raise Exception( f'Response err during getOffers : {data.status_code} '  )
            dataJson = data.json()

            for entry in dataJson:
                if not entry['isDisabled']:
                    if entry["link"]["params"]["uuid"] == row['UUID']:
                        print('updating Href...')
                        db.updateHref( row['UUID'],  entry["link"]['href'] )
                        break
            time.sleep( randint(1, 2) )

        except Exception as e:
            print( { 'exception': e } )

    

def getItems( yamlFile ):
    items = []
    for item in yamlFile['attributesToRetrieve']:
        items.append( item ) 

    return items

def buildSet( yamlFile, item ):
    facetFilters = None
    try:
        if yamlFile[item]['facetFilters']:
            facetFilters = yamlFile[item]['facetFilters']
    except:
        facetFilters = []
    return {
        'facets': yamlFile[item]['facets'],
        'attributes': yamlFile['attributesToRetrieve'][item],
        'filters': yamlFile[item]['filters'],
        'facetFilters': facetFilters,
        'params': yamlFile[item]['params']
    }

# refactor to ensure no duplicate uuid is included in data
def getBackMarketIDsAndUUIDs( response ):
    data = {}
    hits = response['results'][0]['hits']
    for hit in hits:
        if not hit['backmarketID'] in data:
            # added for escaping uuids if already exists in global_uuids arr
            #if not hit['link']['params']['uuid'] in GLOBAL_UUIDS:   # added
            try:
                data[hit['backmarketID']] = [ hit['link']['params']['uuid'] ]
            except:
                log = prepareForInsertLog( 'helpers.py', 'NOT FOUND -> ' + str( hit['backmarketID'] ), '', 'getBackMarketIDsAndUUIDs', 'FAIL' )
                db.insertLog( log )

    return data

#because a single bcid/id can have mulitple uuids for variants
def addVariantUUIDS( ids ):
    toDelete = []
    fetcher = routes.DataFetch( )
    for idx, id in enumerate( ids ):
        log = prepareForInsertLog( 'helpers.py', 'ID NUM : ' + str(idx) + '/' + str(len(ids)), '', 'addVariantUUIDS', '' )
        global db
        db.insertLog( log )
        fetcher.setIds( id, ids[id][0] )
        baseUuid = ids[id][0]
        try:
            while True:
                variantData = fetcher.getVariants()
                time.sleep( randint(1, 3) )
                if variantData.status_code == 200:
                    variants = variantData.json()
                    options = []
                    for option in variants['variantsByDeviceOptions']:
                        options.append( option )
                    baseOption = options[0]
                    if len( variants['variantsByDeviceOptions'][baseOption] ) > 0:
                        uuids = fetchUuidsForBaseOption( baseUuid, baseOption, options, variants )
                        uuidsAndJson = {
                            'uuids'     :   uuids,
                            'json'      :   variants['variantsByDeviceOptions'],
                            'baseoption':   baseOption
                        }
                    else:
                        uuids = fetchUuidsForBaseOption( baseUuid, baseOption, options, variants )
                        uuidsAndJson = {
                            'uuids'     :   uuids,
                            'json'      :   variants['variantsByDeviceOptions']
                        }
                    ids[id] = uuidsAndJson
                    break
                elif variantData.status_code == 429:
                    time.sleep( randint(60, 220) )
                    log = prepareForInsertLog( 'helpers.py', str(variantData), '', 'addVariantUUIDS', f'{variantData.status_code}' )
                    db.insertLog( log )
                else:
                    # may need to remove the id from the IDS array since likely error 404 was returned IE. Not found
                    log = prepareForInsertLog( 'helpers.py', str(variantData), '', 'addVariantUUIDS', f'{variantData.status_code}' )
                    db.insertLog( log )
                    toDelete.append( id )
                    break
        except Exception as e:
            print( e ) 
    
    #start deleting keys that returned 404 err
    for key in toDelete:
        del ids[key]

    return ids

def fetchUuidsForBaseOption( baseUuid, baseOption, options, variants ):
    #print(baseUuid)
    uuids = []
    if len( variants['variantsByDeviceOptions'] ) == 0:
        print('NO OPTIONS FOUND')
    else:
        for option in variants['variantsByDeviceOptions']:
            if len(variants['variantsByDeviceOptions'][option]) > 0:
                if option != baseOption:
                    for variant in variants['variantsByDeviceOptions'][option]:
                        if ( variant['id'] not in uuids ) and ( variant['id'] not in GLOBAL_UUIDS ):    # added
                            GLOBAL_UUIDS.append( variant['id'] )   # added
                            uuids.append( variant['id'] )
                            #print( 'ADDING OPTION <-> ' + variant['id'] )
            else:
                if ( baseUuid not in uuids ) and ( baseUuid not in GLOBAL_UUIDS ) :
                    GLOBAL_UUIDS.append( baseUuid )    # added
                    uuids.append( baseUuid )
    return uuids

#only for initial database data entry
def initializeData( items ):
    print("initializing Datasets ...")

    data = loadYaml()
    collections = {}

    #init builder
    bldr = builder.Builder( '', '', '', '' )

    for item in tqdm( items ):

        ids = {}
        itemSet = buildSet( data, item )

        bldr.setFacets( itemSet['facets'] )
        bldr.setFilters( itemSet['filters'] )
        bldr.setFacetFilters( itemSet['facetFilters'] )
        bldr.setParams( itemSet['params'] )
        response = bldr.getData()

        if response:

            responseData = response
          
            ids = getBackMarketIDsAndUUIDs( responseData )
            ids = addVariantUUIDS( ids )
        else:
            log = prepareForInsertLog( 'helpers.py', str(response), str(item), 'initializeData', f'{response.status_code}' )
            db.insertLog( log )
            time.sleep( 30 )

        collections[item] = ids

    return collections

def getSecondaryOptionIfNotSelected( json, uuid, option ):
    for item in json[option]:
        if str( uuid ) in str( item['link']['href'] ):
            optionItem = {
                'name'      :   item['name'],
                'available' :   item['available'],
                'slug'      :   item['link']['params']['slugV2'],
                'href'      :   item['link']['href']
            }
            return optionItem


# does a full remaping of the product object for readability and accessability
def beautify( collections ):
    data = {}
    print('Remaping Collectionns ... ')
    for collection in tqdm(collections):
        #print(collection)
        data[collection] = {}
        for bcid in collections[collection]:
            data[collection][bcid] = {}
            for id in collections[collection][bcid]['uuids']:
                data[collection][bcid][id] = {}
                try:
                    baseOption = collections[collection][bcid]['baseoption']
                except:
                    baseOption = None
                finally:
                    for uuid in collections[collection][bcid]['uuids']:
                        itemData = {}
                        itemData['bmid'] = bcid
                        itemData['collection'] = collection
                        baseHref = None
                        if baseOption:
                            for item in collections[collection][bcid]['json'][baseOption]:
                                if item['selected']:
                                    baseHref = item['link']['href']
                                    itemData[baseOption] = {
                                        'name'      :   item['name'],
                                        'color'     :   item['color'],
                                        'available' :   item['available'],
                                        'slug'      :   item['link']['params']['slugV2'],
                                        'href'      :   item['link']['href']
                                    }

                            for option in collections[collection][bcid]['json']:
                                if option != baseOption:
                                    #items = []
                                    for item in collections[collection][bcid]['json'][option]:
                                        if item['selected'] and str( uuid ) in str( baseHref ):
                                            optionItem = {
                                                'name'      :   item['name'],
                                                'available' :   item['available'],
                                                'slug'      :   item['link']['params']['slugV2'],
                                                'href'      :   item['link']['href']
                                            }
                                            itemData[option] = optionItem
                                            itemData['href'] = baseHref

                                        elif item['selected'] and str( uuid ) not in str( baseHref ):
                                            itemData[option] = getSecondaryOptionIfNotSelected( collections[collection][bcid]['json'], uuid, option )
                                            itemData['href'] = itemData[option]['href']

                                    itemData['uuid'] = uuid
                                    
                            data[collection][bcid][uuid] = itemData
                        else:
                            itemData['uuid'] = uuid
                            itemData['href'] = baseHref

                            data[collection][bcid][id] = itemData
 
    return data

def getSpecs( fetcher ):
    response = fetcher.getTechnicalSpecs()
    technicalSpecs = {}
    if response.status_code == 200:
        details = response.json()

        for detail in details:
            specs = {
                "title"         : details['title'],
                "specs"         : details['specifications']
            }
            
            technicalSpecs = specs
    else:
        log = prepareForInsertLog( 'helpers.py', str(response), '', 'getSpecs', f'{response.status_code}' )
        db.insertLog( log )
        time.sleep( 30 )

    return technicalSpecs
    

def getConditions( fetcher, product ):
    response = fetcher.getOffers()
    conditions = {}
    optionDisabled = False
    if response.status_code == 200:
        offers = response.json()

        for offer in offers:
            isDisabled = False
            price = None
            try:
                if offer['isDisabled']:
                    isDisabled = True
            except:
                isDisabled = False
            
            try:
                if not product['color']['available']:
                    optionDisabled = True
            except:
                optionDisabled = False

            try:
                if not product['storage']['available']:
                    optionDisabled = True
            except:
                optionDisabled = False

            if isDisabled or optionDisabled:
                data = {
                    "condition"     : offer['backboxGrade']['name'],
                    "isDisabled"    : True
                }
            else:
                data = {
                    "price"         : offer['price']['amount'],
                    "condition"     : offer['backboxGrade']['name'],
                    "isDisabled"    : offer['isDisabled'],
                    "shipping"      : offer['reassurance']['shipping']
                }
            conditions[offer['backboxGrade']['name']] = data
    else:
        log = prepareForInsertLog( 'helpers.py', str(response), '', 'getConditions', f'{response.status_code}' )
        db.insertLog( log )
        time.sleep( 30 )

    return conditions

def getReviews( fetcher ):
    page = 1
    allReviews = []
    hasNext = True
    while hasNext and page < 3:
        response = fetcher.getReviews( page )
        if response.status_code == 200:
            reviews = response.json()
            allReviews.extend( reviews['results'] )
            if reviews['next']:
                page = page+1
            else:
                hasNext = False
        else:
            time.sleep( 30 )

    return allReviews

#collect all relevant data for a specefic product
def purgeProducts( collections ):
    fetcher = routes.DataFetch()
    print('Purging Collections ...')
    with alive_bar(len(collections), force_tty=True) as bar:
        for collection in collections:
            for bcid in collections[collection]:
                for uuid in collections[collection][bcid]:
                    fetcher.setIds( bcid, uuid )

                    conditions = getConditions( fetcher, collections[collection][bcid][uuid] )
                    collections[collection][bcid][uuid]['condition'] = conditions

                    specs = getSpecs( fetcher )
                    collections[collection][bcid][uuid]['specs'] = specs

                    # attempt to prevent too many requests
                    time.sleep( randint(1, 3) )
            bar()

    return collections

# takes a single prodct object and prepares it for insert into db, returns insert string

def prepareForInsert( product ):
    prepared = {}

    baseInsertString = '@collection = ?, @bmid=?, @uuid=?, @href=?, @specs=?, @title = ?'
    baseValues = [product['collection'], product['bmid'], product['uuid'], product['href'], str(product['specs']), product['specs']['title']]
    
    try:
        if product['color']:
            baseInsertString = baseInsertString + ', @color = ?, @colorValue = ?, @colorAvailable = ?'
            baseValues.extend([product['color']['name'], product['color']['color'],product['color']['available']])
    except:
        baseInsertString = baseInsertString
        baseValues = baseValues
    
    try:
        if product['storage']:
            baseInsertString = baseInsertString + ', @storage = ?, @storageAvailable = ?'
            baseValues.extend([product['storage']['name'],product['storage']['available']])
    except:
        baseInsertString = baseInsertString
        baseValues = baseValues

    for condition in product['condition']:
        conditionAvailable = None
        data = {}
        insertValues = []
        insertString = baseInsertString + ', @condition = ?, @conditionAvailable = ?, @bmPrice = ?, @price = ?'
        
        insertValues = copy.deepcopy( baseValues )
        price = None
        bmPrice = None

        if product['condition'][condition]['isDisabled']:
            conditionAvailable = 0
            price = 0.00
            bmPrice = 0.00
        else:
            conditionAvailable = 1
            bmPrice = float( product['condition'][condition]['price'] )
            price = calculateByteCellPrice( bmPrice )
        
        insertValues.extend( [product['condition'][condition]['condition'], conditionAvailable, bmPrice] )
    
        insertValues.append( price )

        data['insertString'] = insertString
        data['insertValues'] = insertValues

        prepared[condition] = data

    return prepared

def prepareForInsertLog( system, message, uuid, method, status ):
    prepared = {}
    data = {}

    data['insertString'] = '@system = ?, @message=?, @uuid=?, @method=?, @status=?'
    data['insertValues'] = [system, message, uuid, method, status]
    
    prepared['log'] = data

    return prepared


def calculateByteCellPrice( price ):
    price = price + ( price * .08 )
    return price


def jsonPrint( data ):
    print( json.dumps( data, indent = 4) )
    exit()