# vietnambot.py

from Avatar import Avatar
from Customer import Customer
from Course import Course
from Database import Database
from menu import Menu
from SPXCafe import SPXCafe
from rapidfuzz import fuzz, process, utils
from Order import Order
from datetime import datetime, timedelta
from OrderItem import OrderItem
from Meal import Meal
from Basket import Basket, BasketItem

class VietnamBot:
    def __init__(self):
        self.avatar = Avatar("VietnamBot")
        self.customer = None
        self.cafe = SPXCafe()
        self.menu = Menu()
        self.basket = Basket() 

    def welcomeCustomer(self):
        print("Welcome to VietnamBot, your Vietnamese food online ordering service!")
        #self.avatar.say("Welcome to VietnamBot, your Vietnamese food online ordering service!")

    def identifyCustomer(self):
        username = input("\nWhat is your username? ")
        db = Database("SPXCafe.db")
        customerData = db.dbGetData(f"SELECT * FROM customer WHERE userName='{username}'")
        if customerData:
            self.customer = Customer(userName=username)
            print(f"Welcome back, {self.customer.userName}!")
            # self.avatar.say(f"Welcome back, {self.customer.userName}!")
        else:
            print("Sorry, we couldn't find a customer with that username.")
            # self.avatar.say("Sorry, we couldn't find a customer with that username.")
            print("Let's create a new account for you!")
            # self.avatar.say("Let's create a new account for you!")
            firstName = input("What is your first name? ")
            lastName = input("What is your last name? ")
            newUsername = input(f"Would you like to use '{firstName}{lastName}' as your username? (yes/no) ")
            if newUsername.lower() == "yes":
                newUsername = f"{firstName}{lastName}"
            else:
                newUsername = input("Enter a new username: ")
            newCustomer = Customer(userName=newUsername, firstName=firstName, lastName=lastName)
            newCustomer.save()
            self.customer = newCustomer
            print(f"Welcome, {self.customer.userName}! Your account has been created.")
            # self.avatar.say(f"Welcome, {self.customer.userName}! Your account has been created.")

    def showMenu(self):
        print("\nOur menu consists of:")
        self.menu.showCourses()
        # self.avatar.say("Our menu consists of starters, main course, and desserts. Would you like to hear more about a specific course?")
        user_input = input("Enter your choice: ")
        
        courses = self.menu.getCourses()
        closest_match = process.extractOne(user_input, courses, scorer=fuzz.token_sort_ratio)
        
        if closest_match and closest_match[1] > 50:
            course_name = closest_match[0]
            print(f"Here are our {course_name}:")
            self.menu.showMealsForCourse(course_name)
        else:
            print("Sorry, I didn't quite understand that. Please try again.")
            # self.avatar.say("Sorry, I didn't quite understand that. Please try again.")

#======================================================================================================================================================

    def takeOrder(self):
        print("\nWhat meal would you like to order? Please note that a minimum of 3 dishes must be ordered to proceed to checkout.")
        # self.avatar.say("What meal would you like to order? Please note that a minimum of 3 dishes must be ordered to proceed to checkout.")
        
        while True:
            user_input = input("Enter your choice, type 'menu' to view menu again, or type 'exit' to abandon order: ")
            
            if user_input.lower() == 'menu':
                self.showMenu()
                continue
            elif user_input.lower() == 'exit':
                confirm_exit = input("Are you sure you want to abandon your order? (yes/no): ")
                if confirm_exit.lower() == 'yes':
                    print("Order abandoned.")
                    self.avatar.say("Order abandoned.")
                    self.basket = Basket()
                    return
                else:
                    continue
            
            meals = Meal.findMeal(user_input)
            
            if meals:
                meal = meals[0]  # Use the first matching meal
                print(f"Great choice! You've selected {meal.getMealName()}.")
                # self.avatar.say(f"Great choice! You've selected {meal.getMealName()}.")
                
                meal_price = meal.getMealPrice()
                print(f"The price of {meal.getMealName()} is ${meal_price:.2f}.")
                # self.avatar.say(f"The price of {meal.getMealName()} is ${meal_price:.2f}.")
                
                quantity = int(input("How many would you like to order? "))
                
                # Check if the meal already exists in the basket
                for basket_item in self.basket.getBasket():
                    if basket_item.getMeal() == meal:
                        # If the meal exists, increment the quantity
                        basket_item.setQuantity(basket_item.getQuantity() + quantity)
                        print(f"Your order of {quantity} {meal.getMealName()}(s) has been added to your basket.")
                        # self.avatar.say(f"Your order of {quantity} {meal.getMealName()}(s) has been added to your basket.")
                        break
                else:
                    # If the meal doesn't exist, add a new BasketItem
                    basket_item = BasketItem(meal, quantity)
                    self.basket.addItem(basket_item)
                    print(f"Your order of {quantity} {meal.getMealName()}(s) has been added to your basket.")
                    # self.avatar.say(f"Your order of {quantity} {meal.getMealName()}(s) has been added to your basket.")
                
                self.basket.displayBasket()
                
                if self.basket.getBasketCount() >= self.basket.getMinOrderLevel():
                    while True:
                        print("\nYou have met the minimum order requirement. What would you like to do?")
                        user_input = input("Continue or finish ordering: ")
                        
                        options = ["Continue ordering", "Finish ordering"]
                        closest_match = process.extractOne(user_input, options, scorer=fuzz.token_sort_ratio)
                        
                        if closest_match and closest_match[1] > 30:
                            closest_match_option = closest_match[0]
                            if closest_match_option == "Continue ordering":
                                break
                            elif closest_match_option == "Finish ordering":
                                return
                        else:
                            print("Invalid choice. Please try again.")
                            self.avatar.say("Invalid choice. Please try again.")
            else:
                print("Sorry, I didn't quite understand that. Please try again.")
                self.avatar.say("Sorry, I didn't quite understand that. Please try again.")

