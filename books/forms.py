from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'authors', 'genres', 'isbn', 'publication_year']
        widgets = {
            'authors': forms.CheckboxSelectMultiple(),
            'genres': forms.CheckboxSelectMultiple(),
        }
