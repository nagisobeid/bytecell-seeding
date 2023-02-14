import requests
import json
import urllib
import copy
 
#import routes

class Builder: 
    def __init__( self, facets, filters, attributesToRetrieve, collectionParams ):
        self.facets = facets
        self.filters = filters
        self.attributesToRetrieve = attributesToRetrieve
        self.collectionParams = collectionParams

        self.url ='https://9x8zudunn9-dsn.algolia.net/1/indexes/*/queries'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'}
        self.params = {
            'x-algolia-agent': 'Algolia for JavaScript (4.14.2); Browser (lite); JS Helper (3.11.1)',
            'x-algolia-application-id': '9X8ZUDUNN9',
            'x-algolia-api-key': '38f3a5eacb0bd01a763275f972706859'
        }
        #Utilize a simplier way to input query parameters
        self.query = {
            "indexName": "prod_us_index_backbox_en-us",
            "hitsPerPage": "30",
            "maxValuesPerFacet": "20",
            "page": "0",
            "distinct": "1", 
            "facetFilters": '',
            "filters": '',
            "facets": '',
            "tagFilters": '"}]}'
        }

    def setFacets( self, facets ):
        self.facets = facets
        self.query['facets'] = str( facets )

    def setFilters( self, filters ):
        self.filters = filters
        self.query['filters'] = filters

    def setFacetFilters( self, facetFilters ):
        self.facetFilters = facetFilters
        self.query['facetFilters'] = facetFilters
    
    def setAttributes( self, attributes ):
        self.attributesToRetrieve = attributes
    
    def setParams( self, params ):
        self.collectionParams = params
    
    def getData( self ):
        localColParams = self.collectionParams
        hits = []
        data = '''{"requests": [{"indexName": "%s", "params": "%s"}]}''' %( self.query['indexName'], self.collectionParams)

        initialData = requests.post( self.url, data=data, params=self.params )
        hits.extend( initialData.json()['results'][0]['hits'] )
        pages = int( initialData.json()['results'][0]['nbPages'] )
        
        for page in range( pages ):
            if page == 0:
                data = data
            else:
                localColParams = localColParams.replace(f"page={str( page - 1 )}", f"page={str( page )}")
                data = '''{"requests": [{"indexName": "%s", "params": "%s"}]}''' %( self.query['indexName'], localColParams)

            pageData = requests.post( self.url, data=data, params=self.params ).json()

            hits.extend( pageData['results'][0]['hits'] )

        initialData.json()['results'][0]['hits'] = hits

        datat = initialData.json()
        datat['results'][0]['hits'] = hits

        return datat
