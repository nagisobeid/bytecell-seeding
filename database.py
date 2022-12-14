import os
import pyodbc
#from dotenv import load_dotenv 
 
#load_dotenv()

class DataBase:
    def __init__( self, server, database, username, db_password ):
        self.server = server
        self.database = database
        self.username = username
        self.db_password = db_password
        self.cnxn = pyodbc.connect('DRIVER={ODBC Driver 18 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ db_password+';TrustServerCertificate=Yes')
        self.cursor = self.cnxn.cursor()
    
    def o2InsertProduct(self, product):
        #query = f"SELECT model, color, storage, condition, bcid FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
        query = f"IF NOT EXISTS ( select * from Products WHERE title = '{product.title}' AND model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}') \
                    BEGIN \
                        SET NOCOUNT ON\
                        INSERT INTO Products (model, color, storage, vendor, vendor_price, bc_price, isavailable, condition, bcid, title)\
                        VALUES ( '{product.model}','{product.color}','{product.storage}','{product.vendor}','{product.price}','{product.bcPrice}', \
                        '{product.isAvailable}', '{product.condition}', '{product.id}', '{product.title}') \
                        SELECT 0\
                    END\
                    ELSE ( select 1 )"
        
        self.cursor.execute(query)
        res = self.cursor.fetchone()
        self.cnxn.commit()
        if (res[0] == 0):
            print('INSERTED -> ' + str(product.id))
            return False
        elif (res[0] == 1):
            print('ALREADY IN DB')
            return True

    def insertProduct( self, product ):
        sql = f"exec [{self.database}].[dbo].[InsertProduct] { product['insertString'] };"
        values = tuple( product['insertValues'] )

        self.cursor.execute( sql, values )
        res = self.cursor.fetchone()
        self.cnxn.commit()
        return res[0]

    def insertLog( self, data ):
        #print('inserting log')
        #print(data['log'])
        sql = f"exec [{self.database}].[dbo].[InsertLog] { data['log']['insertString'] };"
        values = tuple( data['log']['insertValues'] )

        self.cursor.execute( sql, values )
        #res = self.cursor.fetchone()
        self.cnxn.commit()

    def updateCondition(self, product):
        query = f"UPDATE Products SET condition = '{product.condtion}' WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}'"

        self.cursor.execute(query)
        self.cnxn.commit()
       
    def updateVendorPrice(self, product):
        query = f"UPDATE Products SET Vendor_Price = '{product.price}' WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        self.cnxn.commit()
    
    def updateBCPrice(self, product):
        query = f"UPDATE Products SET BC_Price = '{product.bcPrice}' WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        self.cnxn.commit()
    
    def updateOldBCPrice(self, oldBCPrice):
        query = f"UPDATE Products SET Old_BC_price = '{oldBCPrice}' WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        self.cnxn.commit()

    def updateAvailability(self, product):
        query = f"UPDATE Products SET isavailable = '{product.isAvailable}' WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        self.cnxn.commit()
    
    def updateAvailabilityOfAllProductsWithSameBCID(self, product):
        query = f"UPDATE Products SET isavailable = '{product.isAvailable}', vendor_price = 0.0, bc_price = 0.0 WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}'"

        self.cursor.execute(query)
        self.cnxn.commit()
    
    def getVendorPrice(self, product):
        query = f"SELECT Vendor_Price FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        price = self.cursor.fetchone()
        return price[0]
        #self.cnxn.commit()
    
    def getBCPrice(self, product):
        query = f"SELECT BC_Price FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        price = self.cursor.fetchone()
        return price[0]
        #self.cnxn.commit()
    
    def getProduct(self, product):
        query = f"SELECT model, color, storage, condition, bcid FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        prod = self.cursor.fetchone()
        return prod[0]
    
    def getProductsWithUnavailableCondition(self, product):
        query = f"SELECT model, color, storage, condition, bcid FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}'"

        self.cursor.execute(query)
        prods = self.cursor.fetchall()
        return prods
    
    def getAvailability(self, product):
        query = f"SELECT isavailable FROM Products WHERE model = '{product.model}' AND color = '{product.color}' \
                    AND storage = '{product.storage}' AND condition = '{product.condition}'"

        self.cursor.execute(query)
        availability = self.cursor.fetchone()
        return availability[0]
        #self.cnxn.commit()
        
