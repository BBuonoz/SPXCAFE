# from order import Order
# from OrderItem import OrderItem
from SPXCafe import SPXCafe
from Database import Database

class Customer(SPXCafe):
    '''Customer Class'''

    def __init__(self, userName=None, customerId=None,firstName=None,lastName=None):
        ''' Constructor Method:
            Arguments:
                - must be either userName or customerId if existing
                - no customerId if new Customer requested
                - first name and last name can be passed in constructor to update or insert
                - more
        '''
        super().__init__()

        self.setCustomerId(customerId)
        self.setUserName(userName)
        self.setFirstName(firstName)
        self.setLastName(lastName)
        # self.setOrders()

        if self.existsDB():
            self.setCustomer()


    # ------------ set up customer object data ------------

    def existsDB(self):
        '''Check if object already exists in database'''
        retcode = False
        sql = None
        if self.getCustomerId():
            sql = f"SELECT count(*) AS count FROM customer WHERE customerId={self.getCustomerId()}"
            # print(sql)
        elif self.getUserName():
            sql = f"SELECT count(*) AS count FROM customer WHERE userName='{self.getUserName()}'"
        if sql:
            countData = self.dbGetData(sql)
            if countData:
                for countRec in countData:
                    count = int(countRec['count'])
                if count > 0:
                    retcode = True
        return retcode

    @classmethod
    def findCustomer(cls, userName):
        ''' Uses the Username to find a customer and reutrn a Customer object matching it'''
        customer = None
        spxcafe = SPXCafe
        if userName:
            sql = f"SELECT cout(*) AS count FROM customer WHERE userName='{userName}'"
            if sql:
                countData = spxcafe.dbGetData(sql)
                if countData:
                    for countRec in countData:
                        count = int(countRec['count'])
                    if count > 0:
                        # create a customer object for the username if found
                        customer = Customer(userName=userName)
        return customer


    def setCustomer(self,userName=None,customerId=None):
        ''' Creates Customer Object from database info
            Arguments: either userName or customerId
        '''
        retcode = False
        if userName:
            self.setUserName(userName)
        if customerId:
            self.customerId(customerId)
        customerData = None
        if self.getCustomerId():  #customer must exist
            sql = f'''
                SELECT customerId, userName, firstName, lastName
                FROM customer
                WHERE customerId = {self.getCustomerId()}
                ORDER BY customerId
            '''
        # either NEW customer or EXISTING get using userName
        elif self.getUserName():
            sql = f'''
                SELECT customerId, userName, firstName, lastName
                FROM customer
                WHERE userName = '{self.getUserName()}'
                ORDER BY customerId
            '''
        # print(sql)
        customerData = self.dbGetData(sql)


        if customerData:
            # Exiting Customer - should only be ONE customer
            for customer in customerData:
                self.customerId = customer['customerId']
                self.userName   = customer['userName']
                self.firstName  = customer['firstName']
                self.lastName   = customer['lastName']
                # Call ORDER factory method to return a list of Order objects/instances - pass self to it
                # self.setOrders(Order.getOrders(self))
                retcode = True

        return retcode

    def save(self):
        try:
            if self.existsDB():
                sql = f'''UPDATE customer SET
                    customerId = {self.getCustomerId()},
                    userName = '{self.getUserName()}',
                    firstName = '{self.getFirstName()}',
                    lastName = '{self.getLastName()}'
                WHERE customerId={self.getCustomerId()}'''
                self.dbChangeData(sql)
                print("Updated existing customer data")
            else:
                sql = f'''INSERT INTO customer 
                    (userName, firstName, lastName) VALUES
                    ('{self.getUserName()}','{self.getFirstName()}','{self.getLastName()}')
                    '''
                # print(sql)
                self.customerId = self.dbPutData(sql)
                print(f"Customer saved: {self.getUserName()} ({self.getCustomerId()})")
        except Exception as e:
            raise  # re-raise the exception to propagate the error
        
    # ----- get/sets customer data  -------

    def getCustomerName(self):
        ''' get the customer full name for reporting, display etc'''
        return f"{self.firstName} {self.lastName}"

    def getFirstName(self):
        return f"{self.firstName}"

    def getLastName(self):
        return f"{self.lastName}"

    def getCustomerId(self):
        return self.customerId

    def getUserName(self):
        return self.userName

    # def getOrders(self):
    #     '''return a list of order obects for this customer'''
    #     return self.orders

    def setCustomerId(self,customerId):
        self.customerId = customerId

    def setUserName(self,userName):
        self.userName = userName

    def setFirstName(self,firstName):
        self.firstName = firstName

    def setLastName(self,lastName):
        self.lastName = lastName

    # def setOrders(self,orders=None):
    #     '''orders contain a list of existing orders or an empty list'''
    #     if orders:
    #         self.orders = orders
    #     else:
    #         self.orders = []

    # ----- formatted displays -------
    # str function allows you to simply print(customerInstance)
    def __str__(self):
        return f"Customer: ({self.getCustomerId():2d}) - <{self.userName}> {self.getFirstName()} {self.getLastName()} "

    # this requires customerInstance.displayCustomer()
    def display(self):
        '''formal display of the customer'''
        print(f"{"-"*25} Customer Details  {"-"*25}")
        print(f"Customer: {self.getCustomerId()}")
        print(f"Name: <{self.getUserName()}> {self.getCustomerName():50s}")
        # print(self)

    # # Go through list of orders and
    # # use the Order object to print itself
    # def displayOrders(self):
    #     self.display()

    #     heading = " Customer Order History  "
    #     print(f"\n{"-"*22}{heading}{"-"*22}\n")
    #     if self.orders:
    #         for order in self.orders:
    #             order.display()
    #     else:
    #         print("Customer: No orders for customer")

    # ----- Adhoc methods

    # def newCustomerOrder(self,orderDate=None):
    #     return

    # def addOrder(self, order=None):
    #     self.orders.append(order)


def main():

    bloggs = Customer("bloggs")
    bloggs.display()
    # bloggs.displayOrders()

    #new customer called jim jones
    jones=Customer(userName="jonesj2",firstName="Jim",lastName="Jones")
    jones.save()
    jones.display()

    # orders = jones.getOrders()
    # for order in orders:
    #     order.display()

if __name__=="__main__":
    main()