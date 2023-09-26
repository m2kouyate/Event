from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Event


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name')


class EventSerializer(serializers.ModelSerializer):
    creator = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


