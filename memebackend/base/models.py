from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobbies = models.TextField(null=True, blank = True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
 