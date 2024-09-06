class Basket():
    '''Basket Class:
        This is used to collect BasketItems - containing Meals and Quantities
        This is then processed to create an Order once complete
    '''

    def __init__(self):
        self.__basket = []
        self.setBasketTotal(0)
        self.setMinOrderLevel(3)

    '''GETTERS AND SETTERS '''
    def setBasket(self,basket=None):
        self.__basket = basket

    def setBasketTotal(self,total=None):
        if total:
            self.__basketTotal = total
        else:
            self.__basketTotal = 0

    def setMinOrderLevel(self,minOrderLevel=0):
        self.__minOrderLevel = minOrderLevel


    def getBasket(self):
        return self.__basket

    def getBasketTotal(self):
        return self.__basketTotal

    def getBasketCount(self):
        return len(self.__basket)

    def getMinOrderLevel(self):
        return self.__minOrderLevel

    def addBasketTotal(self,cost):
        if cost:
            self.setBasketTotal(self.getBasketTotal()+cost)


    def addItem(self,basketItem=None):
        if basketItem:
            self.__basket.append(basketItem)
            self.addBasketTotal(basketItem.getCost())

    def displayBasket(self):
        print(f"\n{'-'*40}")
        print(f"{' '*10} Your Basket {' '*10}")
        print(f"{'-'*40}\n")

        for i, basketItem in enumerate(self.__basket, start=1):
            print(f"{i}. {basketItem.getMeal().getMealName()} x {basketItem.getQuantity()}")
            print(f"  Price: ${basketItem.getMeal().getMealPrice():.2f}\n")

        print(f"{'-'*40}")
        print(f"Total: ${self.getBasketTotal():.2f}")
        print(f"{'-'*40}\n")

    def removeItem(self, meal):
        for basket_item in self.__basket:
            if basket_item.getMeal() == meal:
                self.__basket.remove(basket_item)
                self.setBasketTotal(self.getBasketTotal() - basket_item.getCost())
                print("Item removed from basket.")
                return True
        print("Item not found in basket.")
        return False
    
    def updateQuantity(self, meal, new_quantity):
        for basket_item in self.__basket:
            if basket_item.getMeal() == meal:
                old_quantity = basket_item.getQuantity()
                basket_item.setQuantity(new_quantity)
                self.setBasketTotal(self.getBasketTotal() - (old_quantity - new_quantity) * basket_item.getMeal().getMealPrice())
                print("Quantity updated.")
                return True
        print("Item not found in basket.")
        return False


    def clearBasket(self):
        self.basket = []

    def checkMinOrderLevel(self):
        if self.getBasketCount() >= self.getMinOrderLevel():
            return True
        else:
            return False

class BasketItem():
    ''' BasketItem Class:
        Stores details about each meal in a basket, including quantities
    '''

    def __init__(self, meal=None, quantity=None):
        '''BasketItem Constructor: requeires a meal and quantity'''
        self.setMeal(meal)
        self.setQuantity(quantity)

    def getMeal(self):
        return self.__meal

    def getQuantity(self):
        return self.__quantity

    def setMeal(self,meal=None):
        self.__meal = meal

    def setQuantity(self,quantity=None):
        if quantity:
            self.__quantity = int(quantity)
        else:
            self.__quantity = 0

    def getCost(self):
        if self.getMeal():
            return self.getMeal().getMealPrice() * self.getQuantity()
        else:
            return 0

    def __str__(self):
        return f"Meal: {self.getMeal()}, Quantity: {self.getQuantity()}  Cost: ${self.getCost():.2f}"