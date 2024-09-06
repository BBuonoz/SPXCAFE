import Meal
from SPXCafe import SPXCafe

class Course(SPXCafe):
    '''Course Class - holds information about a Menu Course. '''

    def __init__(self, courseId=None, courseName=None,meals=None):
        '''Constructor Method for a Course'''

        super().__init__()

        self.setCourseId(courseId)
        self.setCourseName(courseName)
        self.setMeals(meals)

        # set the Meals Aggregations for this Course - e.g. list of meals for course

        if self.existsDB():
            if not self.setCourse():
                print(f"Course: Course Id <{self.getCourseId()}> is invalid ")

    def setCourse(self, courseId=None):
        '''retrieve course data from database '''
        retcode = False
        if courseId:
            self.setCourseId(courseId)

        if self.getCourseId():
            sql = f"SELECT courseId, courseName FROM courses WHERE courseId={self.getCourseId()}"
            courseData = self.dbGetData(sql)

            if courseData:  #course found in database
                for course in courseData:  # retrieve data
                    self.setCourseId(course['courseId'])
                    self.setCourseName(course['courseName'])
                    self.setMeals(Meal.Meal.getMeals(self))  # aggregation!
                    retcode = True

        return retcode

    # getters / setters for the class

    def setCourseId(self,courseId):
        self.__courseId = courseId

    def setCourseName(self,courseName):
        if courseName:
            self.__courseName = courseName.lower()
        else:
            self.__courseName = None

    def setMeals(self,meals=None): # default values means optional parameter
        if meals:
            self.__meals = meals
        else:
            self.__meals = []

    def addMeal(self,meal=None):
        print(type(meal))
        if meal:
            self.__meals.append(meal)
            meal.setCourse(self)

    def getCourseId(self):
        return self.__courseId

    def getCourseName(self):
        return self.__courseName

    def getMeals(self):
        return self.__meals

    def __str__(self):
        '''return a stringified version of object for printing'''
        return f"Course <{self.getCourseId()}> {self.getCourseName().title() if self.getCourseName() else "<Unknown>"}"

    def display(self):
        '''print the course details'''
        print(self)
        for meal in self.getMeals():
            meal.display()

    # Persistent Data - Database - Related Methods
    def existsDB(self):
        '''Check if object already exists in database'''
        retcode = False
        if self.getCourseId():
            sql = f"SELECT count(*) AS count FROM courses WHERE courseId={self.getCourseId()}"
            # print(sql)
            countData = self.dbGetData(sql)
            if countData:
                for countData in self.dbGetData(sql):
                    count = int(countData['count'])
                if count > 0:
                    retcode = True
        return retcode

    def save(self):
        '''Save course data back to the database'''

        if self.existsDB():
            sql = f'''UPDATE courses SET
                courseId={self.getCourseId()},
                courseName='{self.getCourseName()}'
                WHERE courseId={self.getCourseId()}
            '''
            self.dbChangeData(sql)
        else:
            sql = f'''
                INSERT INTO courses
                (courseName)
                VALUES
                ('{self.getCourseName()}')
            '''
            # Save new primary key
            self.setCourseId(self.dbPutData(sql))

    def delete(self):
        '''Deletes an Instance of a Course from the database only if there are no children MEALS
        '''
        if len(self.getMeals())==0:
            sql = f"DELETE FROM courses WHERE courseId={self.getCourseId()}"
            self.dbChangeData(sql)
        else:
            print(f"Cannot delete Course {self.getCourseId()}-{self.getCourseName().title()} - Meals attached")

    @classmethod
    def getCourses(cls,menu=None):
        '''Class Method : Gets All Courses object/instance for Menu - example of Aggregation'''

        sql = "SELECT courseId, courseName FROM courses ORDER BY courseId"
        # print(f"Get all courses: {sql}")

        coursesData = SPXCafe().dbGetData(sql)

        courses=[]
        for courseData in coursesData:
            # create a new instance
            course = cls.__new__(cls)  # create empty object of type cls
            course.setCourseId(courseData['courseId'])
            course.setCourseName(courseData['courseName'])
            course.setMeals(Meal.Meal.getMeals(course))
            # add course object to courses list
            courses.append(course)

        return courses

def main():
    '''Test Harness to make sure all methods work'''

    course = Course(1)
    course.display()
    # course.setCourseName(course.getCourseName()+"X")
    # course.save()
    # course = Course(1)
    # course.display()

    # course1 = Course(courseName="New Course")
    # course1.save()
    # course1.display()

    # print("New Meal")
    # meal = Meal.Meal(mealName="New Meal", mealPrice=99.99,course=course1)
    # # meal.save()
    # meal.display()

    # print("add meal to course")
    # course1.addMeal(meal)
    # course1.display()

    # print("Delete Course")
    # course1.delete()  ### DANGEROUS - What happens to children Meals????
    # course1.display()

if __name__=="__main__":
    main()