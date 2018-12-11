from django.db import models


# Create your models here.

class Photos(models.Model):
    # id = models.IntegerField(primary_key=True)
    photo = models.ImageField(null=True)

    # def __str__(self):

    def __str__(self):
        return "{}".format( self.photo)