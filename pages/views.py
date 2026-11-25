from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from books.models import Book
from books.forms import BookForm

def index(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('pages:index')
    else:
        form = BookForm()

    query = request.GET.get('q', '').strip()
    books = Book.objects.prefetch_related('authors', 'genres').order_by('-pk_id')

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(genres__name__icontains=query) |
            Q(isbn__icontains=query)
        ).distinct()

    return render(request, 'pages/index.html', {
        'form': form,
        'books': books,
        'query': query,
    })

def edit_book(request, pk_id):
    book = get_object_or_404(Book, pk_id=pk_id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            return redirect('pages:index')
    else:
        form = BookForm(instance=book)

    return render(request, 'pages/edit_book.html', {
        'form': form,
        'book': book,
    })

