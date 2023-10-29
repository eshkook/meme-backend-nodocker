# serializers.py
from rest_framework import serializers
from base.models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['hobbies', 'age']
