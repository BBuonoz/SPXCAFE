import Meal
import Order
from SPXCafe import SPXCafe

class OrderItem(SPXCafe):
    '''OrderItem Class extend SPXCafe Class'''

    def __init__(self, orderItemId=None, order=None, meal=None, quantity=None):
        '''
        # Constructor Method
        # Creates a blank orderItem if no orderItemId
        # else Retrieves existing orderItem from Database
        '''

        super().__init__()

        self.setOrderItemId(orderItemId)
        self.setOrder(order)
        self.setMeal(meal)
        self.setQuantity(quantity)
        # save meal price when first adding orderItem - to record historical value of price
        if self.getMeal():
            self.setMealPrice(self.getMeal().getMealPrice())

        # RETRIEVE EXISTING from Database IF OrderItem PK is passed in
        if self.existsDB():
            if not self.setOrderItem(self.getOrderItemId()):
                print(f"Existing Order Item: Order Item Id <{self.__orderItemId}> is invalid")


    def existsDB(self):
        ''' Check if OrderItem exists in Database '''
        retcode=False

        if self.getOrderItemId():
            sql = f"SELECT count(*) AS count FROM orderItems WHERE orderItemId={self.getOrderItemId()}"
            # print(sql)
            countData = self.dbGetData(sql)
            if countData:
                for countData in self.dbGetData(sql):
                    count = int(countData['count'])
                if count > 0:
                    retcode = True
        return retcode

    def setOrderItem(self, orderItemId):
        '''Gets the Order Item details from the database and sets the Object attributes with those values'''

        retCode = False
        if orderItemId:
            sql = f"SELECT orderItemId, orderId, mealId, quantity, mealPrice FROM orderItems WHERE orderItemId = {orderItemId}"
            orderItemData = self.dbGetData(sql)
            if orderItemData:
                for orderItem in orderItemData:
                    self.setOrderItemId(orderItem['orderItemId'])
                    self.setOrder(Order.Order(orderItem['orderId']))
                    self.setMeal(Meal.Meal(orderItem['mealId']))
                    # self.setOrderId(orderItem['orderId'])
                    # self.setMealId(orderItem['mealId'])
                    self.setQuantity(orderItem['quantity'])
                    self.setMealPrice(orderItem['mealPrice'])
                    print(f"Retrieve Order Item: {self.__orderItemId}, {self.__order.getOrderId()}, {self.__meal.getMealId()}, {self.__quantity}, {self.__mealPrice}")
                retCode = True
        return retCode

    def save(self):
        '''Saves Order Item to datbase - either as an Update for existing orderItem or an Insert of a new OrderItem (no orderItemId set yet)'''

        retCode = False
        # validate fields before saving
        if not(self.__order.getOrderId() and self.__meal.getMealId() and self.__quantity and self.__mealPrice):
            print("OrderItem: Save: Missing mandatory data")
            print(self)
        else:
            # print(f"Saving Order Item: {self.__orderItemId}, {self.__order.getOrderId()}, {self.__meal.getMealId()}, {self.__quantity}, {self.__mealPrice}")
            # Update Existing
            if self.__orderItemId:
                sql = f"UPDATE orderItems SET orderId={self.__order.getOrderId()}, mealId={self.__meal.getMealId()}, quantity={self.__quantity},mealPrice={self.__mealPrice} WHERE orderItemId = {self.__orderItemId}"
                self.dbChangeData(sql)
                retCode = True
            else:
            # Insert New
                sql = f"INSERT INTO orderItems (orderId, mealId, quantity, mealPrice) VALUES {self.__order.getOrderId(), self.__meal.getMealId(), self.__quantity, self.__mealPrice}"
                # print(f"Insert SQL: <{sql}>")
                self.setOrderItemId(self.dbPutData(sql))
                retCode = True
        return retCode

    def delete(self):
        '''Delete the current OrderItem from database '''

        if self.getOrderItemId():
            sql = "DELETE FROM orderItems WHERE orderItemId = {self.getOrderItemId()}"
            self.dbChangeData(sql)
            # Now initialise object to prevent further updates
            self.setOrderItemId(None)
            self.setOrder(None)
            self.setMeal(None)
            # self.setOrderId(None)
            # self.setMealId(None)
            self.setQuantity(None)
            self.setMealPrice(None)

    def display(self):
        '''formal display of orderItem'''
        # print("DISPLAY ORDER ITEM")
        # print(self)
        print(f"<{self.__order.getOrderId():2d}-{self.getOrderItemId():2d}> ({self.__meal.getMealId():2d}) {self.__meal.getMealName():30s} - ${self.getMealPrice():5.2f} x {self.getQuantity():2d} = ${(self.getMealPrice()*self.getQuantity()):6.2f}")

    def __str__(self):
        ''' "To String" Method - returns an object as a string for human reading
'''
        return f"Order Item: {self.getOrderItemId():2d} - OrderId: {self.__order.getOrderId():2d}, MealId: {self.__meal.getMealId():2d} - Quantity: {self.__quantity:2d} - MealPrice: ${self.__mealPrice:6.2f}"

    # Get Lists of OrderItems for an Order
    # - FACTORY METHOD THAT RETURNS A LIST OF INSTANCES OF THIS CLASS - takes the cls as the first parameter
    @classmethod
    def getOrderItems(cls, order):
        '''
        input:      Order instance
        process:    Get order items for Order and build a OrderItem object list to return
        output:     a list of orderItems
        '''
        sql = f"SELECT orderItemId, orderId, mealId, quantity, mealPrice FROM orderItems WHERE orderId = {order.getOrderId()} ORDER BY orderItemId"

        orderItemsData = SPXCafe().dbGetData(sql)

        orderItems = []
        for orderItem in orderItemsData:
            newOrderItem = cls.__new__(cls)

            newOrderItem.setOrderItemId(orderItem['orderItemId'])
            newOrderItem.setOrder(order)
            newOrderItem.setMeal(Meal.Meal(mealId=orderItem['mealId']))
            # newOrderItem.setOrderId(orderItem['orderId'])
            # newOrderItem.setMealId(orderItem['mealId'])
            newOrderItem.setQuantity(orderItem['quantity'])
            newOrderItem.setMealPrice(orderItem['mealPrice'])
            # print(f"Class :Retrieve Order Item: {newOrderItem.orderItemId}, {newOrderItem.orderId}, {newOrderItem.mealId}, {newOrderItem.quantity}, {newOrderItem.mealPrice}")

            orderItems.append(newOrderItem)
        return orderItems

    @classmethod
    def getOrderItem(cls, customer, meal):
        sql = f"SELECT * FROM orderItems WHERE orderId = {customer.getCurrentOrder().getOrderId()} AND mealId = {meal.getMealId()}"
        order_item_data = SPXCafe().dbGetData(sql)
        if order_item_data:
            return cls(orderItemId=order_item_data[0][0], order=customer.getCurrentOrder(), meal=meal, quantity=order_item_data[0][3])
        else:
            return None

    ## Object GETS/SETS methods

    '''GETTERS'''
    def getOrderItemId(self):
        return self.__orderItemId

    # def getOrderId(self):
    #     return self.__order.getOrderId()

    # def getMealId(self):
    #     return self.__meal.getMealId()

    def getOrder(self):
        return self.__order

    def getMeal(self):
        return self.__meal

    def getQuantity(self):
        return self.__quantity

    def getMealPrice(self):
        return self.__mealPrice

    '''SETTERS'''
    def setOrderItemId(self, orderItemId):
        self.__orderItemId = orderItemId

    # def setOrderId(self, orderId):
    #     self.__order.getOrderId() = orderId

    def setOrder(self, order=None):
        # If an Order object exists set it and deriver orderId
        if order:
            self.__order = order
            # self.setOrderId(order.getOrderId())
        # elif self.getOrderId():
        #     # if an order object not exist but we have
        #     # orderId - e.g. when retrieved from DB - then
        #     # create an order object
        #     self.__order = Order.Order(orderId=self.getOrderId())
        else:
            self.__order = None

    # def setMealId(self, mealId):
    #     self.__meal.setMealId(mealId)

    def setMeal(self, meal=None):
        if meal:
            self.__meal = meal
            # self.setMealId(self.__meal.getMealId())
        # elif self.getMealId():
        #     self.__meal = Meal.Meal(mealId=self.getMealId())
        else:
            self.__meal = None

    def setQuantity(self, quantity):
        self.__quantity = quantity

    def setMealPrice(self, mealPrice):
        self.__mealPrice = mealPrice


def main():
    '''Test Harness for the OrderItem Class'''
# retrieve an order
    orderItemId = 1
    print(f"Retrieve Order Item {orderItemId}:")
    orderItem = OrderItem(orderItemId=orderItemId)
    orderItem.display()
#    print(orderItem)

#     print("Update Order Item")
#     orderItem.setMealPrice(3.99)
#     orderItem.save()
#     orderItem.display()
# #    print(orderItem)

# create a new order item for an order and meal
    # order = Order.Order(orderId=5)
    # meal = Meal.Meal(mealId=1)

    # print("Create new OrderItem")
    # orderItem = OrderItem(order=order, meal=meal, quantity=2)
    # orderItem.save()
    # orderItem.display()
#    print(orderItem)

if __name__ == "__main__":
    main()