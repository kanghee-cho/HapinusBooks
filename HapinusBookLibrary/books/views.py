from django.shortcuts import render


# Create your views here.
def book_detail(request, book_id):
    book = {
        "id": book_id,
        "title": f"Book Title {book_id}",
        "author": "Author Name",
        "description": "This is a sample book description.",
    }
    return render(request, "books/book_detail.html", {"book": book})
