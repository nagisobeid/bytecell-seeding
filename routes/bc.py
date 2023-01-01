import json
import os
from dotenv import load_dotenv
import requests

load_dotenv()

class ByteCell:

    def __init__( self ):
        #self.headers = {"BYTECELLAPIKEY": os.getenv('BYTECELLAPIKEY')}
        #self.headers = {'User-Agent': 'Mozilla/5.0'}
        self.headers = {
            'BYTECELLAPIKEY'    : os.getenv('BYTECELLAPIKEY'),
            'User-Agent'        : 'Mozilla/5.0'
            #'X-Forwarded-For':'1.1.1.1'
        }
        #self.baseUrl = 'localhost'
        self.baseUrl = os.getenv('BYTECELLAPIURL')

    def insertReviews( self, data ):
        route = f'{self.baseUrl}/reviews'
        return ByteCell.postRequest( route, data, self.headers )

    def getProductsMissingReviews( self ):
        route = f'{self.baseUrl}/reviews/missing'
        return ByteCell.getRequest( route, self.headers )

    def getProductIds( self ):
        route = f'{self.baseUrl}/products/ids'
        return ByteCell.getRequest( route, self.headers )

    def getProductsForPriceChecks( self ):
        route = f'{self.baseUrl}/products/checkprices'
        return ByteCell.getRequest( route, self.headers )
    
    def getEveryProductEntry( self ):
        route = f'{self.baseUrl}/products'
        return ByteCell.getRequest( route, self.headers )
    
    def getTest( self ):
        route = f'{self.baseUrl}/test'
        return ByteCell.getRequest( route, self.headers )

    def updateProducts( self, data ):
        route = f'{self.baseUrl}/products'
        return ByteCell.putRequest( route, data, self.headers )

    @staticmethod
    def getRequest( route, headers ):
        try:
            response = requests.get( route, headers=headers )
            return response
        except Exception as e:
            return e
    
    @staticmethod
    def postRequest( route, data, headers ):
        try:
            response = requests.post( route, json=data, headers=headers )
            return response
        except Exception as e:
            return e
    
    @staticmethod
    def putRequest( route, data, headers ):
        try:
            response = requests.put( route, json=data, headers=headers )
            return response
        except Exception as e:
            return e