from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hobbies = models.TextField(null=True, blank = True)
    age = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'profiles_table' 

    def __str__(self):
        return self.user.username
    
class Topic(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200) 
    description = models.TextField(null=True, # it allows NUULs to be in this field in database
                                   blank = True # it means that saving an empty form is allowed
                                   )

    class Meta:
        db_table = 'topics_table' 

    def __str__(self): 
        return self.name
 