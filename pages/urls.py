from django.urls import path
from . import views
app_name = 'pages'

urlpatterns = [
    path('', views.index, name='index'),
    path('edit/<int:pk_id>/', views.edit_book, name='edit_book'),
]