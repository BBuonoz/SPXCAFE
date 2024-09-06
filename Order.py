from SPXCafe import SPXCafe
import OrderItem
import Customer
# from Basket import Basket
from datetime import datetime

class Order(SPXCafe):
    '''
        Order Class:  Stores Order details for a Customer
    '''

    # def __init__(self,orderId=None, orderDate=None, customerId=None):
    def __init__(self,orderId=None, orderDate=None, customer=None):
        '''
            Constructor method
            - database data is retrieved into order object on construction if an orderId is provided
            - otherwise a new object is created and loaded with attribute information passed on construction
            - Note: a list of OrderItem objects are also retrieved - if they exist in the database.
        '''
        super().__init__()

        self.setOrderId(orderId)
        self.setOrderDate(orderDate)
        self.setCustomer(customer)
        self.setOrderItems()

        # If order exists, then get attributes from Database
        if self.existsDB():
            if not self.setOrder(self.__orderId):
                print(f"Existing Order: Order Id <{self.getOrderId()}> is invalid ")

    def existsDB(self):
        '''Checks if order exists in database'''
        retcode=False

        if self.getOrderId():
            sql = f"SELECT count(*) AS count FROM orders WHERE orderId={self.getOrderId()}"
            # print(sql)
            countData = self.dbGetData(sql)
            if countData:
                for countData in self.dbGetData(sql):
                    count = int(countData['count'])
                if count > 0:
                    retcode = True
        return retcode


    ##  DATABASE GETS/SETS ##
    def setOrder(self, orderId):
        '''
            Set Order - retrieves data from database into the Object Attributes
            for an OrderId if exists.

            Returns True or False if DB data found or not.
        '''
        retCode = False
        print(f"Getting order: {orderId}")
        if orderId:
            sql = f"SELECT orderId, orderDate, customerId FROM orders WHERE orderId = {orderId}"
            print(sql)
            orderData = self.dbGetData(sql)  # should only be one
            if orderData:
                for order in orderData:
                    self.setOrderId(order['orderId'])
                    # self.setCustomerId(order['customerId'])
                    self.setCustomer(Customer.Customer(customerId=order["customerId"]))
                    self.setOrderDate(order['orderDate'])

                    # Using OOP Aggregation - we store a list of OrderItem objects with the Order.
                    # information for OrderItem is delegated to the OrderItem Objects
                    print("Getting orderitems - passing Order object")
                    self.setOrderItems(OrderItem.OrderItem.getOrderItems(self))
                retCode = True

        return retCode

    def save(self):
        ''' Save Order Method:
            Saves the Order details back to the database
            If existing Order: then UPDATES the data in the database
            If not existing Order: then INSERTS the data into database

            returns True or False if successful updated or inserted
        '''
        retcode = False
        # validate compulsory data before saving
        if not (self.getOrderDate() and self.getCustomer()):
            print("Order: Save: missing mandatory data - orderDate or Customer")
            print(self)
        # if orderId exists - then update record otherwise insert new record
        else:
            # Insert NEW
            if self.__orderId is None:
                sql = f"INSERT INTO orders (customerId, orderDate) VALUES ({self.__customer.getCustomerId()},'{self.getOrderDate()}')"
                self.setOrderId(self.dbPutData(sql))
                retcode = True
            else:
                # Update Existing
                sql = f"UPDATE orders SET customerId={self.__customer.getCustomerId()}, orderDate='{self.getOrderDate()}' WHERE orderId = {self.getOrderId()}"
                self.dbChangeData(sql)
                retcode = True

        return retcode

    def __str__(self):
        ''' returns object as a string for human reading
        '''
        if self.getCustomer():
            return f"Order#: {self.getOrderId():2d} - Cust#: {self.getCustomer().getCustomerId():2d} - Order Date: '{self.getOrderDateF()}'" if self.getOrderId() else f"Order#: NEW - Cust#: {self.getCustomer().getCustomerId():2d} - Order Date: '{self.getOrderDateF()}'"
        else:
            return f"Order#: {self.getOrderId():2d} - No Customer - Order Date: '{self.getOrderDateF()}'" if self.getOrderId() else f"Order#: NEW - No Customer - Order Date: '{self.getOrderDateF()}'"

    def display(self):

        print("="*67)
        print(self)
        if self.__orderItems:
            for orderItem in self.__orderItems:
                orderItem.display()
            print("="*67)
            print(f"{' '*46} Order Total: ${self.getOrderTotal():6.2f}")
        else:
            print(f"{"-"*25} No Order Items {"-"*25}")

    # Get Lists of Orders for a Customer
    # - FACTORY METHOD THAT RETURNS A LIST OF INSTANCES OF THIS CLASS - takes the cls as the first parameter
    @classmethod
    def getOrders(cls, customer):

        sql = "SELECT orderId, orderDate, customerId FROM orders "
        if customer.getCustomerId():
            sql += f"WHERE customerId = {customer.getCustomerId()} "
        sql += "ORDER BY orderDate, orderId"
        ordersData = SPXCafe().dbGetData(sql)

        # Build a list of Order objects and return them
        orders = []
        for order in ordersData:
            newOrder =cls.__new__(cls)
            newOrder.setOrderId(order['orderId'])
            newOrder.setOrderDate(order['orderDate'])
            newOrder.setCustomer(customer) # bidirectional pointer to customer object
            newOrder.setOrderItems(OrderItem.OrderItem.getOrderItems(order=newOrder))
            orders.append(newOrder)
        return orders


    ## Object GETS/SETS
    def getOrderId(self):
        return self.__orderId

    def getCustomer(self):
        '''return customer object related to this order'''
        return self.__customer

    def getCustomerId(self):
        # return self.__customerId
        return self.__customer.getCustomerId()

    def getOrderDate(self):
        ''' get raw order date as YYYY-MM-DD '''
        return self.__orderDate

    def getOrderDateF(self):
        '''get formatted order date as DD MMMM YYYY'''
        return datetime.strptime(self.getOrderDate(), "%Y-%m-%d").strftime("%d %b %Y")
        # return self.__orderDate

    def getOrderItems(self):
        return self.__orderItems

    def getOrderTotal(self):
        total = 0
        if self.__orderItems:
            for orderItem in self.__orderItems:
                total += orderItem.getMealPrice() * orderItem.getQuantity()
        return total

    #-----------------------------------
    def setOrderId(self,orderId):
        self.__orderId = orderId

    def setCustomer(self,customer=None):
        '''store customer object for order - use customer id if no customer object '''
        if customer:
            self.__customer = customer
        #     self.setCustomerId(self.__customer.getCustomerId())
        # elif self.__customer.getCustomerId():
        #     self.__customer = Customer.Customer(customerId=self.__customer.getCustomerId())
        else:
            self.__customer = None

    # def setCustomerId(self, customerId=None):
    #     self.__customerId = customerId

    def setOrderDate(self,orderDate):
        ''' Set the order date - if missing default to today '''
        if orderDate:
            self.__orderDate = orderDate
        else:
            # Default to today's date for the order
            self.__orderDate = datetime.today().strftime('%Y-%m-%d')

    def setOrderItems(self,orderItems=None):
        '''
            Store a list of OrderItem objects with Order or empty list.
            Note: OrderItems List is retrieved by calling OrderItem Factory Method called getOrderItems()
        '''
        if orderItems:
            self.__orderItems = orderItems
        else:
            self.__orderItems = []
        # print(f"Set Order Items: {self.__orderItems}")

    def addBasket(self, basket):
        '''For each basketItem add an orderItem - then refresh the orderitems list for this order'''
        if basket:
            for basketItem in basket.getBasket():
                self.addOrderItem(basketItem)
        # rebuild all the order items for this Order
        self.setOrderItems(OrderItem.OrderItem.getOrderItems(self))

    def addOrderItem(self,basketItem=None):
        '''For each basketItem - add an OrderItem object and save to DB '''
        meal        = basketItem.getMeal()
        quantity    = basketItem.getQuantity()
        orderItem   = OrderItem.OrderItem(order=self, meal=meal, quantity=quantity)
        orderItem.save()


def main():
    '''Test Harness for this class'''
    # retrieve an order
    print("Getting Order 2 details")
    order = Order(orderId=2)
    print(order)
    order.display()

# create a new order
    print("Creating NEW order")
    customer = Customer.Customer(customerId=7)
    order = Order(customer=customer)
    print(order)


if __name__ == "__main__":
    main()