from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.utils.text import slugify
import string
import random


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
              
class Commodity(models.Model):
    name = models.CharField(max_length=200, null=True)
    slug = models.SlugField(null=True)
    img = models.ImageField(upload_to='pics', blank=True)
    commodity_type =  models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=500, null=True)

    def __str__(self):
        return self.name

def slug_generator(sender, instance, *rgs, **kwargs):
    if not instance.slug:
        insnace.slug = unqiue_slug_generator(instance)

pre_save.connect(slug_generator, sender=Commodity)

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    """
    This is for a Django project and it assumes your instance 
    has a model with a slug field and a title character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=4)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
    
    



   





 

















    