#======================================================================================================================================================


    def viewOrder(self):
        orders = Order.getOrders(self.customer)
        if orders:
            print("\nYour Previous Orders:")
            print("-" * 80)
            combined_orders = {}
            for order in orders:
                order_items = order.getOrderItems()
                for order_item in order_items:
                    meal_name = order_item.getMeal().getMealName()
                    quantity = order_item.getQuantity()
                    if meal_name in combined_orders:
                        combined_orders[meal_name] += quantity
                    else:
                        combined_orders[meal_name] = quantity
            print(f"{'Order#':^10}{'Customer#':^10}{'Order Details':^60}")
            print("-" * 80)
            print(f"{'COMBINED':^10}{self.customer.getCustomerId():^10}")
            total = 0
            avatar_message = "Your previous orders are: "
            for meal_name, quantity in combined_orders.items():
                meal_price = Meal.findMeal(meal_name)[0].getMealPrice()
                subtotal = quantity * meal_price
                total += subtotal
                print(f"{'':^10}{'':^10}{meal_name:<30}{quantity:^10}{meal_price:^10.2f}{subtotal:^10.2f}")
                avatar_message += f"{quantity} {meal_name} at ${meal_price:.2f} each, "
            avatar_message = avatar_message[:-2]  # Remove the trailing comma and space
            avatar_message += f" with a total of ${total:.2f}."
            print("-" * 80)
            print(f"{'':^70}{'Total:':^10}{total:^10.2f}")
            print("-" * 80)
            self.avatar.say(avatar_message)
        else:
            print("You have no previous orders.")
            self.avatar.say("You have no previous orders.")

                    
    def viewBasket(self):
        if self.basket.getBasketCount() > 0:
            print("\nYour current basket:")
            self.basket.displayBasket()
            
            avatar_message = "Your current basket contains: "
            total = 0
            for basket_item in self.basket.getBasket():
                meal_name = basket_item.getMeal().getMealName()
                quantity = basket_item.getQuantity()
                meal_price = basket_item.getMeal().getMealPrice()
                total += quantity * meal_price
                avatar_message += f"{quantity} {meal_name} at ${meal_price:.2f} each, "
            avatar_message = avatar_message[:-2]  # Remove the trailing comma and space
            avatar_message += f" with a total of ${total:.2f}."
            self.avatar.say(avatar_message)
            
            while True:
                print("\nWhat would you like to do?")
                print("1. Remove an item")
                print("2. Update quantities")
                print("3. Continue to checkout")
                user_input = input("Enter your choice: ")
                
                threshold = 30
                remove_similarity = fuzz.ratio(user_input.lower(), "remove")
                update_similarity = fuzz.ratio(user_input.lower(), "update")
                checkout_similarity = fuzz.ratio(user_input.lower(), "checkout")
                if remove_similarity > update_similarity and remove_similarity > checkout_similarity and remove_similarity > threshold:
                    self.removeBasketItem()
                elif update_similarity > remove_similarity and update_similarity > checkout_similarity and update_similarity > threshold:
                    self.updateBasketQuantities()
                elif checkout_similarity > remove_similarity and checkout_similarity > update_similarity and checkout_similarity > threshold:
                    self.checkout()
                    break
                else:
                    print("Invalid choice. Please try again.")
                    # self.avatar.say("Invalid choice. Please try again.")
        else:
            print("\nYour basket is empty.")
            self.avatar.say("Your basket is empty.")

    def removeBasketItem(self):
        print("\nWhich item would you like to remove?")
        for i, basket_item in enumerate(self.basket.getBasket()):
            print(f"{i+1}. {basket_item.getMeal().getMealName()}")
        user_input = input("Enter the name of the item: ")
        
        threshold = 30
        meal_names = [basket_item.getMeal().getMealName() for basket_item in self.basket.getBasket()]
        closest_match = process.extractOne(user_input, meal_names, scorer=fuzz.token_sort_ratio)
        
        if closest_match and closest_match[1] > threshold:
            closest_match_meal_name = closest_match[0]
            print(f"Found match: {closest_match_meal_name}")
            
            # Find the basket item with the matching meal name
            for basket_item in self.basket.getBasket():
                if basket_item.getMeal().getMealName() == closest_match_meal_name:
                    print(f"Current quantity: {basket_item.getQuantity()}")
                    quantity_to_remove = int(input("How many would you like to remove? "))
                    
                    # Check if the quantity to remove is valid
                    if quantity_to_remove > 0 and quantity_to_remove <= basket_item.getQuantity():
                        # Update the quantity of the basket item
                        basket_item.setQuantity(basket_item.getQuantity() - quantity_to_remove)
                        print(f"Quantity updated: {basket_item.getQuantity()}")
                        
                        # If the quantity is 0, remove the item from the basket
                        if basket_item.getQuantity() == 0:
                            self.basket.removeItem(basket_item.getMeal())
                            print("Item removed from basket.")
                    else:
                        print("Invalid quantity. Please try again.")
                    break
            else:
                print("Item not found in basket.")
        else:
            print("No match found. Please try again.")
        
        # Display the updated basket
        self.viewBasket()


    def updateBasketQuantities(self):
        print("\nWhich item would you like to update?")
        for i, basket_item in enumerate(self.basket.getBasket()):
            print(f"{i+1}. {basket_item.getMeal().getMealName()}")
        user_input = input("Enter the name of the item: ")
        
        # Define the threshold for fuzzy matching (0-100)
        threshold = 30
        
        # Get the list of meal names in the basket
        meal_names = [basket_item.getMeal().getMealName() for basket_item in self.basket.getBasket()]
        
        # Find the closest match using fuzzy logic
        closest_match = process.extractOne(user_input, meal_names, scorer=fuzz.token_sort_ratio)
        
        if closest_match and closest_match[1] > threshold:
            closest_match_meal_name = closest_match[0]
            print(f"Found match: {closest_match_meal_name}")
            
            # Find the basket item with the matching meal name
            for basket_item in self.basket.getBasket():
                if basket_item.getMeal().getMealName() == closest_match_meal_name:
                    print(f"Current quantity: {basket_item.getQuantity()}")
                    new_quantity = int(input("Enter the new quantity: "))
                    
                    # Check if the new quantity is valid
                    if new_quantity > 0:
                        # Update the quantity of the basket item
                        self.basket.updateQuantity(basket_item.getMeal(), new_quantity)
                        print(f"Quantity updated: {new_quantity}")
                    else:
                        print("Invalid quantity. Please try again.")
                    break
            else:
                print("Item not found in basket.")
        else:
            print("No match found. Please try again.")
        
        # Display the updated basket
        self.viewBasket()

    def checkout(self):
        order = Order(customer=self.customer)
        order.save()
        
        for basket_item in self.basket.getBasket():
            order_item = OrderItem(order=order, meal=basket_item.getMeal(), quantity=basket_item.getQuantity())
            order_item.save()
        
        print("\nYour order has been saved successfully!")
        # self.avatar.say("Your order has been saved successfully!")
        self.basket = Basket()
        return


    def run(self):
        self.welcomeCustomer()
        self.identifyCustomer()
        options = {
            "View menu": self.showMenu,
            "Order food": self.takeOrder,
            "View previous orders": self.viewOrder,
            "View basket": self.viewBasket,
            "Exit": self.exitBot
        }

        while True:
            print("\nWhat would you like to do?")
            for i, option in enumerate(options.keys()):
                print(f"{i+1}. {option}")
            user_input = input("Enter your choice: ")

            closest_match = process.extractOne(user_input, options.keys(), scorer=fuzz.token_sort_ratio)

            if closest_match and closest_match[1] > 30:
                closest_match_option = closest_match[0]
                options[closest_match_option]()
            else:
                print("Invalid choice. Please try again.")
                self.avatar.say("Invalid choice. Please try again.")

    def exitBot(self):
        print("Thank you for using VietnamBot!")
        self.avatar.say("Thank you for using VietnamBot!")
        exit()

if __name__ == "__main__":
    vietnambot = VietnamBot()
    vietnambot.run()