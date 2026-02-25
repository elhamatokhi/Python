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
            if self.book.isbn == isbn:
                self.books.remove(book)
                print(f'Book "{book.title}" remove from the library.')
                return
            print("Book not found. No removal peroformed.")

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
                print(book.dispalay_info())
                found = True

            if not found:
                print("No matching books found.")
