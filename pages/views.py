import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db.models import Q
from books.models import Book, Author, Genre
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

@require_POST
def delete_book(request, pk_id):
    book = get_object_or_404(Book, pk_id=pk_id)
    # Optional: delete the uploaded cover image file from storage too
    if book.book_cover:
        book.book_cover.delete(save=False)
    book.delete()
    return redirect('pages:index')

def export_books_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="books_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['title', 'authors', 'genres', 'isbn', 'publication_date'])

    books = Book.objects.prefetch_related('authors', 'genres').order_by('pk_id')
    for book in books:
        authors = ', '.join(a.name for a in book.authors.all())
        genres = ', '.join(g.name for g in book.genres.all())
        writer.writerow([
            book.title,
            authors,
            genres,
            book.isbn,
            book.publication_date.strftime('%Y-%m-%d'),
        ])

    return response


@require_POST
def import_books_csv(request):
    csv_file = request.FILES.get('csv_file')
    if not csv_file:
        messages.error(request, "Please select a CSV file to upload.")
        return redirect('pages:index')

    if not csv_file.name.lower().endswith('.csv'):
        messages.error(request, "Invalid file type. Please upload a .csv file.")
        return redirect('pages:index')

    try:
        # utf-8-sig handles standard UTF-8 as well as Excel CSVs with BOM
        decoded_file = csv_file.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_file))
    except UnicodeDecodeError:
        messages.error(request, "Could not read file. Please save your CSV as UTF-8.")
        return redirect('pages:index')

    created_count = 0
    updated_count = 0
    skipped_count = 0

    for row in reader:
        # Normalize column headers to lowercase so 'Title' or 'title' both work
        clean_row = {k.strip().lower(): (v.strip() if v else '') for k, v in row.items() if k}

        title = clean_row.get('title', '')
        isbn = clean_row.get('isbn', '')
        pub_date_str = clean_row.get('publication_date', '')
        authors_str = clean_row.get('authors', '')
        genres_str = clean_row.get('genres', '')

        # Skip incomplete rows or invalid ISBN lengths (max_length=13)
        if not (title and isbn and pub_date_str) or len(isbn) > 13:
            skipped_count += 1
            continue

        try:
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d').date()
        except ValueError:
            skipped_count += 1
            continue

        book, created = Book.objects.update_or_create(
            isbn=isbn,
            defaults={
                'title': title,
                'publication_date': pub_date,
            }
        )

        # Link Authors (case-insensitive match)
        author_objs = []
        for raw_name in authors_str.split(','):
            clean_name = " ".join(raw_name.split())
            if clean_name:
                author = Author.objects.filter(name__iexact=clean_name).first()
                if not author:
                    author = Author.objects.create(name=clean_name)
                author_objs.append(author)
        book.authors.set(author_objs)

        # Link Genres (case-insensitive match)
        genre_objs = []
        for raw_name in genres_str.split(','):
            clean_name = " ".join(raw_name.split())
            if clean_name:
                genre = Genre.objects.filter(name__iexact=clean_name).first()
                if not genre:
                    genre = Genre.objects.create(name=clean_name)
                genre_objs.append(genre)
        book.genres.set(genre_objs)

        if created:
            created_count += 1
        else:
            updated_count += 1

    messages.success(
        request,
        f"Import complete: {created_count} added, {updated_count} updated, {skipped_count} skipped."
    )
    return redirect('pages:index')