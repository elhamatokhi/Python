"""
Exercise 2 - Week 9: Library Systems
"""

class Book:
    """Represents a single book."""

    def __init__(self, title: str, author: str, isbn: str):
        # Initialize book details
        self.title = title
        self.author = author
        self.isbn = isbn

    def display_info(self) -> str:
        # return formatted book information
        return f"Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}"
    
class Library:
    """Represents a library that manages a collection of books."""

    def __init__(self):
        # Store books as a list of Book objects
        self.books = []
    
    def add_book(self, book: Book):
        # Add a new book to the library
        self.books.append(book)
        print(f'Book "{book.title}" added to the library.')

    def remove_book(self, isbn: str):
        # Remove a book by ISBN
        for book in self.books:
            if book.isbn == isbn:
                self.books.remove(book)
                print(f'Book "{book.title}" removed from the library.')
                return
        print("Book not found. No removal performed.")

    def list_books(self):
        # Display all books in the library
        if not self.books:
            print("The library is currently empty.")
            return
        print("\nLibrary Book List:")
        for book in self.books:
            print(book.display_info())

    def search_by_title(self, title: str):
        # Seearch for books by title (case-insensitive)
        print(f'\nSearch results for "{title}":')
        found = False
        for book in self.books:
            if title.lower() in book.title.lower():
                print(book.display_info())
                found = True

            if not found:
                print("No matching books found.")

# --------------------------------------------------
# Testing the Library System
# --------------------------------------------------

# Create a library instance
library = Library()

# Add books to the libarary
book1 = Book("Atommic Habits", "James Clear", "ISBN001")
book2 = Book("The art of Social Engineering","Hadnagy", "ISBN002")
book3 = Book("The Alchemist", "Paulo Coelho","ISBN003")

library.add_book(book1)
library.add_book(book2)
library.add_book(book3)

# List all books
library.list_books()

# Search for a book by title
library.search_by_title("The Alchemist")
library.search_by_title("ATOMIC HABITS")

# Remove a book and verify removal
library.remove_book('ISBN001')

# List books again to confirm removal
library.list_books()