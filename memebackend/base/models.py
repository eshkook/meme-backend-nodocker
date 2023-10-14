from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobbies = models.TextField(null=True, blank = True)
    age = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Topic(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200) 
    description = models.TextField(null=True, # it allows NUULs to be in this field in database
                                   blank = True # it means that saving an empty form is allowed
                                   )

    def __str__(self): 
        return self.name
    
class Post(models.Model):   
    user= models.ForeignKey(User, on_delete=models.CASCADE) # many to one relationship. each user can send multiple messages. 
                                                            # when the user is deleted, the cascade makes his posts delete.
    title = models.CharField(max_length=200) 
    body = models.TextField(null=True, # it allows NUULs to be in this field in database
                            blank = True # it means that saving an empty form is allowed
                            )
    updated = models.DateTimeField(auto_now=True) 
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated', '-created']

    def __str__(self): # will be accessed in html by '{{message}}'
        return self.body[:50] # we dont want a too long one so we truncate it    