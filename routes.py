import json
import os
import webbrowser 
import requests
import time

requests.trust_env = False

class DataFetch:

    def __init__( self ):
        self.id = None
        self.uuid = None
        #self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.headers = {}
        self.proxy = None

    def getReviews( self, page ):
        route = f'https://www.backmarket.com/bm/reviews/v2/product/{self.uuid}/list?page={page}'
        return DataFetch.request( route, self.headers, {"http": self.proxy} )

    def getOffers( self ):
        route = f'https://www.backmarket.com/bm/product/{self.uuid}/v3/best_offers'
        return DataFetch.request( route, self.headers )

    def getTechnicalSpecs( self ):
        route = f'https://www.backmarket.com/bm/product/{self.uuid}/technical_specifications'
        return DataFetch.request( route, self.headers )

    def getVariants( self ):
        route = f'https://www.backmarket.com/bm/product/{self.uuid}/v2/variants'
        return DataFetch.request( route, self.headers )
        
    def getGradeDescriptions( self ):
        route = f'https://www.backmarket.com/bm/product/{self.uuid}/grade_descriptions?include_technical_comment=tru'
        return DataFetch.request( route, self.headers ).json()

    def setId( self, id ):
        self.id = id
    
    def setUuid( self, uuid ):
        self.uuid = uuid

    def setIds( self, id, uuid ):
        self.id = id
        self.uuid = uuid

    def setHeaders( self, headers ):
        self.headers = headers
    
    def setProxy( self, proxy ):
        self.proxy = proxy

    @staticmethod
    def request( route, headers, proxies ):
        try:
            print( headers, proxies )
            #response = requests.get( route, headers=headers )
            response = requests.get( route, headers=headers, proxies=proxies )
            #response = requests.get( route, headers=headers, proxies={"http": '159.89.128.130:8989', "http": '159.89.128.130:8989'} )
            return response
        except Exception as e:
            print( e )
            raise Exception( e )
