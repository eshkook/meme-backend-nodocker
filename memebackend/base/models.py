from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobbies = models.TextField(null=True, blank = True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Topic(models.Model):
    name = models.CharField(max_length=200) 
    description = models.TextField(null=True, # it allows NUULs to be in this field in database
                                   blank = True # it means that saving an empty form is allowed
                                   )

    def __str__(self): 
        return self.name