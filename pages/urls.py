from django.urls import path
from . import views
app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/<int:pk_id>/', views.edit_book, name='edit_book'),
    path('delete/<int:pk_id>/', views.delete_book, name='delete_book'),
    path('export/', views.export_books_csv, name='export_books'),
    path('import/', views.import_books_csv, name='import_books'),
]