"""
Exercise 1 - Week 9: : School Mangement System 
"""

class Person:
    """
    Base class representing a generic person in school system.
    """

    def __init__(self,name: str, age:int):
        """
        Initialize common attributes for all persons.
        
        :param name: Full name of the person
        :param age: age of the person
        """
        self.name = name
        self.age = age
    
    def introduce(self) -> str:
        """
        Retrun a basic introduction for a person.
        This method is intended to be overridden by subclasses.

        :return: Introduction string
        """
        return f"My name is {self.name} and I am {self.age} years old."
    

class Student(Person):
    """
    Student class that inherits from Person.
    Represents a student in the school system.
    """

    def __init__(self, name: str, age: int, student_id: str):
        """
        Initialize student-specific attributes along with inherited attributes.

        :param name: Student's full name
        :param age: Student's age
        :param student_id: Unique student indetification number
        """
        # Call the parent class constructor
        super().__init__(name, age)
        self.student_id = student_id

    def introduce(self) -> str:
        """
        Override the introduce method to include student-specific information,

        :return: Customized student introduction
        """
        return (
            f"My name is {self.name}, I am {self.age} years old, and my student ID is {self.student_id}."
        )
    
class Teacher(Person):
    """
    Teacher class that inherits from Person.
    Represents a teacher in the school system.
    """

    def __init__(self, name: str, age: int, subject: str):
        """
        Initialize teacher-specific attributes along with inherited attributes.
        
        :param name: Teacher's full name
        :param age: Teacher's age
        :param subject: Subject taught by the teacher
        """

        # Call the parent class constructor
        super().__init__(name, age)
        self.subject = subject
    
    def introduce(self) -> str:
        """
        Override the introduce method to include teaching details.

        :return: Customized teacher introduction
        """
        return (
            f"My name is {self.name}, I am {self.age} years old, and I teach {self.subject}."
        )

# --------------------------------------------------
# Testing the Classes
# --------------------------------------------------

# Create a Student instance
student = Student(name="Edris", age=15, student_id="PL001")

# Create a Teacher instance
teacher = Teacher(name="Kai", age=35, subject="Python")

# Display introductions to verify inheritance and method overriding
print(student.introduce())
print(teacher.introduce())