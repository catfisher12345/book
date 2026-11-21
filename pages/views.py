from django.shortcuts import render, redirect
from books.models import Book
from books.forms import BookForm

def index(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pages:index')
    else:
        form = BookForm()

    books = Book.objects.prefetch_related('authors', 'genres').order_by('-pk_id')
    return render(request, 'pages/index.html', {
        'form': form,
        'books': books,
    })
