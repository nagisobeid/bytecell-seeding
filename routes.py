import json
import os
import webbrowser 
import requests
import time

class DataFetch:

    def __init__( self ):
        self.id = None
        self.uuid = None
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def getReviews( self, page ):
        route = f'https://www.backmarket.com/bm/reviews/v2/product/{self.uuid}/list?page={page}'
        return DataFetch.request( route, self.headers )

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

    @staticmethod
    def request( route, headers ):
        try:
            response = requests.get( route, headers=headers )
            return response
        except Exception as e:
            return e
