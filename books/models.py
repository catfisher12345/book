from django.db import models

class Author(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class Genre(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    pk_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=200)
    authors = models.ManyToManyField(Author, related_name='books')
    genres = models.ManyToManyField(Genre, related_name='books')
    isbn = models.CharField(max_length=13, unique=True)
    publication_date = models.DateField()

    def __str__(self):
        return self.title
