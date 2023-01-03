import helpers
import database
import worker
import os
from dotenv import load_dotenv
import sys
from datetime import datetime
from termcolor import colored

load_dotenv()

# ONLY RUN ONCE!
def seedingProcess( db ):
    collections = helpers.initializeData( items )
    # collect all price data and stock
    collections = helpers.beautify( collections )
    # at this point we have all variant IDs for a single BackmarketID
    purged = helpers.purgeProducts( collections )
    # inserting Objects to DB
    print('inserting objects into Database ...')
    for col in purged:
        with helpers.alive_bar(len(purged[col]), force_tty=True) as bar:
            for id in purged[col]:
                for uuid in purged[col][id]:
                    inserts = helpers.prepareForInsert( purged[col][id][uuid] )
                    for insert in inserts:
                        db.insertProduct( inserts[insert] )
                bar()


def main():

    items = ['galaxy','macbook', 'gaming', 'ipad', 'galaxy-tab', 'apple-watch']

    # initialize db sql
    dbo = database.DataBase( os.getenv('DB_SERVER'), os.getenv('DB'), os.getenv('USERNAME'), os.getenv('PASSWORD') )
    # only run once
    #seedingProcess( dbo )

    #helpers.fillHrefs()
    #helpers.fillReviews()
    #print('\n')
    #check if prices have changed and update the db
    print( f"******************** processing { sys.argv[1] } **********************\n" )
    print( f"START TIME : {datetime.now()} ")
    #print( colored( f"START TIME : {datetime.now()} " , 'green' ) )
    worker.checkPrices( sys.argv[1] )
    #print( colored( f"END TIME : {datetime.now()}\n" , 'red' ) )
    print( f"END TIME : {datetime.now()}\n")
    print( f"*************** completed processing { sys.argv[1] } *****************\n" )
if __name__=="__main__":
    main() 
