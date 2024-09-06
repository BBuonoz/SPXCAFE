import sqlite3
from Database import Database
from rapidfuzz import process, fuzz, utils
from Avatar import Avatar

class Menu(Database):

    def __init__(self):
        super().__init__("SPXCafe.db")
        self.courses = None

    def getCourses(self):
        courses = []
        sql = "SELECT courseId, courseName from courses ORDER BY courseId"
        coursesData = self.dbGetData(sql)
        if coursesData:
            for course in coursesData:
                courseName = course['courseName']
                courses.append(courseName)
        else:
            print("No courses")
        return courses

    def showCourses(self):
        self.courses = self.getCourses()
        print("Courses List:")
        for courseName in self.courses:
            print(f"> {courseName.title()}")

    # retrieve Meals for a Course or all Courses
    def getMealsForCourse(self,courseName=None):
        self.courses = self.getCourses()
        if courseName not in self.courses:
            print(f"Error: Course {courseName} does not exist")
        else:
            self.meals = {}  # empty dictionary
            sql = f'''
            SELECT m.mealName, m.mealPrice
            FROM meals AS m, courses AS c
            WHERE
                c.courseID = m.courseId
            AND c.courseName = '{courseName}'
            ORDER BY m.mealName
            '''
            # sql = f"SELECT m.mealName, m.mealPrice FROM meals AS m, courses AS c WHERE c.courseID = m.courseId AND c.courseName = '{courseName}' ORDER BY m.mealName"

            mealsData = self.dbGetData(sql)

            if mealsData:
                for meal in mealsData:
                    mealName = meal['mealName']
                    mealPrice = meal['mealPrice']
                    self.meals[mealName] = mealPrice
            else:
                print(f"No Meals for {courseName.title()} course")
            return self.meals

    def getMealByName(self, meal_name):
        for meal in self.meals:
            if meal.getMealName() == meal_name:
                return meal
        return None

    def findMeal(self, searchMeal=None):
        if not searchMeal:
            print("Please provide a meal name to search for.")
            return

        all_meals = {}
        for course in self.getCourses():
            self.showMealsForCourse(course)
            course_meals = self.getMealsForCourse(course)
            all_meals.update(course_meals)

        found_meals = [meal for meal in all_meals if searchMeal.lower() in meal.lower()]
        if not found_meals:
            print(f"No meals found containing '{searchMeal}'")
        else:
            print(f"Meals containing '{searchMeal}':")
            for meal in found_meals:
                print(f"> {meal.title()} - ${all_meals[meal]:.2f}")    
        

    def showMealsForCourse(self, courseName=None):
        if courseName:
            self.meals = self.getMealsForCourse(courseName)
            print(f"------- Course: {courseName.title():8s} --------")
            for mealName in self.meals:
                mealPrice = self.meals[mealName]
                print(f">>> {mealName.title():20s} ${mealPrice:.2f}")
        else:
            print(f"Error: Course not provided" )

    def showMeals(self):
        print("--------- MENU ---------")
        self.courses = self.getCourses()
        for courseName in self.courses:
            self.showMealsForCourse(courseName)

    def insertMeal(self, courseName, mealName, mealPrice):
        self.courses = self.getCourses()
        mealId = None
        if courseName in self.courses:
            sql = f"SELECT courseId FROM courses WHERE courseName = '{courseName.lower()}'"
            courseId = self.dbGetData(sql)[0]['courseId']
            print(sql, courseId)
            sql = f"INSERT INTO meals (mealName, mealPrice, courseId) VALUES ('{mealName.lower()}',{mealPrice},{courseId})"
            print(sql)
            mealId = self.dbPutData(sql)
            print("new meal id",mealId)
        return mealId

    def deleteMeal(self, courseName, mealName):
        self.courses = self.getCourses()
        mealId = None
        if courseName in self.courses:
            sql = f"SELECT courseId FROM courses WHERE courseName = '{courseName.lower()}'"
            courseId = self.dbGetData(sql)[0]['courseId']
            print(sql, courseId)
            sql = f"DELETE FROM meals WHERE mealName = '{mealName.lower()}' AND courseId = {courseId}"
            print(sql)
            mealId = self.dbChangeData(sql)
            print("new meal id",mealId)
        return mealId

def main():
    dbname = "SPXCafe.db"
    m = Menu()
    m.showCourses()
    m.showMeals()
    # m.insertMeal("starter","prawn cocktail",5.40)
    # m.showMeals()
    # m.deleteMeal("starter","prawn cocktail")
    # m.showMeals()

    waiter = Avatar("luigi")
    print(f"{",".join(m.getCourses())}")
    waiter.say(m.showCourses)
    choice = waiter.listen(f"Please choose a course from this list : {",".join(m.getCourses())}")
    waiter.say(f"You choose: {choice}")

    (course, confidence, index) = process.extractOne(choice, m.getCourses(), scorer=fuzz.partial_ratio, processor=utils.default_process)

    if confidence > 50:
        waiter.say(f"You chose: {course}. Here is the menu for that course.")
    (m.getMealsForCourse(choice))

    meals = list(m.getMealsForCourse(course).keys())
    print(meals)
    meal = waiter.listen(f"Which meal do you want to order? ")

if __name__=="__main__":
    main()