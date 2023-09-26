from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    title = models.CharField(max_length=255, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='participating_events', blank=True)

    def __str__(self):
        return self.title
