from django.db import models
from django.contrib.auth.models import User

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    icon = models.ImageField(upload_to='photos/%Y/%m/%d/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=50)
    library_card_id = models.CharField(max_length=13, unique=True)

    def __str__(self):
        return self.user.username