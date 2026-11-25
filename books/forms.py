from django import forms
from .models import Book, Author, Genre

class InlineSelectDateWidget(forms.SelectDateWidget):
    template_name = "books/widgets/inline_select_date.html"

class BookForm(forms.ModelForm):
    # Add text fields for user input
    authors_input = forms.CharField(
        label="Authors",
        help_text="Enter author names separated by commas (e.g., J.K. Rowling, George Orwell)",
        widget=forms.TextInput(attrs={'placeholder': 'Author 1, Author 2'})
    )
    genres_input = forms.CharField(
        label="Genres",
        help_text="Enter genres separated by commas (e.g., Fantasy, Sci-Fi)",
        widget=forms.TextInput(attrs={'placeholder': 'Genre 1, Genre 2'})
    )
    # Define the exact display sequence here
    field_order = ['title', 'authors_input', 'genres_input', 'isbn', 'publication_date','book_cover']

    class Meta:
        model = Book
        # Exclude the actual ManyToMany fields from the form UI
        fields = ['title', 'isbn', 'publication_date', 'book_cover']
        widgets = {
            "publication_date": InlineSelectDateWidget(
                years=range(2026, 1899, -1),
                months={i: f"{i:02d}" for i in range(1, 13)},  # Shows 01, 02, 03...
                empty_label=("0000", "00", "00"),  # Year, Month, Day placeholders
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-populate the text fields if editing an existing book
        if self.instance and self.instance.pk:
            self.fields['authors_input'].initial = ', '.join(
                a.name for a in self.instance.authors.all()
            )
            self.fields['genres_input'].initial = ', '.join(
                g.name for g in self.instance.genres.all()
            )

    def save(self, commit=True):
        # Save the Book instance first so it gets a primary key
        book = super().save(commit=False)
        if commit:
            book.save()
            self._save_m2m_from_text(book)
        return book

    def _get_or_create_ci(self, model, raw_name):
        clean_name = " ".join(raw_name.split())  # Strips outer & double inner spaces
        obj = model.objects.filter(name__iexact=clean_name).first()
        if not obj:
            obj = model.objects.create(name=clean_name)
        return obj

    def _save_m2m_from_text(self, book):
        # 1. Process Authors
        author_names = [
            name for name in self.cleaned_data['authors_input'].split(',') if name.strip()
        ]
        author_objs = [self._get_or_create_ci(Author, name) for name in author_names]
        book.authors.set(author_objs)

        # 2. Process Genres
        genre_names = [
            name for name in self.cleaned_data['genres_input'].split(',') if name.strip()
        ]
        genre_objs = [self._get_or_create_ci(Genre, name) for name in genre_names]
        book.genres.set(genre_objs)

        # 1. Process Authors
        author_names = [
            name.strip() for name in self.cleaned_data['authors_input'].split(',') if name.strip()
        ]
        author_objs = []
        for name in author_names:
            # Prevents duplicate authors (case-insensitive check)
            author, _ = Author.objects.get_or_create(
                name__iexact=name, 
                defaults={'name': name}
            )
            author_objs.append(author)
        book.authors.set(author_objs)

        # 2. Process Genres
        genre_names = [
            name.strip() for name in self.cleaned_data['genres_input'].split(',') if name.strip()
        ]
        genre_objs = []
        for name in genre_names:
            genre, _ = Genre.objects.get_or_create(
                name__iexact=name, 
                defaults={'name': name}
            )
            genre_objs.append(genre)
        book.genres.set(genre_objs)
