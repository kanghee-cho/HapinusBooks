from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("<int:book_id>/", views.book_detail, name="book_detail"),
]
