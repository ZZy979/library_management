from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView

from .forms import UserRegisterForm
from .models import Book, BorrowRecord


def user_register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('library:login')
    else:
        form = UserRegisterForm()
    return render(request, 'library/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('library:search-book')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'library/login.html')


def user_logout(request):
    logout(request)
    return redirect('library:login')


class SearchBookView(ListView):
    paginate_by = 20

    def get_queryset(self):
        if query := self.request.GET.get('q'):
            return Book.objects.filter(title__icontains=query)
        else:
            return Book.objects.all()

    def get_context_data(self, **kwargs):
        query_params = self.request.GET.copy()
        if 'page' in query_params:
            del query_params['page']
        querystring = urlencode(query_params)
        return super().get_context_data(querystring=querystring, **kwargs)


class BookDetailView(DetailView):
    model = Book


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    if book.quantity > 0:
        BorrowRecord.objects.create(user=request.user, book=book)
        book.quantity -= 1
        book.save()
    return redirect('library:search-book')


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id, user=request.user)
    record.return_book()
    return redirect('library:borrow-records')


@login_required
def borrow_records(request):
    borrow_record_list = BorrowRecord.objects.filter(user=request.user).order_by('-borrow_date')
    return render(request, 'library/borrow_record_list.html', {'borrow_record_list': borrow_record_list})
