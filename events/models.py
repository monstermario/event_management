from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    attendees = models.ManyToManyField(User, related_name='attending_events')
    created_by = models.ForeignKey(User, related_name='created_events', on_delete=models.CASCADE)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    publised_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
