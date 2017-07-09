from django.db import models

# Create your models here.
class Location(models.Model):
    latitude = models.IntegerField()
    longitude = models.IntegerField()

class User(models.Model):
    name = models.CharField(max_length=30)
    token = models.CharField(max_length=100)
