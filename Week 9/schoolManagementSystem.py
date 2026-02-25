"""
Exercise 1: School Mangement System 
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
    


        