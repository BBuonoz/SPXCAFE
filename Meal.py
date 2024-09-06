from SPXCafe import SPXCafe
import Course

class Meal(SPXCafe):
    ''' Meal Class '''

    def __init__(self,mealId=None,mealName=None,mealPrice=None,courseId=None,course=None):

        super().__init__()

        self.setMealId(mealId)
        self.setMealName(mealName)
        self.setMealPrice(mealPrice)
        self.setCourseId(courseId)
        self.setCourse(course)


        # This checks if Meal already exists...if so, just load it.
        if self.existsDB():
            if not self.setMeal():
                print(f"Meal: Meal Id <{self.getMealId()}> is invalid ")
        else:
            self.save()

    def setMeal(self, mealId=None):
        '''Set the Meal Attributes with values from Database for a mealId '''
        retcode = False
        if mealId:
            self.setMealId(mealId)

        if self.getMealId():
            sql = f"SELECT mealId, mealName, mealPrice, courseId FROM meals WHERE mealId = {self.getMealId()}"

            mealData = self.dbGetData(sql)
            for meal in mealData:
                self.setMealId(meal['mealId'])
                self.setMealName(meal['mealName'])
                self.setMealPrice(meal['mealPrice'])
                self.setCourseId(meal['courseId'])
                ####
                self.setCourse()
            retcode = True
        return retcode

    # Getters/Setters of Attributes

    def setMealId(self,mealId=None):
        self.__mealId = mealId

    def setMealName(self,mealName=None):
        self.__mealName = mealName

    def setMealPrice(self,mealPrice=None):
        self.__mealPrice = mealPrice

    def setCourseId(self,courseId=None):
        self.__courseId = courseId

    #############
    def setCourse(self, course=None):
        '''Save the owning Course for this Meal - bi-directional association'''
        if course:
            self.__course = course
            self.setCourseId(self.__course.getCourseId())  #################
        else:
            if self.getCourseId():
                course = Course.Course(courseId=self.getCourseId())
                self.setCourse(course)
            else:
                self.__course = None

    def getMealId(self):
        return self.__mealId

    def getMealName(self):
        return self.__mealName

    def getMealPrice(self):
        return self.__mealPrice

    def getCourseId(self):
        return self.__courseId

    def getCourse(self):
        return self.__course

    def __str__(self):
        '''Return a stringified version of object for print functions
            - may be same/different from display() method'''
        return f"Meal: <{self.getCourseId():2d}-{self.getMealId():2d}> {self.getMealName().title():20s} ${self.getMealPrice():5.2f}"

    def display(self):
        '''Formal display Meal'''
        print(f"Meal: <Course:{self.getCourseId():2d} {self.getCourse().getCourseName().title()}, Meal:{self.getMealId():2d}> {self.getMealName().title():20s} ${self.getMealPrice():5.2f}")

    # Database driven Methods

    def existsDB(self):
        '''Check if object already exists in database'''
        retcode = False
        # Use Primary Key to check if the Meal exists in DB
        if self.getMealId():
            sql = f"SELECT count(*) AS count FROM meals WHERE mealId={self.getMealId()}"
            # print(sql)
            countData = self.dbGetData(sql)
            if countData:
                for countRec in countData:
                    count = int(countRec['count'])
                if count > 0:
                    retcode = True
        return retcode

    def save(self):
        '''Save meal data back to the database'''

        if self.getCourse():
            self.setCourseId(self.getCourse().getCourseId())

        if self.existsDB():
            sql = f'''UPDATE meals SET
                mealId={self.getMealId()},
                mealName='{self.getMealName()}',
                mealPrice={self.getMealPrice()},
                courseId={self.getCourseId()}
                WHERE mealId={self.getMealId()}
            '''
            self.dbChangeData(sql)
        else:
            sql = f'''
                INSERT INTO meals
                (mealName, mealPrice, courseId)
                VALUES
                ('{self.getMealName()}', {self.getMealPrice()}, {self.getCourseId()})
            '''
            # Save new primary key
            self.setMealId(self.dbPutData(sql))

    def delete(self):
        '''
            Delete meal record from database
            NOTE:
            -  This does not get rid of the Meal instance in Python automatically - which may cause errors if someone tries to update the instance and db record does not exist.\n
            -  This meal object also exists in Associations and these relationships are not removed automatically.
        '''
        sql = f'''
            DELETE FROM meals
            WHERE
                mealId = {self.getMealId()}
        '''
        # print(sql)
        SPXCafe.dbChangeData(sql)

    @classmethod
    def getMeals(cls,course):
        '''Gets Meals for a Course object/instance - example of Aggregation'''
        meals=[]
        if course:
            sql = f"SELECT mealId, mealName, mealPrice, courseId FROM meals WHERE courseId={course.getCourseId()}"
            # print(f"Get all meals: {sql}")
        else:
            sql = f"SELECT mealId, mealName, mealPrice, courseId FROM meals"

            mealsData = SPXCafe().dbGetData(sql)

            for mealData in mealsData:
                # create a new instance
                meal = cls.__new__(cls)
                meal.setMealId(mealData['mealId'])
                meal.setMealName(mealData['mealName'])
                meal.setMealPrice(mealData['mealPrice'])
                meal.setCourseId(mealData['courseId'])
                meal.setCourse(course)
                # add meal object to meals list
                meals.append(meal)

        return meals
    
    @classmethod
    def findMeal(cls, mealName):
        '''Find a meal by name'''
        sql = f"SELECT mealId, mealName, mealPrice, courseId FROM meals WHERE mealName LIKE '%{mealName}%'"
        mealsData = SPXCafe().dbGetData(sql)
        meals = []
        for mealData in mealsData:
            meal = cls.__new__(cls)
            meal.setMealId(mealData['mealId'])
            meal.setMealName(mealData['mealName'])
            meal.setMealPrice(mealData['mealPrice'])
            meal.setCourseId(mealData['courseId'])
            meal.setCourse()  # Set the __course attribute
            meals.append(meal)
        return meals

def main():

    meal = Meal(mealId=1)                       # retrieve an existing Meal
    meal.display()                              # show existing values
    # meal.setMealPrice(meal.getMealPrice()+6)    # update Meal data demo
    # meal.save()                                 # save changes back to database
    # meal = Meal(mealId=1)                       # get same meal again from DB
    # meal.display()                              # show amended meal

    # print("Creating NEW meal not in database....")
    # Create a NEW Meal completetly
    # meal = Meal(mealName="Salata2",mealPrice=3.45,courseId=1)
    # # meal.save()
    # meal.display()

    print("Finding meal by name...")
    mealName = "calamari"
    meals = Meal.findMeal(mealName)
    if meals:
        for meal in meals:
            meal.display()
    else:
        print(f"No meal found with name '{mealName}'")

if __name__=="__main__":
    main()