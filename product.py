class Product:
    def __init__(self, id, model, color, storage, availability, vendor, title):
        self.id = id
        self.model = model
        self.color = color
        self.storage = storage 
        self.isAvailable = availability
        self.price = None
        self.condition = None
        self.bcPrice = None
        self.vendor = vendor
        self.title = title
        #self.bcid = None

    def updatePrice(self, price):
        self.price = price
        self.setByteCellPrice(price)

    def updateCondition(self, condition):
        self.condition = condition
    
    def updateIsAvailable(self, isAvailable):
        self.isAvailable = isAvailable
    
    def setByteCellPrice(self, price):
        if price != None:
            newPrice = (price*.08)+price
            self.bcPrice = round(newPrice,2)
        elif price == None:
            self.bcPrice = None

    def updateVendor(self, vendor):
        self.vendor = vendor


class ConditionData:
    def __init__(self, title, condition, price, available):
        self.title = title
        self.condition = condition
        self.price = price
        self.available = available