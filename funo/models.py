from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Support(models.Model):
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null=True)
    phone = models.CharField(max_length=200, null=True)
    message = models.CharField(max_length=200, null=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    company = models.CharField(max_length=100, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    postalcode = models.CharField(max_length=30, null=True)
    bio = models.TextField(max_length=500, null=True)
    def __str__(self):
        return f'{self.user.username}'

    