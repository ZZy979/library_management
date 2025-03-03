from django.urls import path
from . import views

app_name = 'library'
urlpatterns = [
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('books/', views.SearchBookView.as_view(), name='book-list'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/add/', views.BookCreateView.as_view(), name='add-book'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='edit-book'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='delete-book'),
    path('borrow/<int:book_id>/', views.borrow_book, name='borrow-book'),
    path('return/<int:record_id>/', views.return_book, name='return-book'),
    path('borrow-records/', views.borrow_records, name='borrow-records'),
]
